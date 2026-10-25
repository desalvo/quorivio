"""Third 30-intervention batch: behavioral, adversarial converter acceptance.

The cases exercise actual byte parsing and HTTP request handling, not source
text assertions. Passing is not a substitute for a visual fidelity device lab.
"""
import http.client
import io
import json
import pathlib
import struct
import sys
import tempfile
import threading
import unittest
import zlib
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from zipfile import ZipFile, ZIP_BZIP2

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import import_presentation as flat
import pptx_portable as editable
import conversion_worker as worker


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))


def png():
    raw = b'\x00\xff\x00\x00\x00\x00\xff'  # one 2x1 RGB scanline
    return (flat.PNG_SIGNATURE + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 1, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def parts(blob):
    cursor = 8
    result = []
    while cursor < len(blob):
        n = struct.unpack_from('>I', blob, cursor)[0]
        result.append((blob[cursor + 4:cursor + 8], blob[cursor + 8:cursor + 8 + n]))
        cursor += n + 12
    return result


def rebuild(items):
    return flat.PNG_SIGNATURE + b''.join(chunk(name, data) for name, data in items)


class RasterIntegrity30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)

    def check(self, data):
        path = self.root / 'image.png'
        path.write_bytes(data)
        return flat._verify_png(path)

    def test_01_valid_full_png_is_accepted(self):
        self.assertEqual(self.check(png()), len(png()))

    def test_02_corrupt_idat_crc_is_rejected(self):
        data = bytearray(png()); data[-16] ^= 0x11
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.check(bytes(data))

    def test_03_corrupt_iend_crc_is_rejected(self):
        data = bytearray(png()); data[-1] ^= 0x11
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.check(bytes(data))

    def test_04_missing_iend_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'terminator'):
            self.check(rebuild(parts(png())[:-1]))

    def test_05_trailing_bytes_after_iend_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'terminator'):
            self.check(png() + b'payload')

    def test_06_unknown_critical_chunk_is_rejected(self):
        p = parts(png()); p.insert(1, (b'XTRA', b'payload'))
        with self.assertRaisesRegex(ValueError, 'critical'):
            self.check(rebuild(p))

    def test_07_duplicate_ihdr_is_rejected(self):
        p = parts(png()); p.insert(1, p[0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.check(rebuild(p))

    def test_08_noncontiguous_idat_is_rejected(self):
        p = parts(png()); p.insert(2, (b'tEXt', b'Comment\x00ok')); p.insert(3, (b'IDAT', b''))
        with self.assertRaisesRegex(ValueError, 'Noncontiguous'):
            self.check(rebuild(p))

    def test_09_nonzero_iend_is_rejected(self):
        p = parts(png()); p[-1] = (b'IEND', b'x')
        with self.assertRaisesRegex(ValueError, 'terminator'):
            self.check(rebuild(p))

    def test_10_truncated_image_chunk_is_rejected(self):
        data = png()[:-5]
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            self.check(data)

    def test_11_invalid_image_compressed_data_is_rejected(self):
        p = parts(png()); p[1] = (b'IDAT', b'not-zlib-data')
        with self.assertRaisesRegex(ValueError, 'decoding'):
            self.check(rebuild(p))

    def test_12_invalid_chunk_type_is_rejected(self):
        p = parts(png()); p.insert(1, (b'tEX1', b'bad'))
        with self.assertRaisesRegex(ValueError, 'chunk type'):
            self.check(rebuild(p))

    def test_13_ancillary_chunk_crc_is_verified(self):
        p = parts(png()); p.insert(1, (b'tEXt', b'Comment\x00safe'))
        data = bytearray(rebuild(p)); index = data.index(b'tEXt') + 5; data[index] ^= 1
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.check(bytes(data))

    def test_14_valid_ancillary_chunk_is_supported(self):
        p = parts(png()); p.insert(1, (b'tEXt', b'Comment\x00safe'))
        self.assertGreater(self.check(rebuild(p)), len(png()))

    def test_15_invalid_png_color_type_is_rejected(self):
        p = parts(png()); ihdr = bytearray(p[0][1]); ihdr[9] = 7; p[0] = (b'IHDR', bytes(ihdr))
        with self.assertRaisesRegex(ValueError, 'format'):
            self.check(rebuild(p))


class PdfMetadata30(unittest.TestCase):
    def test_16_encrypted_pdf_rejected(self):
        with patch.object(flat, 'run', return_value=b'Pages: 2\nEncrypted: yes (print:no)\n'):
            with self.assertRaisesRegex(ValueError, 'Encrypted'):
                flat._page_count('ignored.pdf')

    def test_17_javascript_pdf_rejected(self):
        with patch.object(flat, 'run', return_value=b'Pages: 2\nJavaScript: yes\n'):
            with self.assertRaisesRegex(ValueError, 'JavaScript'):
                flat._page_count('ignored.pdf')

    def test_18_normal_pdf_accepted(self):
        with patch.object(flat, 'run', return_value=b'Pages: 3\nEncrypted: no\nJavaScript: no\n'):
            self.assertEqual(flat._page_count('ignored.pdf'), 3)


class OOXMLRelations30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)

    def check(self, additions=None, compress=None):
        source = self.root / 'presentation.pptx'
        members = {'[Content_Types].xml': b'<Types/>', 'ppt/presentation.xml': b'<p:presentation/>'}
        members.update(additions or {})
        with ZipFile(source, 'w', compression=compress or 0) as archive:
            for name, value in members.items():
                archive.writestr(name, value)
        editable.validate_pptx_archive(source)

    def rel(self, target, rel_type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'):
        return (f'<Relationships><Relationship Target="{target}" Type="{rel_type}"/></Relationships>').encode()

    def test_19_dtd_in_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DTD'):
            self.check({'ppt/_rels/presentation.xml.rels': b'<!DOCTYPE x [<!ENTITY x "y">]><Relationships/>'})

    def test_20_dtd_in_presentation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DTD'):
            self.check({'ppt/presentation.xml': b'<!DOCTYPE p><p:presentation/>'})

    def test_21_dtd_in_content_types_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DTD'):
            self.check({'[Content_Types].xml': b'<!DOCTYPE Types><Types/>'})

    def test_22_absolute_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('/etc/passwd')})

    def test_23_scheme_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('file:///etc/passwd')})

    def test_24_backslash_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('..\\media\\image.png')})

    def test_25_percent_encoded_separator_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('..%2f..%2fsecret')})

    def test_26_ole_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Active'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('embeddings/object.bin', 'http://example.test/oleObject')})

    def test_27_activex_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Active'):
            self.check({'ppt/_rels/presentation.xml.rels': self.rel('activeX/a.xml', 'http://example.test/activeXControl')})

    def test_28_valid_internal_relationship_supported(self):
        self.check({'ppt/_rels/presentation.xml.rels': self.rel('../media/image.png')})

    def test_29_unsupported_zip_compression_rejected(self):
        with self.assertRaisesRegex(ValueError, 'compression method'):
            self.check(compress=ZIP_BZIP2)


