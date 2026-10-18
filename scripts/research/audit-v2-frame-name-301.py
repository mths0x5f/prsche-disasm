"""Check301 shared input closure and captured original-string counterexamples."""
import hashlib,json
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/301-frame-name-bound'
def main():
 summary=json.loads((RUN/'summary.json').read_bytes());reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 validation=json.loads((RUN/'validation.json').read_bytes());assert validation['summary_sha256']==hashlib.sha256((RUN/'summary.json').read_bytes()).hexdigest()
 evidence=json.loads((RUN/'evidence.json').read_bytes());assert evidence['registration']['label_hex']==b'TRACK_NAME\0'.hex()
 assert evidence['format_wrapper_cutpoint']['remaining_capacity']==0x7fffffff
 assert not summary['upper_bound_31_proved'] and not summary['storage_definition_added']
 for case in evidence['consumer_cases']:
  length=case['source_length'];source=bytes.fromhex(case['source_after_hex']);destination=bytes.fromhex(case['destination_after_hex'])
  assert source==b'Q'*length+b'\0'+b'\xa5'*(63-length)
  assert destination==b'Q'*length+b'\0'+b'\xa5'*(79-length)
  assert case['root_changed']==(length>=32)
 assert summary['compiler_commands']==summary['native_commands']==0
 reader.cache.check_stable()
 result=dict(passed=True,original_packet_cases=4,formatter_cutpoints=1,storage='HOLD',reader_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
