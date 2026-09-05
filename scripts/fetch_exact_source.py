#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, urllib.request, zipfile
from pathlib import Path
URL="https://codeload.github.com/foxBMS/foxbms-2/zip/308028fb13d046ba29b98886895c2e17937b1437"
EXPECTED="2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2"
NAME="foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip"

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

p=argparse.ArgumentParser(); p.add_argument('--output-dir',type=Path,default=Path('.cache/upstream')); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
out=a.output_dir/NAME
if not out.exists() or sha(out)!=EXPECTED:
 urllib.request.urlretrieve(URL,out)
actual=sha(out)
if actual!=EXPECTED: raise SystemExit(f'SHA-256 mismatch: {actual} != {EXPECTED}')
extract=a.output_dir/'source'
if extract.exists():
 import shutil; shutil.rmtree(extract)
extract.mkdir()
with zipfile.ZipFile(out) as z: z.extractall(extract)
roots=[x for x in extract.iterdir() if x.is_dir()]
if len(roots)!=1: raise SystemExit('unexpected source archive layout')
print(out.resolve())
print(roots[0].resolve())
