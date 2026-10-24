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
   with patch('instance_backup.assert_empty_database'):
    with patch('instance_backup.subprocess.run',side_effect=fake):restore(root/'backup.tgz',root/'empty','postgres://dummy','RESTORE-QUORIVIO-DATA')
   self.assertEqual((root/'empty'/'s'/'f').read_bytes(),b'data')
 def test_reject_symlinks(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);a=root/'assets';a.mkdir();(a/'link').symlink_to('/etc/passwd')
   with patch('instance_backup.subprocess.run') as run:
    run.side_effect=lambda args,**kw:pathlib.Path(args[args.index('--file')+1]).write_bytes(b'dump')
    with self.assertRaises(ValueError):make_backup(root/'b.tgz',a,'postgres://dummy')
if __name__=='__main__':unittest.main()

class BackupHardeningTests(unittest.TestCase):
 def fixture(self, root):
  from instance_backup import make_backup
  assets=root/'assets';(assets/'s').mkdir(parents=True)
  (assets/'s'/'asset').write_bytes(b'private-content')
  def fake(args, **kw):
   if args[0]=='pg_dump':pathlib.Path(args[args.index('--file')+1]).write_bytes(b'postgres dump')
  with patch('instance_backup.subprocess.run',side_effect=fake):make_backup(root/'backup.tgz',assets,'postgres://dummy')
  return root/'backup.tgz'
 def rewrite(self, source, destination, modify):
  with tarfile.open(source,'r:gz') as z:
   entries=[(m.name,z.extractfile(m).read()) for m in z.getmembers()]
  entries=modify(entries)
  with tarfile.open(destination,'w:gz') as z:
   for name,data in entries:
    member=tarfile.TarInfo(name);member.size=len(data);z.addfile(member,io.BytesIO(data))
 def test_reject_traversal_and_absolute_asset_paths(self):
  import json
  from instance_backup import verify
  for badname in ('assets/../escape','assets//escape','assets/s/../../escape','/assets/s/file','assets/s\\escape'):
   with self.subTest(badname=badname),tempfile.TemporaryDirectory() as td:
    root=pathlib.Path(td);source=self.fixture(root)
    def tamper(entries):
     manifest=json.loads(entries[0][1]);manifest['files'][1]['path']=badname
     return [(entries[0][0],json.dumps(manifest).encode()),(entries[1][0],entries[1][1]),(badname,entries[2][1])]
    target=root/'bad.tgz';self.rewrite(source,target,tamper)
    with self.assertRaises(ValueError):verify(target)
 def test_reject_duplicate_archive_names(self):
  from instance_backup import verify
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);source=self.fixture(root);target=root/'bad.tgz'
   self.rewrite(source,target,lambda entries:entries+[entries[-1]])
   with self.assertRaises(ValueError):verify(target)
 def test_reject_manifest_size_type_and_hash(self):
  import json
  from instance_backup import verify
  for mutation in ({'bytes':True},{'bytes':-1},{'bytes':2**40},{'sha256':'x'*64}):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as td:
    root=pathlib.Path(td);source=self.fixture(root);target=root/'bad.tgz'
    def tamper(entries):
     m=json.loads(entries[0][1]);m['files'][1].update(mutation)
     return [('manifest.json',json.dumps(m).encode()),*entries[1:]]
    self.rewrite(source,target,tamper)
    with self.assertRaises(ValueError):verify(target)
 def test_reject_symlink_restore_destination(self):
  from instance_backup import restore
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);source=self.fixture(root);(root/'elsewhere').mkdir();(root/'target').symlink_to(root/'elsewhere')
   with patch('instance_backup.subprocess.run') as run:
    with self.assertRaises(ValueError):restore(source,root/'target','postgres://dummy','RESTORE-QUORIVIO-DATA')
    run.assert_not_called()
 def test_failed_database_restore_does_not_publish_assets(self):
  import subprocess
  from instance_backup import restore
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);source=self.fixture(root)
   with patch('instance_backup.subprocess.run',side_effect=subprocess.CalledProcessError(1,'pg_restore')):
    with self.assertRaises(subprocess.CalledProcessError):restore(source,root/'target','postgres://dummy','RESTORE-QUORIVIO-DATA')
   self.assertFalse((root/'target').exists())
 def test_backup_does_not_overwrite_existing_destination(self):
  from instance_backup import make_backup
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);self.fixture(root)
   old=(root/'backup.tgz').read_bytes()
   with self.assertRaises(FileExistsError):make_backup(root/'backup.tgz',root/'assets','postgres://dummy')
   self.assertEqual((root/'backup.tgz').read_bytes(),old)
 def test_backup_source_change_cannot_publish_archive(self):
  from instance_backup import make_backup
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);a=root/'assets';(a/'s').mkdir(parents=True);(a/'s'/'f').write_bytes(b'data')
   def fake(args,**kw):
    pathlib.Path(args[args.index('--file')+1]).write_bytes(b'dump')
    (a/'s'/'f').write_bytes(b'data changed')
   with patch('instance_backup.subprocess.run',side_effect=fake):
    # Mutation occurs before capture; the snapshot should remain valid.
    make_backup(root/'new.tgz',a,'postgres://dummy')
   self.assertEqual(len(__import__('instance_backup').verify(root/'new.tgz')['files']),2)


