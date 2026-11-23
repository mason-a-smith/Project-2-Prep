"""Archive probe output and validate every saved persona memo."""
import copy
import json
from pathlib import Path
import panel

root = Path(__file__).resolve().parent
report = {}
for ticker in ['COST', 'AAPL']:
    folder = root / 'results' / ticker
    result = panel.enrich(json.loads((folder / 'analysis.json').read_text(encoding='utf-8')))
    memos = {name: (folder / filename).read_text(encoding='utf-8') for name, filename in
             [('Buffett', 'memo.md'), ('Cathie Wood', 'cathie_memo.md'), ('Burry', 'burry_memo.md')]}
    flags = panel.memo_flags(memos, result)
    assert not any(flags.values()), flags
    report[ticker] = flags
    probe = panel.enrich(copy.deepcopy(result), .05)
    (folder / 'threshold_probe.md').write_text(panel.printed_table(probe), encoding='utf-8')
(root / 'memo_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
