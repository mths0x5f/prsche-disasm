"""The cache must reduce reads without hiding changes during acceptance."""
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from v2_proof_cache import ProofCache
import v2_manual_index


class ProofCacheTests(unittest.TestCase):
    def test_one_read_and_digest_for_repeated_report_references(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'proof.json'
            path.write_bytes(b'{"passed": true}\r\n')
            cache = ProofCache()
            read_bytes = Path.read_bytes
            with patch.object(Path, 'read_bytes', autospec=True, side_effect=read_bytes) as read:
                for _ in range(100):
                    self.assertTrue(cache.document(path)['passed'])
                    self.assertEqual(cache.digest(path), hashlib.sha256(b'{"passed": true}\n').hexdigest())
                self.assertEqual(read.call_count, 1)
            cache.check_stable()
            self.assertEqual(cache.counts, dict(unique_files=1,unique_sha256=1,unique_json=1))

    def test_changed_cached_dependency_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'source.cpp'
            path.write_bytes(b'old')
            cache = ProofCache();cache.digest(path)
            path.write_bytes(b'new, different length')
            with self.assertRaisesRegex(RuntimeError, 'changed during audit'):
                cache.digest(path)
            with self.assertRaisesRegex(RuntimeError, 'changed during audit'):
                cache.check_stable()

    def test_change_during_read_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'source.cpp';path.write_bytes(b'old')
            read_bytes = Path.read_bytes
            def mutate(file):
                data = read_bytes(file);file.write_bytes(b'changed during read');return data
            with patch.object(Path, 'read_bytes', autospec=True, side_effect=mutate):
                with self.assertRaisesRegex(RuntimeError, 'changed during audit'):
                    ProofCache().digest(path)


class ManualIndexCacheTests(unittest.TestCase):
    def fixture(self, root):
        path=root/'local/game/Porsche.exe';path.parent.mkdir(parents=True)
        # CRLF must remain binary bytes, with each indexed body ending in RET.
        data=b'\r\n\xc3'*100;path.write_bytes(data)
        sha=hashlib.sha256(data).hexdigest()
        rows=[{'sha256':sha,'entry_va':f'{0x400000+i*3:08x}',
               'path':'Porsche.exe','file_offset':i*3,'body_bytes':3,
               'body_sha256':hashlib.sha256(b'\r\n\xc3').hexdigest(),
               'ranges':[[f'{0x400000+i*3:08x}',f'{0x400002+i*3:08x}']]}
              for i in range(100)]
        index=root/'index.jsonl';index.write_text('\n'.join(map(json.dumps,rows)))
        return path,index

    def test_hundred_functions_read_one_original_binary(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);path,index=self.fixture(root)
            read_bytes=Path.read_bytes
            with patch.object(v2_manual_index,'ROOT',root),patch.object(v2_manual_index,'INDEX',index),patch.object(Path,'read_bytes',autospec=True,side_effect=read_bytes) as read:
                self.assertEqual(len(v2_manual_index.records()),100)
                self.assertEqual(read.call_count,1)

    def test_binary_mutation_during_read_rejected(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);path,index=self.fixture(root)
            read_bytes=Path.read_bytes
            def mutate(file):
                data=read_bytes(file);file.write_bytes(data+b'changed');return data
            with patch.object(v2_manual_index,'ROOT',root),patch.object(v2_manual_index,'INDEX',index),patch.object(Path,'read_bytes',autospec=True,side_effect=mutate):
                with self.assertRaisesRegex(RuntimeError,'changed during audit'):
                    v2_manual_index.records()


class RefreshPlanTests(unittest.TestCase):
    def make_plan(self, directory, verifier, modes, flags=(), composite=False):
        root = Path(directory)
        scripts = root/'scripts/research';scripts.mkdir(parents=True)
        source = root/'source/fixture_probe.cpp';source.parent.mkdir();source.write_text('changed')
        names = [verifier]
        if composite:
            names += ['verify-v2-timer-setup.py','verify-v2-formatter-original.py','verify-v2-auxiliary-wait.py']
        pins = {'source/fixture_probe.cpp':'0'*64}
        for name in names:
            body = "p.add_argument('--report-dir')\np.add_argument('--probe', default='x/bin/Release/fixture_probe.exe')\n"
            body += ''.join(f'p.add_argument({flag!r})\n' for flag in flags)
            script = scripts/name;script.write_text(body)
            pins[script.relative_to(root).as_posix()] = hashlib.sha256(body.encode()).hexdigest()
        functions = []
        for index, mode in enumerate(modes):
            path = root/f'reports/{index}'/mode.pop('filename','verification.json')
            path.parent.mkdir(parents=True);path.write_text(json.dumps({'source_sha256':pins,**mode}))
            functions.append({'verification_report':path.relative_to(root).as_posix()})
        registry = root/'functions.json';registry.write_text(json.dumps({'functions':functions}))
        actual = Path(__file__).with_name('refresh-v2-proofs.py')
        spec = importlib.util.spec_from_file_location('refresh_plan_test',actual)
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.ROOT=root;module.REGISTRY=registry;module.BIN=root/'bin';module.PROOF_CACHE=ProofCache()
        with patch.object(sys,'argv',['refresh-v2-proofs.py','--report-root',str(root/'out'),'--plan-only']),redirect_stdout(io.StringIO()):
            module.main()
        return json.loads((root/'out/refresh-plan.json').read_text())

    def test_isolated_and_connected_modes_have_separate_outputs(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-formatter-bootstrap.py',
                [{},{'connected_original_strings':True}],flags=['--connected-strings'])
            self.assertEqual(plan['unsupported'],[])
            self.assertEqual(len(plan['tasks']),2)
            self.assertEqual(len({task['output'] for task in plan['tasks']}),2)
            connected = next(t for t in plan['tasks'] if '--connected-strings' in t['command'])
            self.assertIn('formatter_error_integration_probe.exe',' '.join(connected['command']))

    def test_scoped_full_proof_keeps_its_filename(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-application-context-base.py',
                                  [{'filename':'full-verification.json'}])
            self.assertEqual(Path(plan['tasks'][0]['output']).name,'full-verification.json')

    def test_observer_free_proof_keeps_its_build_mode_and_filename(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-formatter-float-output.py',
                [{'private_stage_trace_enabled':True},
                 {'private_stage_trace_enabled':False,'filename':'production-verification.json'}],
                flags=['--no-stage-trace','--report-name'])
            self.assertEqual(plan['unsupported'],[])
            self.assertEqual(len(plan['tasks']),2)
            self.assertEqual(len({task['output'] for task in plan['tasks']}),2)
            production = next(t for t in plan['tasks'] if '--no-stage-trace' in t['command'])
            command = production['command']
            self.assertEqual(Path(command[command.index('--probe')+1]).name,'fixture_production_probe.exe')
            self.assertEqual(command[command.index('--report-name')+1],'production-verification.json')
            self.assertEqual(Path(production['output']).name,'production-verification.json')

    def test_observer_free_proof_rejects_verifier_without_mode_flag(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-formatter-float-output.py',
                                  [{'private_stage_trace_enabled':False}])
            self.assertEqual(plan['tasks'],[])
            self.assertTrue(plan['unsupported'][0]['missing_trace_off_flag'])

    def test_uninstrumented_production_probe_is_preserved(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-formatter-strings.py',
                [{'uninstrumented_native_equal_instrumented':True}],flags=['--production-probe'])
            self.assertIn('--production-probe',plan['tasks'][0]['command'])

    def test_composite_uses_all_four_probes(self):
        with TemporaryDirectory() as directory:
            plan = self.make_plan(directory,'verify-v2-formatter-timer-integration.py',[{}],
                flags=['--timer-probe','--formatter-probe','--auxiliary-probe'],composite=True)
            self.assertEqual(plan['unsupported'],[])
            self.assertEqual(len(plan['tasks']),1)
            for flag in ['--probe','--timer-probe','--formatter-probe','--auxiliary-probe']:
                self.assertIn(flag,plan['tasks'][0]['command'])


if __name__ == '__main__':
    unittest.main()