class RestorePreflightTests(unittest.TestCase):
 def fixture(self, root):
  assets=root/'assets';(assets/'s').mkdir(parents=True)
  (assets/'s'/'asset').write_bytes(b'private-content')
  def fake(args, **kw):
   if args[0]=='pg_dump':pathlib.Path(args[args.index('--file')+1]).write_bytes(b'postgres dump')
  with patch('instance_backup.subprocess.run',side_effect=fake):make_backup(root/'backup.tgz',assets,'postgres://dummy')
  return root/'backup.tgz'
 def test_preflight_rejects_nonempty_database(self):
  from instance_backup import assert_empty_database
  with patch('instance_backup.subprocess.run') as run:
   run.return_value.stdout='2\n'
   with self.assertRaisesRegex(ValueError,'fresh database'):assert_empty_database('postgres://dummy')
   self.assertEqual(run.call_args.args[0][0],'psql')
 def test_preflight_accepts_empty_database(self):
  from instance_backup import assert_empty_database
  with patch('instance_backup.subprocess.run') as run:
   run.return_value.stdout='0\n'
   assert_empty_database('postgres://dummy')
 def test_preflight_rejects_unreadable_result(self):
  from instance_backup import assert_empty_database
  with patch('instance_backup.subprocess.run') as run:
   run.return_value.stdout='garbled'
   with self.assertRaisesRegex(ValueError,'Could not verify'):assert_empty_database('postgres://dummy')
 def test_nonempty_database_is_not_modified(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);source=self.fixture(root)
   with patch('instance_backup.assert_empty_database',side_effect=ValueError('nonempty')):
    with patch('instance_backup.subprocess.run') as run:
     with self.assertRaises(ValueError):restore(source,root/'target','postgres://dummy','RESTORE-QUORIVIO-DATA')
     run.assert_not_called()
   self.assertFalse((root/'target').exists())
 def test_changed_archive_between_validation_and_extraction_is_rejected(self):
  import instance_backup
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);source=self.fixture(root)
   original=instance_backup.verify
   def mutate_after_verify(path):
    manifest=original(path)
    with tarfile.open(path,'r:gz') as z:
     entries=[(m.name,z.extractfile(m).read()) for m in z.getmembers()]
    with tarfile.open(path,'w:gz') as z:
     for name,data in entries:
      if name=='assets/s/asset':data=b'changed-content'
      m=tarfile.TarInfo(name);m.size=len(data);z.addfile(m,io.BytesIO(data))
    return manifest
   with patch('instance_backup.verify',side_effect=mutate_after_verify):
    with patch('instance_backup.assert_empty_database'):
     with patch('instance_backup.subprocess.run') as run:
      with self.assertRaisesRegex(ValueError,'changed during restore'):
       restore(source,root/'target','postgres://dummy','RESTORE-QUORIVIO-DATA')
      run.assert_not_called()
   self.assertFalse((root/'target').exists())
