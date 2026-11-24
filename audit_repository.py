"""Download an actual GitHub commit, create its locked environment and test it.

Explicit network audit, separate from the normal offline automated suites.
"""
import argparse
from datetime import datetime,timezone
import io
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--commit',required=True)
    args=parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.commit):
        raise ValueError('Expected an exact 40-character commit SHA.')
    started=datetime.now(timezone.utc).isoformat()
    url=f'https://codeload.github.com/mason-a-smith/Project-2-Prep/zip/{args.commit}'
    data=urllib.request.urlopen(url,timeout=60).read()
    archive=zipfile.ZipFile(io.BytesIO(data))
    target_parent=Path(tempfile.mkdtemp(prefix='project2-final-repository-'))
    if any(Path(n).is_absolute() or '..' in Path(n).parts for n in archive.namelist()):
        raise ValueError('Unsafe archive path.')
    archive.extractall(target_parent)
    target=next(p for p in target_parent.iterdir() if p.is_dir())
    assert not (target/'.venv').exists(),'Archive unexpectedly includes an environment'
    records=[]
    def execute(arguments):
        began=datetime.now(timezone.utc).isoformat()
        result=subprocess.run(arguments,cwd=target,capture_output=True,text=True,encoding='utf-8',errors='replace')
        records.append({'command':arguments,'started_at_utc':began,'exit_code':result.returncode,
                        'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:
            raise RuntimeError(result.stdout+'\n'+result.stderr)
        return result
    health=False
    process=None
    try:
        execute(['uv','run','--locked','python','run.py'])
        execute(['uv','run','--locked','python','verify_all.py'])
        interpreter=execute(['uv','run','--locked','python','-c','import sys; print(sys.executable)']).stdout.strip()
        with socket.socket() as s:
            s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
        command=[interpreter,'-m','streamlit','run','app.py','--server.headless','true',
                 '--server.address','127.0.0.1','--server.port',str(port)]
        with (target_parent/'server.log').open('w',encoding='utf-8') as log:
            process=subprocess.Popen(command,cwd=target,stdout=log,stderr=subprocess.STDOUT,
                                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            for _ in range(120):
                if process.poll() is not None: break
                try:
                    health=urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=1).read()==b'ok'
                    if health:break
                except OSError:pass
                time.sleep(.25)
            if not health:raise RuntimeError('Fresh-environment server health failed')
        full=json.loads((target/'outputs/all-tests.json').read_text(encoding='utf-8'))
        original=ROOT/'outputs/repository-reproduction.json'
        baseline=json.loads(original.read_text(encoding='utf-8')) if original.exists() else {}
        report={'status':'PASS','started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
                'source_commit':args.commit,'anonymous_download_url':url,'fresh_directory':str(target),
                'scope':'Assistant-run actual repository download, new virtual environment and shared machine/cache; not an independent partner or clean machine',
                'readme_runner_and_full_suite_commands':records,'actual_server_command':command,
                'server_health':health,'server_note':'Direct interpreter is the fresh environment selected by uv; server is terminated after the health check',
                'all_suite_status':full['status'],'suite_exit_codes':{x['suite']:x['exit_code'] for x in full['results']},
                'optional_sec_archives_reported':json.loads((target/'outputs/prep-verification.json').read_text(encoding='utf-8')).get('optional_unpublished_sec_archives_absent',[]),
                'earlier_baseline_record':baseline if 'baseline_commit' in baseline else {}}
        original.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':report['status'],'source_commit':args.commit,'server_health':health,
                          'suite_exit_codes':report['suite_exit_codes']},indent=2))
    finally:
        if process is not None and process.poll() is None:
            process.terminate();process.wait(timeout=15)

if __name__=='__main__':
    main()
