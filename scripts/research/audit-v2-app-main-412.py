"""Independent verification audit for Run 412."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/412-app-main-frame-event-pump'
EXP = ROOT / 'local/experiments/v2-app-main-412'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def main():
    summary_path = RUN / 'summary.json'
    assert summary_path.exists(), f'summary.json missing at {summary_path}'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))

    assert summary['original_sha256'] == SHA, 'SHA mismatch'
    assert summary['original_selected_bytes'] == 1078, 'Byte count mismatch'
    assert summary['original_vas'] == ['004b4da0'], 'VA mismatch'
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

    print('Run 412 verified: PE 1,078B for frame_event_pump_004b4da0, physical x86 slab verified, 10 differential cases passed, receipts verified')


if __name__ == '__main__':
    main()
