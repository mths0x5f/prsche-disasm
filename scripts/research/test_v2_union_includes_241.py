"""No native tools: guard canonical include lookup and observed compiler receipts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('union241', ROOT/'scripts/research/audit-v2-native-union-241.py')
union = importlib.util.module_from_spec(spec)
spec.loader.exec_module(union)


class IncludeGuards(unittest.TestCase):
    def test_search_and_receipt_guards(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/reports', prefix='include241-') as temporary:
            directory = Path(temporary)
            assert directory.resolve().is_relative_to((ROOT/'local/reports').resolve())
            source = directory/'source'; source.mkdir()
            first = directory/'first'; first.mkdir()
            second = directory/'second'; second.mkdir()
            for parent, value in [(source, 'local'), (first, 'first'), (second, 'second')]:
                (parent/'header.h').write_text(value)
            current = source/'unit.cpp'
            self.assertEqual(union.quoted_include(current, 'header.h', [first, second]), source/'header.h')
            self.assertEqual(union.quoted_include(directory/'other.cpp', 'header.h', [second, first]), second/'header.h')
            self.assertEqual(union.quoted_include(current, str(first/'header.h'), []), first/'header.h')
            with self.assertRaises(AssertionError): union.quoted_include(current, 'absent.h', [first])
            command = ['cl.exe', '/I'+str(first), '/I', str(second), '/c', str(current)]
            receipt = directory/'compile.execution.json'
            receipt.write_text(json.dumps(dict(command=command, exit_code=0)))
            pins = {receipt: union.digest(receipt)}
            row = dict(include_directories=[str(first),str(second)], compiler_command=command,
                       compiler_execution_receipt=str(receipt))
            self.assertEqual(union.recorded_include_roots(row, pins), [first,second])
            for changed in [dict(row, include_directories=[str(second),str(first)]),
                            dict(row, compiler_command=command+['/W4'])]:
                with self.assertRaises(AssertionError): union.recorded_include_roots(changed, pins)
            with self.assertRaises(AssertionError): union.recorded_include_roots(row, {})
            receipt.write_text(json.dumps(dict(command=command, exit_code=1)))
            pins[receipt] = union.digest(receipt)
            with self.assertRaises(AssertionError): union.recorded_include_roots(row, pins)
            self.assertEqual(union.recorded_include_roots({}, {}), [])


if __name__ == '__main__': unittest.main()
