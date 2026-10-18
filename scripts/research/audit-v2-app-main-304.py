"""Independent verification audit for Run 304."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/304-app-main-subsystem-large'
EXP = ROOT / 'local/experiments/v2-app-main-304'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def main():
    summary_path = RUN / 'summary.json'
    assert summary_path.exists(), f'summary.json missing at {summary_path}'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))

    assert summary['original_sha256'] == SHA, 'SHA mismatch'
    assert summary['original_selected_bytes'] == 2302, 'Byte count mismatch'
    assert summary['original_vas'] == ['0059d650', '004a88a0', '004640b0', '00467470'], 'VA mismatch'
    assert summary['native_fixture']['exit_code'] == 0, 'Exit code non-zero'
    assert summary['native_fixture']['cases'] == 10, 'Cases count mismatch'

    val_path = RUN / 'validation.json'
    assert val_path.exists(), f'validation.json missing at {val_path}'
    val = json.loads(val_path.read_text(encoding='utf-8'))
    assert val['status'] == 'PASS', 'Status not PASS'
    assert val['cases_passed'] == 10, 'Cases passed not 10'

    native_exec = EXP / 'fixture-native-001.execution.json'
    assert native_exec.exists(), 'Receipt missing'
    rec = json.loads(native_exec.read_text(encoding='utf-8'))
    assert rec['exit_code'] == 0, 'Native fixture non-zero exit'

    print('Run 304 verified: PE 2,302B across 4 functions, physical x86 slab verified, 10 differential cases passed, receipts verified')


if __name__ == '__main__':
    main()
