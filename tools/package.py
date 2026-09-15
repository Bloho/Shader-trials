#!/usr/bin/env python3
"""Build a deterministic shaderpack ZIP with shaders/ at its root."""
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / 'tools/validate.py')], check=True)
output = ROOT / 'dist/BlohoShaders-shadow-fix-v0.3.2.zip'
output.parent.mkdir(exist_ok=True)
files = sorted(p for p in (ROOT / 'shaders').rglob('*') if p.is_file())
files += [ROOT / 'README.md'] + sorted((ROOT / 'docs').glob('*.md'))
files += sorted((ROOT / 'docs').glob('*.tsv'))
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (2026, 9, 16, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, path.read_bytes())
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert 'shaders/world0/gbuffers_terrain.vsh' in archive.namelist()
    assert all(not n.startswith(('/', '../')) for n in archive.namelist())
print(f'Packaged {len(files)} files: {output}')
