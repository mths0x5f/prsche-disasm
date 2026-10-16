"""Fail-closed lowering guards; native execution equivalence is separate Run258."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('backend257', Path(__file__).with_name('x86-cpp-backend-257.py'))
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class Guards(unittest.TestCase):
    def test_rejections(self):
        cases = {
            'empty':'', 'truncated':'e8', 'unknown':'ccc3',
            'open-fallthrough':'90', 'branch-interior':'7501b800000000c3',
            'jmp-interior':'eb01b800000000c3', 'call-interior':'e8fdffffffc3',
            'segment':'64a100000000c3', 'address16':'678b00c3',
            'stack16':'6650c3', 'ret16':'66c3', 'conditional16':'660f840000c3',
            'repeat':'f390c3', 'x87':'d9e8c3', 'farcall':'9a000000000000c3',
        }
        for label, raw in cases.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                backend.translate(bytes.fromhex(raw), 0x1000)
        for entry in (-1,0x100000000,'0x1000'):
            with self.assertRaises(ValueError): backend.translate(b'\xc3',entry)
        with self.assertRaises(ValueError): backend.translate(b'\x50\xc3',0xffffffff)

    def test_stack_order_and_return(self):
        cpp,witnesses = backend.translate(bytes.fromhex('545c8f0424ff1424c20800'),0x1000)
        codes = [r['cpp'] for r in witnesses]
        self.assertIn('U value=s.r[4];s.r[4]-=4u;', codes[0])
        self.assertIn('s.r[4]+=4u;s.r[4]=value;', codes[1])
        self.assertLess(codes[2].index('s.r[4]+=4u;'), codes[2].index('write257('))
        self.assertLess(codes[3].index('read257('), codes[3].index('call257('))
        self.assertIn('0x00001008u',codes[3])
        self.assertIn('s.r[4]+=12u;s.stop=Stop257::Returned;',codes[4])
        self.assertEqual(len(witnesses),cpp.count('if(!step257('))

    def test_subregister_views(self):
        cpp,w = backend.translate(bytes.fromhex('b401b1026601c86631db8b442404c3'),0x1000)
        self.assertIn('0xffff00ffu',w[0]['cpp'])  # AH preserves other bytes
        self.assertIn('<<8',w[0]['cpp'])
        self.assertIn('0xffffff00u',w[1]['cpp'])  # CL
        self.assertIn('add257(s,a,b,16u)',w[2]['cpp'])
        self.assertIn('0xffff0000u',w[2]['cpp'])
        self.assertIn('logical257(s,a^b,16u)',w[3]['cpp'])
        self.assertIn('s.r[4]*1u',cpp)

    def test_dispatch_and_labels(self):
        cpp,w = backend.translate(bytes.fromhex('85c07402ebfae900100000'),0x1000)
        self.assertIn('L_00001000:',cpp)
        self.assertIn('L_00001006:',cpp)
        self.assertIn('dispatch257(s,target);return;',w[-1]['cpp'])
        self.assertEqual([r['va'] for r in w],['00001000','00001002','00001004','00001006'])


if __name__ == '__main__':
    started = time.perf_counter()
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards))
    if '--report' in sys.argv:
        run = ROOT/'iterations/v2/001-original-recovery/runs/257-x86-call-backend'
        run.mkdir(parents=True,exist_ok=True)
        path = run/'summary.json'
        assert not path.exists(),'completed257 immutable; run guards without --report'
        summary = dict(status='PASS' if result.wasSuccessful() else 'FAIL',
                       guard_groups=result.testsRun,rejection_cases=19,
                       elapsed_seconds=time.perf_counter()-started,
                       native_execution=False,new_accepted_functions=0,
                       scope='Lowering safety, stack ordering, byte/word register views, static control flow.',
                       native_equivalence='Separate Run258; no full CPU or game claim.',
                       source_pins={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [Path(__file__),Path(backend.__file__)]})
        path.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8',newline='\n')
    sys.exit(0 if result.wasSuccessful() else 1)
