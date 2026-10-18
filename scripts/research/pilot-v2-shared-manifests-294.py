"""Store293's identical source closure once; keep both actual build receipts distinct."""
import argparse,hashlib,json
from pathlib import Path
from v2_shared_manifests import ManifestReader, externalize

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/294-shared-input-manifests'
PREVIOUS=RUN.parent/'293-game-startup-followup'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--finalize-existing',action='store_true');args=parser.parse_args()
 RUN.mkdir(parents=True,exist_ok=True)
 previous_metadata=None
 if (RUN/'summary.json').exists():
  assert args.finalize_existing,'Completed pilot is immutable'
  # Before first publication, finalize helper/test pins without rewriting any
  # captured build or shared manifest. Retain the initial WIP metadata verbatim.
  history=ROOT/'local/experiments/v2-shared-input-manifests-294';history.mkdir(parents=True,exist_ok=True)
  for name in ('summary.json','validation.json'):
   old=RUN/name;backup=history/('pre-finalization-'+name);assert not backup.exists();backup.write_bytes(old.read_bytes())
  previous_metadata=dict(path=(history/'pre-finalization-summary.json').relative_to(ROOT).as_posix(),sha256=sha(history/'pre-finalization-summary.json'),reason='Finalize helper validation and test coverage; captured proof artifacts unchanged')
 documents=[];reference=None;legacy_bytes=0;references_bytes=0;inputs={}
 for attempt in ('001','002'):
  legacy_path=PREVIOUS/('build-'+attempt+'.json');legacy=load(legacy_path)
  source=legacy['source_sha256'];legacy_bytes+=len(encoded(dict(source_sha256=source)))
  inputs[legacy_path.relative_to(ROOT).as_posix()]=sha(legacy_path)
  receipt=ROOT/legacy['receipt'];assert sha(receipt)==legacy['receipt_sha256']
  inputs[receipt.relative_to(ROOT).as_posix()]=sha(receipt)
  snapshot=dict(schema=2,kind='captured-game-build-manifest-pilot',attempt=attempt,
                legacy_report=dict(path=legacy_path.relative_to(ROOT).as_posix(),sha256=sha(legacy_path)),
                execution_receipt=dict(path=legacy['receipt'],sha256=legacy['receipt_sha256']),
                source_sha256=source,graph_source_count=legacy['source_count'],
                exit_code=legacy['exit_code'],unresolved_names=legacy['unresolved_names'],
                unresolved_references=legacy['unresolved_references'],game_executed=False)
  snapshot=externalize(ROOT,snapshot,'source','crlf-to-lf',reference)
  reference=snapshot['source_manifest']
  assert not snapshot.get('source_delta') and not snapshot.get('source_removed')
  p=RUN/('build-'+attempt+'.json')
  if p.exists():assert p.read_bytes()==encoded(snapshot),'Captured build document changed'
  else:p.write_bytes(encoded(snapshot))
  documents.append((legacy,snapshot,p))
  references_bytes+=len(encoded({k:v for k,v in snapshot.items() if k.startswith('source_')}))
 reader=ManifestReader(ROOT)
 for legacy,snapshot,p in documents:
  self_contained=reader.verify(legacy,'source','crlf-to-lf',expected_hash_mode='crlf-to-lf')
  assert reader.verify(snapshot,'source',expected_hash_mode='crlf-to-lf')==self_contained
  inputs[p.relative_to(ROOT).as_posix()]=sha(p)
 assert reader.counts['manifest_documents']==1 and reader.counts['unique_files']==381
 assert documents[0][1]['execution_receipt']!=documents[1][1]['execution_receipt']
 reader.cache.check_stable()
 manifest=ROOT/reference['path'];inputs[reference['path']]=sha(manifest)
 for p in (Path(__file__),ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/test_v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py'):
  inputs[p.relative_to(ROOT).as_posix()]=sha(p)
 new_bytes=manifest.stat().st_size+references_bytes
 summary=dict(schema=1,kind='shared-input-manifest-pilot',input_sha256=inputs,
              shared_manifest=reference,source_pins=380,captured_builds=2,
              legacy_and_reference_pin_sets_identical=True,execution_receipts_distinct=True,
              legacy_reports_modified=False,compiler_commands=0,native_commands=0,
              reader_counts=reader.counts,inline_pin_payload_bytes=legacy_bytes,
              shared_pin_payload_bytes=new_bytes,pin_payload_bytes_saved=legacy_bytes-new_bytes,
              pin_payload_saving_percent=round(100*(legacy_bytes-new_bytes)/legacy_bytes,2),
              metadata_finalization=previous_metadata,
              limits=['Only repeated input/source closures are shared here, not ownership or COFF schemas',
                      'Frozen legacy reports remain in Git; this pilot adds files rather than shrinking existing history'])
 (RUN/'summary.json').write_bytes(encoded(summary))
 (RUN/'validation.json').write_bytes(encoded(dict(passed=True,summary_sha256=sha(RUN/'summary.json'),input_pins=len(inputs),manifest_documents_loaded=1,resolved_source_pins=380,raw_and_normalized_modes_separate=True)))
 print(json.dumps({k:summary[k] for k in ('source_pins','captured_builds','inline_pin_payload_bytes','shared_pin_payload_bytes','pin_payload_saving_percent','reader_counts')}))
if __name__=='__main__':main()
