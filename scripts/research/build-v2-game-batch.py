"""Config-driven fresh game build using the established receipt/manifest driver."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--phase', choices=('configure', 'build'), required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config_path.relative_to(ROOT)
    cfg = json.loads(config_path.read_bytes())
    spec = importlib.util.spec_from_file_location('game_batch_base', ROOT / 'scripts/research/build-v2-game-entry-335.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    driver = base.driver
    driver.RUN = (ROOT / cfg['run']).resolve()
    driver.BUILD = (ROOT / cfg['build']).resolve()
    driver.OUT = (ROOT / cfg['experiment']).resolve()
    driver.RUN.relative_to(ROOT / 'iterations/v2/001-original-recovery/runs')
    driver.BUILD.relative_to(ROOT / 'local/builds/v2')
    driver.OUT.relative_to(ROOT / 'local/experiments')
    source_hashes = driver.source_hashes

    def pins(paths, compiled_sources=()):
        # CMake supplies the complete generation dependencies, including nested
        # historical run CMakeLists. Avoid another hardcoded chain per batch.
        cmake = set()
        iteration = ROOT / 'iterations/v2/001-original-recovery'
        for stamp in driver.BUILD.glob('**/generate.stamp.depend'):
            for line in stamp.read_text(encoding='utf8').splitlines():
                if not line or line.startswith('#'):
                    continue
                path = Path(line).resolve()
                if path.is_file() and path.is_relative_to(iteration):
                    cmake.add(path)
        return source_hashes([*paths, Path(__file__), config_path,
                              driver.RUN.parent / '335-resource-open-game-integration/CMakeLists.txt',
                              *sorted(cmake)], compiled_sources=compiled_sources)

    driver.source_hashes = pins
    sys.argv = [sys.argv[0], '--phase', args.phase, '--attempt', args.attempt]
    driver.main()
    if args.phase == 'build':
        summary = json.loads((driver.RUN / f'build-{args.attempt}.json').read_bytes())
        receipt = json.loads((ROOT / summary['receipt']).read_bytes())
        log = (ROOT / receipt['log']).read_text(encoding='utf8')
        assert re.search(r'(?m)^\s+[A-Za-z0-9_.-]+\.cpp\s*$', log), 'No compiler events; receipt retained'
        assert not summary['compiler_errors'] and not summary['other_linker_errors'], 'See build report'


if __name__ == '__main__':
    main()
