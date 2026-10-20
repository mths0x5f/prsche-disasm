"""Fresh actual game build after original resource constructor/drive and canonical search intake."""
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen_build328', ROOT / 'scripts/research/build-v2-game-entry-328.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
driver = previous.driver
driver.RUN = ROOT / 'iterations/v2/001-original-recovery/runs/332-resource-chain-game-integration'
driver.BUILD = ROOT / 'local/builds/v2/resource-chain-game-integration-332'
driver.OUT = ROOT / 'local/experiments/v2-resource-chain-game-integration-332'
source_hashes = driver.source_hashes


def pins(paths, compiled_sources=()):
    return source_hashes([*paths, Path(__file__), driver.RUN.parent / '328-resource-device-game-integration/CMakeLists.txt'],
                         compiled_sources=compiled_sources)


driver.source_hashes = pins
if __name__ == '__main__':
    driver.main()
    if sys.argv[sys.argv.index('--phase') + 1] == 'build':
        attempt = sys.argv[sys.argv.index('--attempt') + 1]
        summary = json.loads((driver.RUN / ('build-' + attempt + '.json')).read_bytes())
        receipt = json.loads((ROOT / summary['receipt']).read_bytes())
        log = (ROOT / receipt['log']).read_text(encoding='utf8')
        assert re.search(r'(?m)^\s+[A-Za-z0-9_.-]+\.cpp\s*$', log), 'No compiler events; receipt preserved'
        assert not summary['compiler_errors'] and not summary['other_linker_errors'], 'See build report'
