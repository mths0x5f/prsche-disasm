"""Shared manifests must save space without weakening immutable proof inputs."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from v2_shared_manifests import DIRECTORY, ManifestReader, externalize, write_manifest


def digest(data):
    return hashlib.sha256(data).hexdigest()


class SharedManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'a').write_bytes(b'a\n')
        (self.root/'b').write_bytes(b'b\r\n')

    def test_legacy_and_reference_are_equivalent_and_read_base_once(self):
        old = dict(input_sha256={'a':digest(b'a\n')})
        new = externalize(self.root, old)
        reader = ManifestReader(self.root)
        self.assertEqual(reader.verify(old), reader.verify(new))
        self.assertEqual(reader.verify(new), reader.verify(new))
        self.assertEqual(reader.counts['manifest_documents'], 1)
        self.assertEqual(reader.counts['unique_files'], 2)

    def test_store_is_deterministic_and_refuses_corrupt_existing_bytes(self):
        pins = {'b':digest(b'b\r\n'), 'a':digest(b'a\n')}
        one = write_manifest(self.root, pins, 'raw')
        two = write_manifest(self.root, dict(reversed(list(pins.items()))), 'raw')
        self.assertEqual(one,two)
        (self.root/one['path']).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):write_manifest(self.root,pins,'raw')

    def test_delta_removes_updates_and_adds_without_mutating_base(self):
        base = write_manifest(self.root, {'a':digest(b'a\n'),'c':'0'*64}, 'raw')
        doc = externalize(self.root,dict(input_sha256={'a':'1'*64,'b':digest(b'b\r\n')}),base_reference=base)
        reader = ManifestReader(self.root)
        self.assertEqual(reader.resolve(doc)[1], {'a':'1'*64,'b':digest(b'b\r\n')})
        self.assertEqual(reader.manifest(base)[1], {'a':digest(b'a\n'),'c':'0'*64})
        self.assertEqual(doc['input_removed'],['c'])

    def test_missing_and_changed_manifest_are_rejected(self):
        doc = externalize(self.root,dict(input_sha256={'a':digest(b'a\n')}))
        p=self.root/doc['input_manifest']['path'];data=p.read_bytes();p.unlink()
        with self.assertRaises(FileNotFoundError):ManifestReader(self.root).resolve(doc)
        p.write_bytes(data+b' ')
        with self.assertRaises(ValueError):ManifestReader(self.root).resolve(doc)

    def test_raw_and_normalized_are_distinct_and_enforced(self):
        old=dict(source_sha256={'b':digest(b'b\n')})
        new=externalize(self.root,old,'source','crlf-to-lf')
        reader=ManifestReader(self.root)
        self.assertEqual(reader.verify(old,'source','crlf-to-lf'),reader.verify(new,'source'))
        with self.assertRaises(ValueError):reader.verify(new,'source',expected_hash_mode='raw')
        bad=externalize(self.root,old,'source','raw')
        with self.assertRaises(ValueError):ManifestReader(self.root).verify(bad,'source')

    def test_paths_ambiguous_forms_and_contradictory_removals_are_rejected(self):
        for name in ('../a','/a','C:/a','a\\b','a/../b','./a'):
            with self.subTest(name=name),self.assertRaises(ValueError):write_manifest(self.root,{name:'0'*64},'raw')
        doc=externalize(self.root,dict(input_sha256={'a':digest(b'a\n')}))
        with self.assertRaises(ValueError):ManifestReader(self.root).resolve(dict(doc,input_sha256={}))
        with self.assertRaises(ValueError):ManifestReader(self.root).resolve(dict(doc,input_removed=['missing']))
        with self.assertRaises(ValueError):ManifestReader(self.root).resolve(dict(doc,input_removed=['a'],input_delta={'a':'0'*64}))
        with self.assertRaises(ValueError):ManifestReader(self.root).resolve(dict(input_delta={}))

    def test_changed_input_is_rejected_even_when_reader_reuses_cache(self):
        doc=externalize(self.root,dict(input_sha256={'a':digest(b'a\n')}))
        reader=ManifestReader(self.root);reader.verify(doc)
        (self.root/'a').write_bytes(b'changed length')
        with self.assertRaises(RuntimeError):reader.verify(doc)
        with self.assertRaises(ValueError):ManifestReader(self.root).verify(doc)

    def test_one_changed_source_uses_delta_and_verifies_current_files(self):
        old=dict(source_sha256={'a':digest(b'a\n'),'b':digest(b'b\n')})
        first=externalize(self.root,old,'source','crlf-to-lf')
        (self.root/'a').write_bytes(b'new\r\n')
        current=dict(source_sha256={'a':digest(b'new\n'),'b':digest(b'b\n')})
        second=externalize(self.root,current,'source','crlf-to-lf',first['source_manifest'])
        self.assertEqual(second['source_delta'],{'a':digest(b'new\n')})
        self.assertEqual(first['source_manifest'],second['source_manifest'])
        self.assertEqual(ManifestReader(self.root).verify(second,'source')[1],current['source_sha256'])

    def test_unknown_schema_mode_and_duplicate_json_keys_are_rejected(self):
        valid=dict(schema=1,kind='recovery-pin-manifest',hash_mode='raw',files={})
        payloads=[json.dumps(dict(valid,schema=2)).encode(),json.dumps(dict(valid,hash_mode='mystery')).encode(),json.dumps(dict(valid,hash_mode=[])).encode(),
                  b'{"schema":1,"schema":1,"kind":"recovery-pin-manifest","hash_mode":"raw","files":{}}']
        for data in payloads:
            name=DIRECTORY+'/'+digest(data)+'.json';p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            with self.assertRaises(ValueError):ManifestReader(self.root).manifest(dict(path=name,sha256=digest(data)))


if __name__ == '__main__':unittest.main()
