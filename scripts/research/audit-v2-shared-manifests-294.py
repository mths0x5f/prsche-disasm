"""Read-only comparison of legacy293 and shared-reference294 proof inputs."""
import hashlib,json
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/294-shared-input-manifests'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def size(d):return len((json.dumps(d,indent=2)+'\n').encode())
def main():
 s=load(RUN/'summary.json');v=load(RUN/'validation.json');assert sha(RUN/'summary.json')==v['summary_sha256']
 for name,h in s['input_sha256'].items():assert sha(ROOT/name)==h,name
 reader=ManifestReader(ROOT);receipts=[];inline_bytes=0;ref_bytes=0
 for attempt in ('001','002'):
  snapshot=load(RUN/('build-'+attempt+'.json'));legacy_path=ROOT/snapshot['legacy_report']['path']
  assert sha(legacy_path)==snapshot['legacy_report']['sha256'];legacy=load(legacy_path)
  mode,pins=reader.verify(snapshot,'source',expected_hash_mode='crlf-to-lf')
  assert len(pins)==380 and (mode,pins)==reader.resolve(legacy,'source','crlf-to-lf')
  assert snapshot['source_manifest']==s['shared_manifest']
  assert 'source_sha256' not in snapshot and 'source_delta' not in snapshot
  receipt=snapshot['execution_receipt'];assert sha(ROOT/receipt['path'])==receipt['sha256'];receipts.append(receipt)
  for key in ('exit_code','unresolved_names','unresolved_references'):assert snapshot[key]==legacy[key]
  inline_bytes+=size(dict(source_sha256=legacy['source_sha256']))
  ref_bytes+=size({k:val for k,val in snapshot.items() if k.startswith('source_')})
 assert receipts[0]!=receipts[1]
 shared_bytes=(ROOT/s['shared_manifest']['path']).stat().st_size+ref_bytes
 assert inline_bytes==s['inline_pin_payload_bytes']==118624
 assert shared_bytes==s['shared_pin_payload_bytes']==59847
 assert round(100*(inline_bytes-shared_bytes)/inline_bytes,2)==s['pin_payload_saving_percent']==49.55
 assert reader.counts['manifest_documents']==1 and reader.counts['unique_files']==381
 reader.cache.check_stable()
 result=dict(passed=True,audit_sha256=sha(__file__),summary_sha256=sha(RUN/'summary.json'),
             shared_source_pins=380,manifest_documents_loaded=1,captured_receipts_distinct=True,
             legacy_reports_unchanged=True,pin_payload_saving_percent=49.55,
             compiler_commands=0,native_commands=0,reader_counts=reader.counts)
 (RUN/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(passed=True,source_pins=380,one_manifest=True,pin_payload_saving_percent=49.55)))
if __name__=='__main__':main()