class WorkerBoundary30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.token = 'strong-worker-test-token-32-characters'
        self.patches = [patch.object(worker, 'TOKEN', self.token), patch.object(worker, 'ROOT', self.root)]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), worker.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)

    def close(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=3)

    def request(self, headers=None, body=b'{"job":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}', method='POST'):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.putrequest(method, '/convert')
        for name, value in (headers if headers is not None else [('Authorization', 'Bearer ' + self.token),
                                                                  ('Content-Type', 'application/json'),
                                                                  ('Content-Length', str(len(body)))]):
            conn.putheader(name, value)
        conn.endheaders(body)
        response = conn.getresponse()
        result = response.status
        response.read(); conn.close()
        return result

    def test_30_worker_root_symlink_ancestor_rejected(self):
        real = self.root / 'real'; real.mkdir()
        alias = self.root / 'alias'; alias.symlink_to(real, target_is_directory=True)
        (real / ('a' * 32)).mkdir()
        with patch.object(worker, 'ROOT', alias / 'nested'):
            (real / 'nested').mkdir()
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                worker._workspace('a' * 32)

    def test_31_health_rejects_symlinked_root(self):
        alias = self.root / 'alias'; alias.symlink_to(self.root, target_is_directory=True)
        with patch.object(worker, 'ROOT', alias):
            conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
            conn.request('GET', '/health'); response = conn.getresponse()
            self.assertEqual(response.status, 503); response.read(); conn.close()

    def test_32_raw_token_without_bearer_rejected(self):
        headers = [('Authorization', self.token), ('Content-Type', 'application/json'), ('Content-Length', '42')]
        self.assertEqual(self.request(headers), 403)

    def test_33_duplicate_authorization_headers_rejected(self):
        headers = [('Authorization', 'Bearer ' + self.token), ('Authorization', 'Bearer ' + self.token),
                   ('Content-Type', 'application/json'), ('Content-Length', '42')]
        self.assertEqual(self.request(headers), 403)

    def test_34_transfer_encoding_rejected(self):
        headers = [('Authorization', 'Bearer ' + self.token), ('Content-Type', 'application/json'),
                   ('Content-Length', '42'), ('Transfer-Encoding', 'chunked')]
        self.assertEqual(self.request(headers), 400)

    def test_35_duplicate_content_length_rejected(self):
        headers = [('Authorization', 'Bearer ' + self.token), ('Content-Type', 'application/json'),
                   ('Content-Length', '42'), ('Content-Length', '42')]
        self.assertEqual(self.request(headers), 400)

    def test_36_content_encoding_rejected(self):
        headers = [('Authorization', 'Bearer ' + self.token), ('Content-Type', 'application/json'),
                   ('Content-Length', '42'), ('Content-Encoding', 'gzip')]
        self.assertEqual(self.request(headers), 400)

    def test_37_valid_authorized_request_reaches_job_handler(self):
        with patch.object(worker, 'execute_job', return_value={'page_count': 1}):
            self.assertEqual(self.request(), 200)


