"""Real TLS SMTP simulator protocol tests; no network, DB or external credentials."""
import json
import os
from pathlib import Path
import shutil
import smtplib
import ssl
import subprocess
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[2]

class SMTPSCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('openssl'):
            raise unittest.SkipTest('openssl unavailable')
        cls.tmp=tempfile.TemporaryDirectory(prefix='q-ci-smtps-test-')
        cls.folder=Path(cls.tmp.name)
        cls.cert=cls.folder/'cert.pem';cls.key=cls.folder/'key.pem'
        p=subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-sha256','-days','1',
                          '-keyout',str(cls.key),'-out',str(cls.cert),'-subj','/CN=localhost',
                          '-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],capture_output=True,timeout=8)
        if p.returncode:
            raise RuntimeError('could not generate ephemeral test certificate')
        cls.mail=cls.folder/'mail.jsonl'
        import socket
        sock=socket.socket();sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1];sock.close()
        env={**os.environ,'QUORIVIO_CI_SMTP_TEST':'1','QUORIVIO_CI_SMTP_CERT':str(cls.cert),
             'QUORIVIO_CI_SMTP_KEY':str(cls.key),'QUORIVIO_CI_SMTP_PORT':str(cls.port),
             'QUORIVIO_CI_SMTP_CAPTURE':str(cls.mail)}
        cls.proc=subprocess.Popen(['python3',str(ROOT/'tools/ci_smtps_capture.py')],env=env,
                                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for i in range(35):
            if cls.mail.exists():
                try:
                    cls.connect().quit();break
                except (OSError,smtplib.SMTPException):pass
            time.sleep(.08)
        else:
            cls.proc.kill();raise RuntimeError('CI SMTPS fixture failed to start')

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:cls.proc.kill()
        cls.tmp.cleanup()

    @classmethod
    def connect(cls):
        ctx=ssl.create_default_context(cafile=str(cls.cert))
        return smtplib.SMTP_SSL(host='127.0.0.1',port=cls.port,context=ctx,timeout=4)

    def test_tls_certificate_validation(self):
        with self.connect() as s:
            self.assertEqual(s.noop()[0],250)
            self.assertEqual(s.ehlo()[0],250)
            self.assertIn('auth',s.esmtp_features)

    def test_reject_unauthenticated_senders(self):
        with self.connect() as s:
            s.ehlo()
            with self.assertRaises(smtplib.SMTPSenderRefused):
                s.sendmail('sender@example.invalid','ci-email-mfa@example.invalid','Subject: refusal\n\nhi')

    def test_reject_wrong_credentials(self):
        with self.connect() as s:
            s.ehlo()
            with self.assertRaises(smtplib.SMTPAuthenticationError):
                s.login('ci-smtp-user','wrong-password')

    def test_accept_private_mail_and_unstuff_data(self):
        old=len(self.mail.read_text().splitlines())
        with self.connect() as s:
            s.login('ci-smtp-user','ci-smtp-password-should-not-leave-runner')
            self.assertEqual(s.sendmail('sender@example.invalid','ci-email-mfa@example.invalid',
                             'Subject: test\r\n\r\nYour Quorivio verification code is 123456. It expires in 10 minutes.\r\n..literal\r\n'),{})
        rows=[json.loads(row) for row in self.mail.read_text().splitlines()]
        self.assertEqual(len(rows),old+1)
        self.assertIn('ci-email-mfa@example.invalid',rows[-1]['recipient'])
        self.assertIn('verification code is 123456',rows[-1]['message'])
        self.assertIn('.literal',rows[-1]['message'])
        self.assertEqual(self.mail.stat().st_mode&0o777,0o600)

if __name__=='__main__':unittest.main()
