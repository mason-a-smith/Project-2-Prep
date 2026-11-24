"""Check final disclosure, consistency, manifest and evidence-status requirements."""
from pathlib import Path
import json
import re
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
opening='AI use: OpenAI Codex assisted with code, analysis, documentation and verification.\n\nThe analysis and decision are mine (Mason Smith); education, not investment advice.'
for name in ['README.md','docs/decision-memo.md','docs/video-preparation.md']:
    assert (R/name).read_text(encoding='utf-8').startswith(opening),name
video=(R/'docs/video-preparation.md').read_text(encoding='utf-8')
assert video.count('OPENING\n\n'+opening)==3
assert 'app is running live' in video
memo=(R/'docs/decision-memo.md').read_text(encoding='utf-8')
assert len(memo.split())<=750,'Memo is no longer concise'
for value in ['6.6643%','5.2807%','4.0510%','3.4762%','6.3143%','6.6856%','5.1134%','4.7951%']:
    assert value in memo,value
assert 'AI-assisted' in memo and '0% live capital' in memo
manifest=(R/'docs/submission-manifest.md').read_text(encoding='utf-8')
rows=re.findall(r'^\| (\d+) \|',manifest,flags=re.M)
assert rows==[str(i) for i in range(1,13)],rows
assert manifest.count('MISSING — no YouTube URL supplied')==3
assert manifest.count('MISSING — no transcript supplied')==3
validation=(R/'docs/validation-and-ai-use.md').read_text(encoding='utf-8')
for text in ['462e6e2','5.113379%','4.795116%','AI-assisted','full dataset was previously examined']:
    assert text in validation,text
audit=(R/'docs/final-audit.md').read_text(encoding='utf-8')
assert 'NOT SCORED' in audit and 'not assigned out of 300' in audit
assert 'AI-closed execution' in audit
# The opening declarations are draft text, never an automatic personal attestation.
assert 'confirmation pending' in (R/'README.md').read_text(encoding='utf-8')
for i in range(1,4):
    assert not (R/f'docs/transcript-video-{i}.txt').exists(),'Re-audit actual transcript if newly supplied'
record={'status':'PASS','verified_at_utc':datetime.now(timezone.utc).isoformat(),
        'checks':['Two written openings and three video openings','Concise memo and consistent saved values',
                  '12-row GitHub manifest with missing video/transcript status','Complete locked-record disclosure with execution qualification',
                  'Personal confirmation not fabricated','Unavailable rubric not assigned invented scores'],
        'rubric_grade':'NOT SCORED: exact anchors unavailable','scope':'Assistant-run artifact checks; not personal confirmation or independent human evidence'}
(R/'outputs/final-audit-checks.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
