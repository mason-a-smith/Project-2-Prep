"""Create an uploadable source archive without local environments or secrets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
archive = root.parent / 'Project2_Week12_Prep.zip'
files = [p for p in root.rglob('*') if p.is_file()
         and not {'.venv', '__pycache__', '.uv-cache', '.git'}.intersection(p.relative_to(root).parts)
         and p.suffix != '.pyc' and not p.name.startswith('.env')]
with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
    for file in files:
        output.write(file, 'Project2/' + file.relative_to(root).as_posix())
with ZipFile(archive) as output:
    assert output.testzip() is None
    assert 'Project2/README.md' in output.namelist()
    assert 'Project2/uv.lock' in output.namelist()
print(f'{archive.name}: {len(files)} files, {archive.stat().st_size:,} bytes; ZIP integrity passed.')
