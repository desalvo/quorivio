"""RC261: real separate-mount PDF image import and fail-closed converter OS fixes.

The Kubernetes converter mounts /conversions and /tmp as distinct emptyDir
volumes. A staging directory under /tmp cannot be renamed to /conversions
(EXDEV). This suite uses distinct filesystem devices when available and also
checks the stage path independent of any particular CI mount layout.
"""
import errno
import io
import json
import os
from email.message import Message
from pathlib import Path
import re
import stat
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import conversion_worker as worker
import import_presentation as converter


def _valid_small_png():
    def chunk(name,payload):
        return (struct.pack('>I',len(payload))+name+payload+
                struct.pack('>I',zlib.crc32(name+payload)))
    ihdr=struct.pack('>IIBBBBB',2,2,8,2,0,0,0)
    raw=(b'\x00'+b'\xff\xff\xff'*2)*2
    return converter.PNG_SIGNATURE+chunk(b'IHDR',ihdr)+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')


def _render_mock(args,timeout=90):
    if args[0]=='pdfinfo':
        return b'Pages: 1\n'
    if args[0]=='pdftoppm':
        image=Path(args[-1]).parent/'page-1.png'
        image.write_bytes(_valid_small_png())
        return b''
    raise AssertionError('Unexpected converter subprocess')


def _fake_tools(binary):
    # The synthetic test renderer replaces subprocess calls; an external
    # Poppler installation is therefore not a test prerequisite. The real
    # converter still fail-closes if the executable is missing in production.
    return '/mock/bin/'+binary if binary in ('pdfinfo','pdftoppm') else None


class ConverterMountBoundary(unittest.TestCase):
    def test_stage_and_atomic_publish_use_same_device_even_with_tmp_override(self):
        with tempfile.TemporaryDirectory(prefix='quorivio-rc261-') as td:
            parent=Path(td)
            source=parent/'source.pdf'
            source.write_bytes(b'%PDF-1.4\n% synthetic fixture\n')
            actual=converter.tempfile.TemporaryDirectory
            staged=[]
            def track(*args,**kwargs):
                self.assertEqual(Path(kwargs['dir']),parent)
                directory=actual(*args,**kwargs)
                self.assertEqual(os.stat(directory.name).st_dev,os.stat(parent).st_dev)
                staged.append(Path(directory.name))
                return directory
            with patch.object(converter.tempfile,'TemporaryDirectory',side_effect=track),\
                 patch.object(converter.shutil,'which',side_effect=_fake_tools),\
                 patch.object(converter,'run',side_effect=_render_mock):
                result=converter.convert(source,parent/'pages')
            self.assertEqual(result['page_count'],1)
            self.assertTrue((parent/'pages/page-0001.png').is_file())
            self.assertTrue((parent/'pages/manifest.json').is_file())
            self.assertEqual(len(staged),1)
            self.assertFalse(staged[0].exists(), 'staging should be removed after publication')

    @unittest.skipUnless(Path('/dev/shm').is_dir(),'separate mount not available')
    def test_real_cross_mount_layout_matches_kubernetes_and_does_not_exdev(self):
        if os.stat('/dev/shm').st_dev==os.stat(tempfile.gettempdir()).st_dev:
            self.skipTest('runtime does not expose different temp/conversion filesystems')
        with tempfile.TemporaryDirectory(prefix='qrc261-',dir='/dev/shm') as td:
            parent=Path(td)
            source=parent/'source.pdf'
            source.write_bytes(b'%PDF-1.4\n% synthetic fixture\n')
            with patch.object(converter.shutil,'which',side_effect=_fake_tools),\
                 patch.object(converter,'run',side_effect=_render_mock):
                result=converter.convert(source,parent/'pages')
            self.assertEqual(result['page_count'],1)
            self.assertTrue((parent/'pages/page-0001.png').is_file())
            self.assertTrue((parent/'pages/manifest.json').is_file())

    def test_worker_reports_safe_errno_not_document_paths(self):
        handler=worker.Handler.__new__(worker.Handler)
        handler.path='/convert'
        headers=Message()
        headers['Authorization']='Bearer '+'x'*64
        headers['Content-Type']='application/json'
        body=json.dumps({'job':'a'*32}).encode('ascii')
        headers['Content-Length']=str(len(body))
        handler.headers=headers
        handler.rfile=io.BytesIO(body)
        messages=[]
        handler.log_error=lambda fmt,*args: messages.append(fmt%args)
        handler.reply=lambda status,payload:(status,payload)
        with patch.object(worker,'TOKEN','x'*64),patch.object(worker,'execute_job',
                    side_effect=OSError(errno.EXDEV,'cross-device','/private/sensitive-document.pdf')):
            response=handler.do_POST()
        self.assertEqual(response,(422,{'error':'conversion_failed'}))
        self.assertTrue(any('errno=18' in item for item in messages))
        self.assertTrue(all('sensitive' not in item and '/private/' not in item for item in messages))

    def test_api_and_ui_report_sanitized_conversion_failure_instead_of_internal_error(self):
        api=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
        web=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
        self.assertIn("reply.status===422?'conversion_failed':'conversion_worker_failed'",api)
        self.assertIn("res.status(422).json({error:'conversion_failed'})",api)
        self.assertIn("message==='conversion_failed'",web)
        self.assertNotIn('exc.strerror', (ROOT/'tools/conversion_worker.py').read_text())


class ConverterZlibSecurity(unittest.TestCase):
    def test_fixed_zlib_is_installed_and_version_checked_before_poppler(self):
        docker=(ROOT/'Dockerfile.converter').read_text(encoding='utf8')
        upgrade='--only-upgrade zlib1g'
        floor="dpkg --compare-versions \"$zlib_version\" ge '1:1.3.dfsg+really1.3.1-1+deb13u1'"
        poppler='poppler-utils libreoffice-impress fonts-dejavu-core'
        self.assertIn(upgrade,docker)
        self.assertIn(floor,docker)
        self.assertTrue(docker.index(upgrade)<docker.index(floor)<docker.index(poppler))
        self.assertIn('--only-upgrade apt libapt-pkg7.0',docker)
        self.assertNotIn('|| true',docker)

    def test_cve_security_gate_cannot_be_silenced_or_downgraded(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        step=workflow.split('- name: Scan converter image',1)[1].split('\n      - name:',1)[0]
        self.assertIn('severity: CRITICAL,HIGH',step)
        self.assertRegex(step, r"exit-code: ['\"]?1['\"]?")
        self.assertIn('ignore-unfixed: true',step)

if __name__=='__main__':unittest.main()
