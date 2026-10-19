"""Reuse the306/298 capture driver; preserve the shared389-input source base."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frozen_build306',ROOT/'scripts/research/build-v2-game-entry-306.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
driver=previous.driver
driver.RUN=ROOT/'iterations/v2/001-original-recovery/runs/309-disk-slot-game-integration'
driver.BUILD=ROOT/'local/builds/v2/disk-slot-game-integration-309'
driver.OUT=ROOT/'local/experiments/v2-disk-slot-game-integration-309'
source_hashes=driver.source_hashes
def pins(paths,compiled_sources=()):
    return source_hashes([*paths,Path(__file__),driver.RUN.parent/'306-file-pool-game-integration/CMakeLists.txt'],compiled_sources=compiled_sources)
driver.source_hashes=pins
if __name__=='__main__':driver.main()
