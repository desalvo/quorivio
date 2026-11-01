#!/usr/bin/env python3
"""Private streaming authenticated encryption for Quorivio backup archives.

Envelope v1: 8-byte MAGIC, 12-byte random nonce, AES-256-GCM ciphertext,
16-byte authentication tag. The magic and nonce are authenticated as AAD.
Keys are 32 random bytes in owner-only regular files; never pass keys in argv.
This utility does not modify the established tar.gz backup/restore format.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import stat
import sys
import tempfile
from contextlib import contextmanager

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b'QVBKENC1'
NONCE_SIZE = 12
TAG_SIZE = 16
CHUNK = 1024 * 1024
HEADER_SIZE = len(MAGIC) + NONCE_SIZE


def key_bytes(path: pathlib.Path) -> bytes:
    """Require an operator-controlled, private, non-symlink raw key file."""
    path = pathlib.Path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('Key must be a regular owner-only file owned by the current user')
        if info.st_size != 32:
            raise ValueError('AES-256 key must contain exactly 32 raw bytes')
        data = os.read(fd, 33)
        if len(data) != 32:
            raise ValueError('Invalid AES-256 key length')
        return data
    finally:
        os.close(fd)


def private_keygen(path: pathlib.Path) -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(os.urandom(32))
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


@contextmanager
def exclusive_output(path: pathlib.Path):
    """Write privately and publish with a no-clobber hardlink after validation."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.exists():
        raise FileExistsError('Refusing to overwrite backup or symlink')
    fd, tmp_name = tempfile.mkstemp(prefix='.quorivio-envelope-', dir=path.parent)
    tmp = pathlib.Path(tmp_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as output:
            yield output
            output.flush()
            os.fsync(output.fileno())
        os.link(tmp, path, follow_symlinks=False)
    finally:
        tmp.unlink(missing_ok=True)


@contextmanager
def checked_input(path: pathlib.Path):
    path = pathlib.Path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Backup input must be a regular file')
        with os.fdopen(fd, 'rb') as source:
            yield source, info
    except BaseException:
        # fdopen closes descriptor only if entered successfully.
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _same_input(source, info):
    after = os.fstat(source.fileno())
    if (after.st_size, after.st_mtime_ns, after.st_ino, after.st_dev) != (
        info.st_size, info.st_mtime_ns, info.st_ino, info.st_dev
    ):
        raise ValueError('Backup input changed during processing')


def encrypt(source: pathlib.Path, target: pathlib.Path, key_file: pathlib.Path) -> None:
    key = key_bytes(key_file)
    nonce = os.urandom(NONCE_SIZE)
    header = MAGIC + nonce
    with checked_input(source) as (inp, info), exclusive_output(target) as out:
        out.write(header)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
        cipher.authenticate_additional_data(header)
        while chunk := inp.read(CHUNK):
            out.write(cipher.update(chunk))
        out.write(cipher.finalize())
        out.write(cipher.tag)
        _same_input(inp, info)


def decrypt(source: pathlib.Path, target: pathlib.Path, key_file: pathlib.Path) -> None:
    key = key_bytes(key_file)
    with checked_input(source) as (inp, info):
        if info.st_size < HEADER_SIZE + TAG_SIZE:
            raise ValueError('Truncated encrypted backup')
        header = inp.read(HEADER_SIZE)
        if not header.startswith(MAGIC) or len(header) != HEADER_SIZE:
            raise ValueError('Not a Quorivio encrypted backup v1')
        inp.seek(-TAG_SIZE, os.SEEK_END)
        tag = inp.read(TAG_SIZE)
        if len(tag) != TAG_SIZE:
            raise ValueError('Truncated authentication tag')
        inp.seek(HEADER_SIZE)
        cipher = Cipher(algorithms.AES(key), modes.GCM(header[len(MAGIC):], tag)).decryptor()
        cipher.authenticate_additional_data(header)
        remaining = info.st_size - HEADER_SIZE - TAG_SIZE
        with exclusive_output(target) as out:
            while remaining:
                chunk = inp.read(min(CHUNK, remaining))
                if not chunk:
                    raise ValueError('Truncated ciphertext')
                out.write(cipher.update(chunk))
                remaining -= len(chunk)
            try:
                out.write(cipher.finalize())
            except InvalidTag as error:
                raise ValueError('Backup authentication failed: wrong key or tampered archive') from error
            _same_input(inp, info)


def rotate(source: pathlib.Path, target: pathlib.Path, old_key: pathlib.Path, new_key: pathlib.Path) -> None:
    """Authenticated one-pass AES-GCM re-encryption without plaintext on disk.

    Both the new ciphertext and its tag are private until the old authentication
    tag has been checked. Any wrong key, corruption, source mutation, or write
    failure leaves no published target (the staging ciphertext is removed).
    """
    previous = key_bytes(old_key)
    replacement = key_bytes(new_key)
    if previous == replacement:
        raise ValueError('Rotation requires a distinct new key')
    with checked_input(source) as (inp, info):
        if info.st_size < HEADER_SIZE + TAG_SIZE:
            raise ValueError('Truncated encrypted backup')
        previous_header = inp.read(HEADER_SIZE)
        if len(previous_header) != HEADER_SIZE or not previous_header.startswith(MAGIC):
            raise ValueError('Not a Quorivio encrypted backup v1')
        inp.seek(-TAG_SIZE, os.SEEK_END)
        old_tag = inp.read(TAG_SIZE)
        inp.seek(HEADER_SIZE)
        decipher = Cipher(algorithms.AES(previous),
                          modes.GCM(previous_header[len(MAGIC):], old_tag)).decryptor()
        decipher.authenticate_additional_data(previous_header)
        fresh_header = MAGIC + os.urandom(NONCE_SIZE)
        encipher = Cipher(algorithms.AES(replacement),
                          modes.GCM(fresh_header[len(MAGIC):])).encryptor()
        encipher.authenticate_additional_data(fresh_header)
        remaining = info.st_size - HEADER_SIZE - TAG_SIZE
        with exclusive_output(target) as output:
            output.write(fresh_header)
            while remaining:
                chunk = inp.read(min(CHUNK, remaining))
                if not chunk:
                    raise ValueError('Truncated encrypted backup during rotation')
                remaining -= len(chunk)
                # Plaintext exists only transiently in bounded process memory.
                output.write(encipher.update(decipher.update(chunk)))
            try:
                final_clear = decipher.finalize()
            except InvalidTag as error:
                raise ValueError('Backup authentication failed: wrong key or tampered archive') from error
            output.write(encipher.update(final_clear))
            output.write(encipher.finalize())
            output.write(encipher.tag)
            _same_input(inp, info)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    keygen = commands.add_parser('keygen', help='create private random 32-byte encryption key')
    keygen.add_argument('--key-file', required=True)
    for action in ('encrypt', 'decrypt'):
        operation = commands.add_parser(action)
        operation.add_argument('--input', required=True)
        operation.add_argument('--output', required=True)
        operation.add_argument('--key-file', required=True)
    rekey = commands.add_parser('rotate', help='authenticate with old key, re-encrypt with new key')
    rekey.add_argument('--input', required=True)
    rekey.add_argument('--output', required=True)
    rekey.add_argument('--old-key-file', required=True)
    rekey.add_argument('--new-key-file', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'keygen':
            private_keygen(pathlib.Path(args.key_file))
        elif args.action == 'rotate':
            rotate(pathlib.Path(args.input), pathlib.Path(args.output), pathlib.Path(args.old_key_file), pathlib.Path(args.new_key_file))
        else:
            globals()[args.action](pathlib.Path(args.input), pathlib.Path(args.output), pathlib.Path(args.key_file))
    except (OSError, ValueError) as error:
        print(f'Backup envelope operation failed: {error}', file=sys.stderr)
        raise SystemExit(1) from None
    print(f'Quorivio {args.action}: success')


if __name__ == '__main__':
    main()
