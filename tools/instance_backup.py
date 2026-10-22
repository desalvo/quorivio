#!/usr/bin/env python3
"""Offline instance snapshot and controlled restore. Python stdlib; requires pg_dump/pg_restore.

Stop application writers first. Only administrators with filesystem and database rights should run this.
"""
import argparse, hashlib, io, json, os, pathlib, subprocess, sys, tarfile, tempfile
from datetime import datetime, timezone

VERSION = 1

def digest(data): return hashlib.sha256(data).hexdigest()

def checked_asset_files(root):
    if not root.is_dir(): raise ValueError('Asset directory does not exist')
    for p in sorted(root.rglob('*')):
        if p.is_symlink(): raise ValueError(f'Symlink in asset directory: {p}')
        if p.is_file():
            rel=p.relative_to(root)
            if len(rel.parts)!=2 or not all(x and x not in ('.','..') for x in rel.parts):
                raise ValueError(f'Unexpected asset path: {rel}')
            yield p, 'assets/'+rel.as_posix()

def make_backup(destination, assets, database_url):
    if not database_url: raise ValueError('DATABASE_URL is required')
    destination=pathlib.Path(destination); assets=pathlib.Path(assets)
    if destination.exists(): raise FileExistsError('Refusing to overwrite an existing backup')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='quorivio-backup-') as tmp:
        dump=pathlib.Path(tmp)/'database.dump'
        env=os.environ.copy();env['PGCONNECT_TIMEOUT']='15'
        subprocess.run(['pg_dump','--format=custom','--no-owner','--no-acl','--file',str(dump),database_url],env=env,check=True,timeout=3600)
        objects=[(dump,'database.dump'),*checked_asset_files(assets)]
        records=[]
        for src,name in objects:
            content=src.read_bytes();records.append({'path':name,'sha256':digest(content),'bytes':len(content)})
        manifest={'format':'quorivio-instance-backup','version':VERSION,'created_at':datetime.now(timezone.utc).isoformat(),'files':records,'privacy':'contains personal data, credentials derived from database and uploaded content; encrypt and restrict backup storage'}
        with tarfile.open(destination,'x:gz') as archive:
            encoded=json.dumps(manifest,sort_keys=True,indent=2).encode('utf-8')
            info=tarfile.TarInfo('manifest.json');info.size=len(encoded);info.mode=0o600;archive.addfile(info,io.BytesIO(encoded))
            for src,name in objects:
                info=archive.gettarinfo(str(src),arcname=name);info.mode=0o600
                with src.open('rb') as stream:archive.addfile(info,stream)
    os.chmod(destination,0o600)
    return manifest

def verify(archive_path):
    with tarfile.open(archive_path,'r:gz') as archive:
        members=archive.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or not names or names[0]!='manifest.json':raise ValueError('Invalid archive member names')
        if any(not m.isfile() or m.issym() or m.islnk() for m in members):raise ValueError('Non-regular archive entry')
        if len(members)>100000:raise ValueError('Too many archive members')
        manifest_member=members[0]
        if manifest_member.size>1024*1024:raise ValueError('Manifest exceeds size limit')
        manifest=json.load(archive.extractfile(manifest_member))
        if manifest.get('format')!='quorivio-instance-backup' or manifest.get('version')!=VERSION:raise ValueError('Unsupported backup format')
        declared=manifest.get('files')
        if not isinstance(declared,list) or len(declared)+1!=len(members):raise ValueError('Archive/manifest length mismatch')
        for member,record in zip(members[1:],declared):
            name=record.get('path')
            if name!='database.dump' and (not isinstance(name,str) or not name.startswith('assets/') or len(pathlib.PurePosixPath(name).parts)!=3 or '..' in pathlib.PurePosixPath(name).parts):raise ValueError('Invalid backup asset path')
            if member.name!=name or member.size!=record.get('bytes'):raise ValueError('Manifest file mismatch')
            h=hashlib.sha256();file=archive.extractfile(member)
            for chunk in iter(lambda:file.read(1024*1024),b''):h.update(chunk)
            if h.hexdigest()!=record.get('sha256'):raise ValueError('Checksum mismatch: '+name)
        if not declared or declared[0]['path']!='database.dump':raise ValueError('Missing database dump')
        return manifest

def restore(archive_path, assets, database_url, confirmation):
    if confirmation!='RESTORE-QUORIVIO-DATA':raise ValueError('Explicit confirmation is required')
    if not database_url:raise ValueError('DATABASE_URL is required')
    manifest=verify(archive_path)
    root=pathlib.Path(assets)
    if root.exists() and any(root.iterdir()):raise ValueError('Restore requires an EMPTY asset directory')
    root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='quorivio-restore-') as tmp,tarfile.open(archive_path,'r:gz') as archive:
        dump=pathlib.Path(tmp)/'database.dump'
        with dump.open('wb') as f:
            source=archive.extractfile('database.dump')
            for chunk in iter(lambda:source.read(1024*1024),b''):f.write(chunk)
        # Restore into a freshly created empty database. --clean is deliberately forbidden.
        subprocess.run(['pg_restore','--exit-on-error','--no-owner','--no-acl','--dbname',database_url,str(dump)],check=True,timeout=3600)
        for record in manifest['files'][1:]:
            dest=root/pathlib.PurePosixPath(record['path']).relative_to('assets')
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as f:
                src=archive.extractfile(record['path'])
                for chunk in iter(lambda:src.read(1024*1024),b''):f.write(chunk)
            os.chmod(dest,0o600)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('backup');b.add_argument('--output',required=True);b.add_argument('--assets',required=True)
    v=s.add_parser('verify');v.add_argument('--input',required=True)
    r=s.add_parser('restore');r.add_argument('--input',required=True);r.add_argument('--assets',required=True);r.add_argument('--confirm',default='')
    args=p.parse_args()
    try:
        if args.action=='backup': m=make_backup(args.output,args.assets,os.environ.get('DATABASE_URL'))
        elif args.action=='verify':m=verify(args.input)
        else:m=restore(args.input,args.assets,os.environ.get('DATABASE_URL'),args.confirm)
        print(json.dumps({'ok':True,'files':len(m['files']),'created_at':m['created_at']},indent=2))
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,tarfile.TarError) as e:
        print('Backup operation failed: '+str(e),file=sys.stderr);sys.exit(1)
if __name__=='__main__':main()
