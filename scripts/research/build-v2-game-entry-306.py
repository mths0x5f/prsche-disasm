"""Reuse the frozen298 build driver and source manifest; add only the306 delta."""
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frozen_build298',ROOT/'scripts/research/build-v2-game-entry-298.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
driver.RUN=ROOT/'iterations/v2/001-original-recovery/runs/306-file-pool-game-integration'
driver.BUILD=ROOT/'local/builds/v2/file-pool-game-integration-306'
driver.OUT=ROOT/'local/experiments/v2-file-pool-game-integration-306'
source_hashes=driver.source_hashes
externalize=driver.externalize
base=json.loads((driver.RUN.parent/'298-frame-game-integration/build-002.json').read_bytes())['source_manifest']
def pins(paths,compiled_sources=()):
    return source_hashes([*paths,Path(__file__),driver.RUN.parent/'298-frame-game-integration/CMakeLists.txt'],compiled_sources=compiled_sources)
def share(root,document,scope='input',hash_mode='raw',base_reference=None):
    return externalize(root,document,scope,hash_mode,base_reference or (base if scope=='source' else None))
driver.source_hashes=pins
driver.externalize=share
if __name__=='__main__':driver.main()
