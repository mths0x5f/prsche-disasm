"""Recheck303 original binding/state closure, without compiling or rerunning."""
import hashlib,json
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/303-heap-shutdown-bridge'
def main():
 summary=json.loads((RUN/'summary.json').read_bytes());reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 validation=json.loads((RUN/'validation.json').read_bytes());assert validation['summary_sha256']==hashlib.sha256((RUN/'summary.json').read_bytes()).hexdigest()
 evidence=json.loads((RUN/'evidence.json').read_bytes());assert len(bytes.fromhex(evidence['wrapper_hex']))==5 and len(bytes.fromhex(evidence['body_hex']))==159
 assert evidence['physical_pointer_initializers']['005e4fec']=='74f36a00'
 cases=evidence['cutpoint_cases'];assert len(cases)==8 and all(x['esp_delta']==4 and x['nonvolatiles_preserved'] for x in cases)
 disabled=next(x for x in cases if x['name']=='disabled');assert disabled['events']==[] and disabled['before_slots_hex']==disabled['after_slots_hex']
 alias=next(x for x in cases if x['name']=='index16_aliases_guard');assert bytes.fromhex(alias['after_slots_hex'])[64:68]==b'\0'*4
 mutation=next(x for x in cases if x['name']=='free_changes_object_id');assert bytes.fromhex(mutation['after_slots_hex'])[28:32]==b'\0'*4
 for case in cases:
  if case['name']!='disabled':assert case['final_context_pointer']=='005e3e18'
 assert summary['actual_274_provider_vas']==['0055ec30'] and not summary['implementation_added'] and not summary['storage_added']
 assert summary['compiler_commands']==summary['native_commands']==0;reader.cache.check_stable()
 result=dict(passed=True,original_bytes=164,original_cutpoint_cases=8,implementation='HOLD',reader_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