if __name__ == '__main__':
    unittest.main()

class AdditionalActiveContentRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = pathlib.Path(self.temp.name) / 'presentation.pptx'

    def check(self, additional):
        members = {'[Content_Types].xml': b'<Types/>', 'ppt/presentation.xml': b'<p:presentation/>'}
        members.update(additional)
        with ZipFile(self.path, 'w') as archive:
            for name, value in members.items():
                archive.writestr(name, value)
        editable.validate_pptx_archive(self.path)

    def test_38_activex_parts_rejected(self):
        with self.assertRaisesRegex(ValueError, 'active'):
            self.check({'ppt/activeX/activeX1.xml': b'<control/>'})

    def test_39_embedded_ole_parts_rejected(self):
        with self.assertRaisesRegex(ValueError, 'active'):
            self.check({'ppt/embeddings/oleObject1.bin': b'payload'})

    def test_40_disguised_macro_enabled_content_type_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Active'):
            self.check({'[Content_Types].xml': b'<Types ContentType="application/vnd.ms-powerpoint.presentation.macroEnabled.main+xml"/>'})

    def test_41_double_encoded_external_uri_rejected(self):
        payload = b'<Relationships><Relationship Target="%2566ile:///etc/passwd"/></Relationships>'
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': payload})

    def test_42_dtd_after_large_xml_comment_rejected(self):
        payload = b'<!--' + b' ' * (300 * 1024) + b'--><!DOCTYPE x><p:presentation/>'
        with self.assertRaisesRegex(ValueError, 'DTD'):
            self.check({'ppt/presentation.xml': payload})

    def test_43_malformed_percent_escape_rejected(self):
        payload = b'<Relationships><Relationship Target="media%2ximage.png"/></Relationships>'
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.check({'ppt/_rels/presentation.xml.rels': payload})
