#!/usr/bin/env python3
"""Loopback-only, TLS-protected fake SMTPS sink for disposable CI MFA acceptance.

Never expose this sink publicly or run it against production; the messages contain
real OTPs for the disposable CI account. Stores mode-0600 JSONL for test assertions.
"""
from __future__ import annotations
import asyncio
import base64
import json
import os
import ssl
from pathlib import Path

HOST = '127.0.0.1'
PORT = int(os.getenv('QUORIVIO_CI_SMTP_PORT', '2465'))
OUT = Path(os.getenv('QUORIVIO_CI_SMTP_CAPTURE', '/tmp/quorivio-ci-mail.jsonl'))
USER = os.getenv('QUORIVIO_CI_SMTP_USER', 'ci-smtp-user')
PASS = os.getenv('QUORIVIO_CI_SMTP_PASSWORD', '')

async def connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    authenticated = False
    sender = recipient = None
    async def reply(line: str) -> None:
        writer.write((line + '\r\n').encode('ascii'))
        await writer.drain()
    try:
        await reply('220 localhost ESMTP disposable Quorivio CI')
        while line := await reader.readline():
            if len(line) > 4096:
                await reply('500 line too long'); break
            cmd = line.decode('utf-8', 'replace').strip()
            verb, _, arg = cmd.partition(' ')
            if verb.upper() in ('EHLO', 'HELO'):
                await reply('250-localhost'); await reply('250-AUTH PLAIN'); await reply('250 8BITMIME')
            elif verb.upper() == 'AUTH':
                try:
                    method, _, token = arg.partition(' ')
                    if method.upper() != 'PLAIN':
                        await reply('504 unsupported authentication'); continue
                    raw = base64.b64decode(token, validate=True).split(b'\0')
                    authenticated = len(raw) == 3 and raw[-2].decode() == USER and raw[-1].decode() == PASS
                    await reply('235 2.7.0 authenticated' if authenticated else '535 5.7.8 rejected')
                except (ValueError, UnicodeDecodeError):
                    await reply('535 5.7.8 rejected')
            elif verb.upper() == 'MAIL':
                if not authenticated:
                    await reply('530 authentication required'); continue
                sender=arg[:320]; await reply('250 2.1.0 sender ok')
            elif verb.upper() == 'RCPT':
                if not sender:
                    await reply('503 bad sequence'); continue
                recipient=arg[:320]; await reply('250 2.1.5 recipient ok')
            elif verb.upper() == 'DATA':
                if not recipient:
                    await reply('503 bad sequence'); continue
                await reply('354 end with <CRLF>.<CRLF>')
                data=bytearray()
                while part := await reader.readline():
                    if part == b'.\r\n': break
                    if part.startswith(b'..'): part=part[1:]
                    if len(data)+len(part)>100_000: raise ValueError('message too large')
                    data.extend(part)
                record={'recipient':recipient,'message':data.decode('utf-8','replace')}
                with OUT.open('a', encoding='utf-8') as out:
                    out.write(json.dumps(record)+'\n')
                sender=recipient=None
                await reply('250 2.0.0 accepted')
            elif verb.upper() == 'RSET':
                sender=recipient=None; await reply('250 reset')
            elif verb.upper() == 'NOOP':
                await reply('250 ok')
            elif verb.upper() == 'QUIT':
                await reply('221 bye');break
            else:
                await reply('502 unsupported command')
    except (ConnectionResetError, BrokenPipeError, ValueError):
        pass
    finally:
        writer.close()
        try:await writer.wait_closed()
        except (ConnectionResetError,BrokenPipeError):pass

async def main() -> None:
    if os.getenv('QUORIVIO_CI_SMTP_TEST') != '1':
        raise SystemExit('Disposable SMTP requires QUORIVIO_CI_SMTP_TEST=1')
    if not PASS:
        raise SystemExit('Disposable SMTP requires QUORIVIO_CI_SMTP_PASSWORD')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.touch(mode=0o600,exist_ok=True)
    os.chmod(OUT,0o600)
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version=ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(os.environ['QUORIVIO_CI_SMTP_CERT'],os.environ['QUORIVIO_CI_SMTP_KEY'])
    server=await asyncio.start_server(connection,HOST,PORT,ssl=ctx)
    async with server: await server.serve_forever()

if __name__=='__main__':asyncio.run(main())
