"""Run the locked reserve test only after recording its GitHub commit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import audit_controls as c
import portfolio as p

ROOT = Path(__file__).resolve().parent

def main():
    receipt_path = ROOT / 'docs/locked-commit.json'
    if not receipt_path.exists():
        raise SystemExit('STOP: publish docs/locked-input.json to GitHub before this run; commit receipt missing.')
    receipt = json.loads(receipt_path.read_text())
    raw = (ROOT / 'docs/locked-input.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt['record_sha256'], 'STOP: locked input changed'
    record = json.loads(raw)
    for name, digest in record['input_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f'STOP: {name} changed'
    assets, corr = p.estimate_from_csv(ROOT / 'prices.csv')
    for a in assets:
        a['reserve_eligible'] = a['name'] == 'SGOV'
    fixed = c.evaluate([.65, 0, 0, .35], assets, corr, minimum=.70)
    optimized = c.search(assets, corr, minimum=.70)
    result = {'run_at_utc': datetime.now(timezone.utc).isoformat(), 'pre_run_commit': receipt,
              'fixed': fixed, 'optimized': optimized,
              'prediction_confirmed': not fixed['mandate_pass'] and optimized is None,
              'decision': 'STOP: 70% reserve minimum leaves no feasible grid allocation; do not relax rules.'}
    (ROOT / 'outputs/locked-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
