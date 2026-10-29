#!/usr/bin/env python3
"""Fail-closed mirror of *already encrypted* Quorivio backups to a mounted volume.

The operator must explicitly mount and secure an independent volume; mountpoint
checking cannot prove geographical separation, independent failure domains, or
production DR objectives. Keys are never copied. The destination is published
only after AES-GCM authentication and inner-manifest verification. No cleartext
backup is placed on the destination volume; the verification scratch directory
MUST be an operator-controlled encrypted filesystem.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import stat
import sys
import tempfile
from datetime import datetime, timezone

from backup_envelope import MAGIC, checked_input, key_bytes
from secure_instance_backup import _reject_symlink_ancestors, private_workspace, verify_encrypted

CHUNK = 1024 * 1024
FORMAT = 'quorivio-encrypted-mirror-receipt'


def _private_dir(path: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    _reject_symlink_ancestors(path)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('Mirror directory must exist and be owner-only (0700)')
    return path


def _mount_guard(directory: pathlib.Path, mount_root: pathlib.Path) -> None:
    """Never write to the local underlying directory after a remote unmount."""
    directory = _private_dir(directory)
    mount_root = pathlib.Path(mount_root)
    _reject_symlink_ancestors(mount_root)
    if mount_root == pathlib.Path('/') or mount_root not in (directory, *directory.parents):
        raise ValueError('Expected mount must be a non-root ancestor of mirror directory')
    if not mount_root.is_dir() or not os.path.ismount(mount_root):
        raise ValueError('Independent backup mount is not mounted; refusing local fallback')
    if mount_root.stat().st_dev != directory.stat().st_dev:
        raise ValueError('Mirror target is not on the expected mount filesystem')


def _private_file(path: pathlib.Path):
    _reject_symlink_ancestors(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('Mirror archive and receipt must be private regular files')
    return info


def _identity(info: os.stat_result) -> tuple:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_mode, info.st_uid)


def _digest_words(value: str) -> list[str]:
    return [value[i:i + 8] for i in range(0, 64, 8)]


def _read_receipt(path: pathlib.Path) -> dict:
    info = _private_file(path)
    if info.st_size > 8192:
        raise ValueError('Invalid or oversized mirror receipt')
    with path.open('rb') as stream:
        receipt = json.load(stream)
    if not isinstance(receipt, dict) or receipt.get('format') != FORMAT or receipt.get('version') != 1:
        raise ValueError('Invalid mirror receipt format')
    return receipt


def _sha256_file(path: pathlib.Path) -> tuple[str, int]:
    info = _private_file(path)
    h = hashlib.sha256()
    with checked_input(path) as (stream, opened):
        if _identity(info) != _identity(opened):
            raise ValueError('Mirror input changed before hashing')
        count = 0
        while part := stream.read(CHUNK):
            count += len(part)
            h.update(part)
        if _identity(os.fstat(stream.fileno())) != _identity(opened):
            raise ValueError('Mirror input changed during hashing')
    return h.hexdigest(), count


def mirror_backup(source: pathlib.Path, directory: pathlib.Path, mount_root: pathlib.Path,
                  key_file: pathlib.Path, work_dir: pathlib.Path) -> dict:
    """Copy, authenticate and atomically publish the encrypted copy and its receipt."""
    source = pathlib.Path(source)
    directory = pathlib.Path(directory)
    _mount_guard(directory, mount_root)
    # Never put an unencrypted staging workspace or the backup key on the
    # mirror volume; independent key custody is an explicit safety boundary.
    protected_root = pathlib.Path(mount_root).resolve()
    if pathlib.Path(key_file).resolve().is_relative_to(protected_root):
        raise ValueError('Encryption key must be kept outside the mirror mount')
    if pathlib.Path(work_dir).resolve().is_relative_to(protected_root):
        raise ValueError('Decryption workspace must be outside the mirror mount')
    if source.resolve().is_relative_to(protected_root):
        raise ValueError('Mirror source must be outside the mirror mount')
    if source.name in ('', '.', '..') or not source.name.endswith('.qenc'):
        raise ValueError('Only named .qenc archives may be mirrored')
    if source.resolve().parent == directory.resolve():
        raise ValueError('Source and mirror destination must be different directories')
    _private_file(source)
    key_bytes(pathlib.Path(key_file))
    # Fail fast if the scratch volume isn't private; no plaintext in the mirror.
    with private_workspace(pathlib.Path(work_dir)):
        pass
    output = directory / source.name
    receipt_path = directory / (source.name + '.receipt.json')
    if output.exists() or output.is_symlink() or receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError('Mirror archive/receipt exists; refusing overwrite')
    fd, temp_name = tempfile.mkstemp(prefix='.quorivio-mirror-', dir=directory)
    temporary = pathlib.Path(temp_name)
    published = False
    try:
        os.fchmod(fd, 0o600)
        with checked_input(source) as (src, original), os.fdopen(fd, 'wb') as dest:
            if src.read(len(MAGIC)) != MAGIC:
                raise ValueError('Mirror source is not an encrypted Quorivio archive')
            src.seek(0)
            digest = hashlib.sha256()
            copied = 0
            while block := src.read(CHUNK):
                dest.write(block)
                digest.update(block)
                copied += len(block)
            dest.flush()
            os.fsync(dest.fileno())
            if _identity(os.fstat(src.fileno())) != _identity(original):
                raise ValueError('Source changed during copy')
        # Authentication and inner manifest verification happen on the copied bytes.
        manifest = verify_encrypted(temporary, pathlib.Path(key_file), pathlib.Path(work_dir))
        if _sha256_file(temporary) != (digest.hexdigest(), copied):
            raise ValueError('Mirror staging bytes changed')
        if _sha256_file(source) != (digest.hexdigest(), copied):
            raise ValueError('Source changed after copy')
        _mount_guard(directory, mount_root)
        record = {
            'format': FORMAT, 'version': 1, 'archive': source.name,
            'size_bytes': copied, 'sha256_hex_groups': _digest_words(digest.hexdigest()),
            'verified_files': len(manifest['files']), 'backup_created_at': manifest['created_at'],
            'mirrored_at': datetime.now(timezone.utc).isoformat(),
            'limitations': 'Technical authenticated copy only; not proof of offsite independence or production RPO/RTO.',
        }
        # No-clobber publication of the ciphertext, then receipt. Failures
        # remove the new archive, never modify an existing destination.
        os.link(temporary, output, follow_symlinks=False)
        published = True
        temp_receipt = None
        try:
            with tempfile.NamedTemporaryFile(prefix='.quorivio-mirror-receipt-', dir=directory,
                                             delete=False) as stream:
                temp_receipt = pathlib.Path(stream.name)
                os.fchmod(stream.fileno(), 0o600)
                stream.write((json.dumps(record, sort_keys=True, indent=2) + '\n').encode('utf-8'))
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temp_receipt, receipt_path, follow_symlinks=False)
        finally:
            if temp_receipt is not None:
                temp_receipt.unlink(missing_ok=True)
        return record
    except BaseException:
        if published:
            output.unlink(missing_ok=True)
        raise
    finally:
        temporary.unlink(missing_ok=True)


def verify_mirror(directory: pathlib.Path, mount_root: pathlib.Path, name: str,
                  key_file: pathlib.Path, work_dir: pathlib.Path) -> dict:
    directory = pathlib.Path(directory)
    _mount_guard(directory, mount_root)
    protected_root = pathlib.Path(mount_root).resolve()
    if pathlib.Path(key_file).resolve().is_relative_to(protected_root):
        raise ValueError('Encryption key must be kept outside the mirror mount')
    if pathlib.Path(work_dir).resolve().is_relative_to(protected_root):
        raise ValueError('Decryption workspace must be outside the mirror mount')
    if pathlib.Path(name).name != name or '\\' in name or not name.endswith('.qenc') or name in ('', '.', '..'):
        raise ValueError('Unsafe mirror archive name')
    source = directory / name
    receipt = _read_receipt(directory / (name + '.receipt.json'))
    if receipt.get('archive') != name or not isinstance(receipt.get('sha256_hex_groups'), list):
        raise ValueError('Mirror receipt does not refer to archive')
    digest, size = _sha256_file(source)
    if (receipt['sha256_hex_groups'] != _digest_words(digest) or
            receipt.get('size_bytes') != size):
        raise ValueError('Mirrored archive checksum mismatch')
    verified = verify_encrypted(source, pathlib.Path(key_file), pathlib.Path(work_dir))
    if (len(verified['files']) != receipt.get('verified_files') or
            verified['created_at'] != receipt.get('backup_created_at')):
        raise ValueError('Mirrored backup manifest differs from receipt')
    _mount_guard(directory, mount_root)
    return {'status': 'verified', 'archive': name, 'files': len(verified['files']),
            'size_bytes': size, 'limitations': receipt['limitations']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('push', 'verify'))
    parser.add_argument('--directory', type=pathlib.Path, required=True)
    parser.add_argument('--mount-root', type=pathlib.Path, required=True)
    parser.add_argument('--source', type=pathlib.Path, help='required for push')
    parser.add_argument('--name', help='required for verify')
    parser.add_argument('--key-file', type=pathlib.Path, required=True)
    parser.add_argument('--work-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == 'push':
            if args.source is None or args.name is not None:
                raise ValueError('Push requires source and forbids name')
            result = mirror_backup(args.source, args.directory, args.mount_root, args.key_file, args.work_dir)
        else:
            if args.name is None or args.source is not None:
                raise ValueError('Verify requires name and forbids source')
            result = verify_mirror(args.directory, args.mount_root, args.name, args.key_file, args.work_dir)
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError) as error:
        print('Encrypted mirror operation failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
