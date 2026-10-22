#!/usr/bin/env python3
"""Offline, bounded PDF/PPTX to presentation pages converter. No database mutations."""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import zipfile

MAX_BYTES=100*1024*1024
MAX_PAGES=200

def inspect_source(source):
    path=pathlib.Path(source)
    if not path.is_file() or path.stat().st_size>MAX_BYTES or path.stat().st_size<8:
        raise ValueError('Invalid source file size')
    ext=path.suffix.lower()
    if ext not in ('.pdf','.pptx'):
        raise ValueError('Only PDF and PPTX are supported')
    with path.open('rb') as f: signature=f.read(8)
    if ext=='.pdf' and not signature.startswith(b'%PDF-'):
        raise ValueError('Invalid PDF signature')
    if ext=='.pptx':
        if not zipfile.is_zipfile(path):raise ValueError('Invalid PPTX archive')
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            if '[Content_Types].xml' not in names or 'ppt/presentation.xml' not in names:
                raise ValueError('Invalid Office presentation')
            if len(names)>30000 or sum(v.file_size for v in z.infolist())>500*1024*1024:
                raise ValueError('PPTX archive exceeds extraction limits')
    return ext

def run(args,timeout=90):
    p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
    if p.returncode:raise RuntimeError('Conversion failed: '+p.stderr.decode(errors='replace')[:800])

def convert(source,dest):
    ext=inspect_source(source)
    output=pathlib.Path(dest)
    if output.exists():raise FileExistsError('Output directory already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='quorivio-import-') as scratch:
        tmp=pathlib.Path(scratch)
        pdf=pathlib.Path(source)
        if ext=='.pptx':
            if not shutil.which('libreoffice'):raise RuntimeError('LibreOffice required for PPTX import')
            profile=(tmp/'lo-profile').as_uri()
            run(['libreoffice','-env:UserInstallation='+profile,'--headless','--convert-to','pdf','--outdir',str(tmp),str(pathlib.Path(source).resolve())],120)
            pdf=tmp/(pathlib.Path(source).stem+'.pdf')
            if not pdf.exists():raise RuntimeError('PPTX conversion produced no PDF')
        if not shutil.which('pdfinfo') or not shutil.which('pdftoppm'):
            raise RuntimeError('Poppler pdfinfo and pdftoppm required')
        info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,timeout=20,check=True).stdout
        page_line=next((s for s in info.splitlines() if s.startswith('Pages:')),None)
        if not page_line:raise RuntimeError('Page count unavailable')
        pages=int(page_line.split(':',1)[1].strip())
        if pages<1 or pages>MAX_PAGES:raise ValueError('Page count out of supported range')
        images=tmp/'pages';images.mkdir()
        run(['pdftoppm','-f','1','-l',str(pages),'-scale-to','1600','-png','-r','96',str(pdf),str(images/'page')],180)
        files=sorted(images.glob('page-*.png'))
        if len(files)!=pages:raise RuntimeError('Unexpected number of rendered pages')
        manifest={'format':'quorivio-presentation-pages','version':1,'source_type':ext[1:],'source_sha256':hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest(),'page_count':pages,'pages':[],'notes':'Flattened slide images; animations and embedded video are not preserved.'}
        for i,p in enumerate(files,1):
            name=f'page-{i:04d}.png'
            p.rename(images/name)
            data=(images/name).read_bytes()
            manifest['pages'].append({'position':i,'image':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        # Finish the manifest before publishing the directory; interrupted writes
        # must not expose an incomplete page set to the API reader.
        (images/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        images.rename(output)
        return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Convert PDF/PPTX into Quorivio slide images (offline staging)')
    parser.add_argument('source');parser.add_argument('output_dir')
    args=parser.parse_args()
    print(json.dumps(convert(args.source,args.output_dir),indent=2))
