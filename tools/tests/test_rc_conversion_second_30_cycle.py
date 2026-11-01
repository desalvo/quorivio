"""Second 30-intervention converter batch: real parser, exporter and worker regressions.

All cases exercise behavior; a PASS does not imply visual fidelity of arbitrary decks.
"""
import io
import json
import pathlib
import sys
import tempfile
import unittest
import uuid
from base64 import b64decode
from unittest.mock import patch
from zipfile import ZipFile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pptx_portable as portable
import conversion_worker as worker

PIXEL = b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC')


def document(widget=None):
    return {'format': 'quorivio-session', 'version': 1, 'activities': [
        {'type': 'slide', 'page_design': {'widgets': [widget] if widget is not None else []}}]}


def text_widget(**updates):
    widget = {'kind': 'text', 'label': 'Safe heading',
              'position': {'x': 1, 'y': 1, 'width': 60, 'height': 20}}
    widget.update(updates)
    return widget


class ConversionSecond30(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)

    def export(self, data, name='export.pptx', **kwargs):
        path = self.root / name
        portable.portable_to_pptx(data, path, **kwargs)
        return path

    def archive(self, members):
        path = self.root / 'archive.pptx'
        with ZipFile(path, 'w') as archive:
            for key, value in members.items():
                archive.writestr(key, value)
        return path

    def base_members(self):
        return {'[Content_Types].xml': '<Types/>', 'ppt/presentation.xml': '<p:presentation/>'}

    def test_01_fake_png_signature_rejected(self):
        self.assertFalse(portable._supported_image(b'\x89PNG\r\n\x1a\nspoofed', 'image/png'))

    def test_02_fake_jpeg_signature_rejected(self):
        self.assertFalse(portable._supported_image(b'\xff\xd8\xffspoofed', 'image/jpeg'))

    def test_03_valid_png_accepted(self):
        self.assertTrue(portable._supported_image(PIXEL, 'image/png'))

    def test_04_truncated_png_rejected(self):
        self.assertFalse(portable._supported_image(PIXEL[:-15], 'image/png'))

    def test_05_png_mime_mismatch_rejected(self):
        self.assertFalse(portable._supported_image(PIXEL, 'image/jpeg'))

    def test_06_image_pixel_budget_enforced(self):
        from PIL import Image
        with patch.object(portable, 'MAX_IMAGE_PIXELS', 0):
            self.assertFalse(portable._supported_image(PIXEL, 'image/png'))

    def test_07_case_colliding_ooxml_parts_rejected(self):
        members = self.base_members() | {'PPT/PRESENTATION.XML': 'duplicate'}
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            portable.validate_pptx_archive(self.archive(members))

    def test_08_windows_drive_ooxml_member_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            portable.validate_pptx_archive(self.archive(self.base_members() | {'C:payload': 'x'}))

    def test_09_noncanonical_ooxml_member_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            portable.validate_pptx_archive(self.archive(self.base_members() | {'ppt//media': 'x'}))

    def test_10_script_extension_ooxml_member_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Macro'):
            portable.validate_pptx_archive(self.archive(self.base_members() | {'ppt/evil.ps1': 'x'}))

    def test_11_external_relationship_with_xml_entities_rejected(self):
        payload = '<Relationships><Relationship TargetMode="Ex&#116;ernal" Target="https://bad.example"/></Relationships>'
        with self.assertRaisesRegex(ValueError, 'External'):
            portable.validate_pptx_archive(self.archive(self.base_members() | {'ppt/_rels/presentation.xml.rels': payload}))

    def test_12_malformed_relationships_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            portable.validate_pptx_archive(self.archive(self.base_members() | {'ppt/_rels/presentation.xml.rels': '<broken'}))

    def test_13_symlink_pptx_source_rejected(self):
        original = self.archive(self.base_members())
        link = self.root / 'link.pptx'
        link.symlink_to(original)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            portable.validate_pptx_archive(link)

    def test_14_export_rejects_non_mapping_root(self):
        with self.assertRaisesRegex(ValueError, 'session definition'):
            self.export(['bad'])

    def test_15_export_rejects_empty_slide_list(self):
        data = document(); data['activities'] = []
        with self.assertRaisesRegex(ValueError, 'page count'):
            self.export(data)

    def test_16_export_rejects_invalid_slide(self):
        data = document(); data['activities'] = [None]
        with self.assertRaisesRegex(ValueError, 'slide'):
            self.export(data)

    def test_17_export_rejects_non_mapping_page_design(self):
        data = document(); data['activities'][0]['page_design'] = ['bad']
        with self.assertRaisesRegex(ValueError, 'page design'):
            self.export(data)

    def test_18_export_rejects_non_list_widgets(self):
        data = document(); data['activities'][0]['page_design']['widgets'] = {'kind': 'text'}
        with self.assertRaisesRegex(ValueError, 'widgets'):
            self.export(data)

    def test_19_export_rejects_non_mapping_widget(self):
        data = document(); data['activities'][0]['page_design']['widgets'] = ['bad']
        with self.assertRaisesRegex(ValueError, 'widget'):
            self.export(data)

    def test_20_export_rejects_bad_geometry_type(self):
        with self.assertRaisesRegex(ValueError, 'geometry'):
            self.export(document(text_widget(position='not-a-position')))

    def test_21_export_rejects_bad_numeric_geometry(self):
        with self.assertRaisesRegex(ValueError, 'geometry'):
            self.export(document(text_widget(position={'x': 'bad', 'y': 0, 'width': 10, 'height': 10})))

    def test_22_export_rejects_nonfinite_rotation(self):
        with self.assertRaisesRegex(ValueError, 'rotation'):
            self.export(document(text_widget(position={'x': 0, 'y': 0, 'width': 10, 'height': 10, 'rotation': float('nan')})))

    def test_23_export_rejects_xml_control_character(self):
        with self.assertRaisesRegex(ValueError, 'text'):
            self.export(document(text_widget(label='unsafe\x00text')))

    def test_24_export_rejects_invalid_style_type(self):
        with self.assertRaisesRegex(ValueError, 'style'):
            self.export(document(text_widget(style='invalid')))

    def test_25_export_rejects_invalid_quiz_options(self):
        with self.assertRaisesRegex(ValueError, 'quiz options'):
            self.export(document({'kind': 'question', 'label': 'Quiz', 'options': [{'label': 'x'}] * 13}))

    def test_26_export_never_overwrites_existing_presentation(self):
        destination = self.root / 'export.pptx'
        destination.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            self.export(document(text_widget()))
        self.assertEqual(destination.read_bytes(), b'original')

    def test_27_export_does_not_leave_partial_output_on_error(self):
        from pptx.presentation import Presentation
        with patch.object(Presentation, 'save', side_effect=RuntimeError('broken writer')):
            with self.assertRaisesRegex(RuntimeError, 'broken writer'):
                self.export(document(text_widget()))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_28_import_media_symlink_directory_rejected(self):
        from pptx import Presentation
        source = self.root / 'source.pptx'
        deck = Presentation(); deck.slides.add_slide(deck.slide_layouts[6]); deck.save(source)
        actual = self.root / 'actual'; actual.mkdir()
        link = self.root / 'alias'; link.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinked import media'):
            portable.pptx_to_portable(source, media_dir=link)

    def test_29_worker_detects_mutating_import_source(self):
        from pptx import Presentation
        job = 'a' * 32; work = self.root / job; work.mkdir()
        deck = Presentation(); deck.slides.add_slide(deck.slide_layouts[6]); deck.save(work / 'source.pptx')
        def mutate(source, media_dir):
            (work / 'source.pptx').write_bytes(b'changed')
            return document()
        with patch.object(worker, 'ROOT', self.root), patch.object(worker, 'pptx_to_portable', side_effect=mutate), patch.object(worker, 'inspect_pptx_fidelity', return_value={}):
            with self.assertRaisesRegex(ValueError, 'changed'):
                worker.execute_portable_job(job, 'import')
        self.assertFalse((work / 'portable.json').exists())
        self.assertFalse((work / 'import-media').exists())
        self.assertFalse((work / '.conversion-lock').exists())

    def test_30_worker_detects_mutating_export_source(self):
        job = 'b' * 32; work = self.root / job; work.mkdir()
        (work / 'portable.json').write_text(json.dumps(document(text_widget())))
        def mutate(data, destination, media_dir):
            (work / 'portable.json').write_text('changed')
            pathlib.Path(destination).write_bytes(b'fake')
        with patch.object(worker, 'ROOT', self.root), patch.object(worker, 'portable_to_pptx', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'changed'):
                worker.execute_portable_job(job, 'export')
        self.assertFalse((work / 'presentation.pptx').exists())
        self.assertFalse((work / '.conversion-lock').exists())


    def test_31_worker_rejects_symlinked_conversion_root(self):
        actual = self.root / 'actual'; actual.mkdir()
        job = 'c' * 32; (actual / job).mkdir()
        alias = self.root / 'alias'; alias.symlink_to(actual, target_is_directory=True)
        with patch.object(worker, 'ROOT', alias):
            with self.assertRaisesRegex(ValueError, 'unsafe conversion root'):
                worker._workspace(job)

    def test_32_cli_import_never_overwrites_existing_json(self):
        from pptx import Presentation
        import sys
        source = self.root / 'source.pptx'
        deck = Presentation(); deck.slides.add_slide(deck.slide_layouts[6]); deck.save(source)
        destination = self.root / 'session.json'; destination.write_text('keep this')
        with patch.object(sys, 'argv', ['pptx_portable.py', 'import', str(source), str(destination)]):
            with self.assertRaises(FileExistsError):
                portable.main()
        self.assertEqual(destination.read_text(), 'keep this')

    def test_33_cli_import_publishes_valid_private_json(self):
        from pptx import Presentation
        import sys
        source = self.root / 'source.pptx'
        deck = Presentation(); deck.slides.add_slide(deck.slide_layouts[6]); deck.save(source)
        destination = self.root / 'session.json'
        with patch.object(sys, 'argv', ['pptx_portable.py', 'import', str(source), str(destination)]):
            portable.main()
        self.assertEqual(json.loads(destination.read_text())['format'], 'quorivio-session')
        self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        self.assertFalse(list(self.root.glob('.quorivio-portable-*')))

    def test_34_valid_jpeg_accepted(self):
        from PIL import Image
        buffer = io.BytesIO()
        Image.new('RGB', (2, 2), (20, 30, 40)).save(buffer, format='JPEG')
        self.assertTrue(portable._supported_image(buffer.getvalue(), 'image/jpeg'))

    def test_35_export_does_not_leave_temporary_file(self):
        output = self.export(document(text_widget()))
        self.assertTrue(output.is_file())
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        self.assertFalse(list(self.root.glob('.quorivio-pptx-*')))


if __name__ == '__main__':
    unittest.main()
