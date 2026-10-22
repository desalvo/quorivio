import io, pathlib, sys, tarfile, tempfile, unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from instance_backup import make_backup,verify,restore
class InstanceBackupTests(unittest.TestCase):
 def test_backup_integrity_and_integrity_detection(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);assets=root/'assets';(assets/'session').mkdir(parents=True);(assets/'session'/'file').write_bytes(b'example payload');target=root/'backup.tar.gz'
   def fake_run(args,**kw): pathlib.Path(args[args.index('--file')+1]).write_bytes(b'postgres binary dump')
   with patch('instance_backup.subprocess.run',side_effect=fake_run):make_backup(target,assets,'postgres://dummy')
   self.assertEqual(len(verify(target)['files']),2)
   with tarfile.open(target,'r:gz') as z:
    data={m.name:z.extractfile(m).read() for m in z.getmembers()}
   data['assets/session/file']=b'changed'
   bad=root/'tampered.tar.gz'
   with tarfile.open(bad,'w:gz') as z:
    for k,v in data.items():
     m=tarfile.TarInfo(k);m.size=len(v);z.addfile(m,io.BytesIO(v))
   with self.assertRaises(ValueError):verify(bad)
 def test_restore_requires_confirmation_and_empty_assets(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);a=root/'assets';(a/'s').mkdir(parents=True);(a/'s'/'f').write_bytes(b'data')
   def fake(args,**kw):
    if args[0]=='pg_dump':pathlib.Path(args[args.index('--file')+1]).write_bytes(b'dump')
   with patch('instance_backup.subprocess.run',side_effect=fake):make_backup(root/'backup.tgz',a,'postgres://dummy')
   with self.assertRaises(ValueError):restore(root/'backup.tgz',root/'restore','postgres://dummy','no')
   (root/'restore').mkdir();(root/'restore'/'old').write_text('old')
   with self.assertRaises(ValueError):restore(root/'backup.tgz',root/'restore','postgres://dummy','RESTORE-QUORIVIO-DATA')
   with patch('instance_backup.subprocess.run',side_effect=fake):restore(root/'backup.tgz',root/'empty','postgres://dummy','RESTORE-QUORIVIO-DATA')
   self.assertEqual((root/'empty'/'s'/'f').read_bytes(),b'data')
 def test_reject_symlinks(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);a=root/'assets';a.mkdir();(a/'link').symlink_to('/etc/passwd')
   with patch('instance_backup.subprocess.run') as run:
    run.side_effect=lambda args,**kw:pathlib.Path(args[args.index('--file')+1]).write_bytes(b'dump')
    with self.assertRaises(ValueError):make_backup(root/'b.tgz',a,'postgres://dummy')
if __name__=='__main__':unittest.main()
