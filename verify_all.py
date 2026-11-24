"""Run every current Project2 automated verification suite in isolated processes."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
R = Path(__file__).resolve().parent
suites = ['verify_validation.py','verify_reconciliation.py','verify_improvements.py','verify_final.py','verify_prework.py']
results=[]
for suite in suites:
    started = datetime.now(timezone.utc)
    run = subprocess.run([sys.executable,str(R/suite)],cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
    results.append({'suite':suite,'started_at_utc':started.isoformat(),
                    'completed_at_utc':datetime.now(timezone.utc).isoformat(),
                    'exit_code':run.returncode,'status':'PASS' if run.returncode==0 else 'FAIL',
                    'output':run.stdout,'stderr':run.stderr})
    print(f'{suite}: {results[-1]["status"]}',flush=True)
record={'status':'PASS' if all(x['exit_code']==0 for x in results) else 'FAIL',
        'scope':'Automated assistant-run implementation checks only; no human AI-off record or independent partner validation',
        'results':results}
(R/'outputs/all-tests.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
raise SystemExit(0 if record['status']=='PASS' else 1)
