"""Recheck296's shared inputs and captured bounded original-copy evidence."""
import hashlib,json
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/296-frame-root-state'
def main():
 summary=json.loads((RUN/'summary.json').read_bytes());reader=ManifestReader(ROOT)
 reader.verify(summary,expected_hash_mode='raw')
 validation=json.loads((RUN/'validation.json').read_bytes())
 assert validation['summary_sha256']==hashlib.sha256((RUN/'summary.json').read_bytes()).hexdigest()
 evidence=json.loads((RUN/'evidence.json').read_bytes())
 assert len(evidence['direct_consumers'])==summary['direct_HIGHLOW_count']==27
 assert not summary['storage_definition_added'] and not summary['storage_standalone_approved']
 assert not evidence['root_initial']['physical_file_bytes'] and evidence['root_initial']['hex']=='00000000'
 for case in evidence['copy_cutpoint_cases']:
  before=bytes.fromhex(case['before_hex']);after=bytes.fromhex(case['after_hex']);length=case['source_length']
  assert after[:length+1]==b'X'*length+b'\0' and after[length+1:]==before[length+1:]
  assert case['root_changed']==(length>=32)
 reader.cache.check_stable()
 print(json.dumps(dict(passed=True,root_references=27,copy_cutpoints=5,storage='HOLD',reader_counts=reader.counts)))
if __name__=='__main__':main()
