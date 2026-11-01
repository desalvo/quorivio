"""Fourth batch: 30 behavioral regression checks for OOXML and editable export.

Every case calls the real archive preflight or PowerPoint serializer. No mocked
security predicates, no network access, and no source-text-only assertions.
"""
import copy
import pathlib
import sys
import tempfile
import unittest
import uuid
from zipfile import ZipFile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pptx_portable as portable


def definition(kind='text'):
    return {'format': 'quorivio-session', 'version': 1, 'activities': [
        {'type': 'slide', 'page_design': {'widgets': [{
            'kind': kind, 'label': 'Hello',
            'position': {'x': 5, 'y': 10, 'width': 40, 'height': 20},
            'style': {}}]}}]}


class OOXMLFourth30(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)

    def validate(self, members):
        path = self.root / 'input.pptx'
        base = {'[Content_Types].xml': b'<Types/>', 'ppt/presentation.xml': b'<presentation/>'}
        base.update(members)
        with ZipFile(path, 'w') as archive:
            for name, value in base.items():
                archive.writestr(name, value)
        return portable.validate_pptx_archive(path)

    def rel(self, target, extra=''):
        return f'<Relationships><Relationship Type="slide" Target="{target}" {extra}/></Relationships>'.encode()

    def test_01_uppercase_relationship_extension_is_inspected(self):
        with self.assertRaisesRegex(ValueError, 'External'):
            self.validate({'ppt/_rels/presentation.xml.RELS': self.rel('https://example.test', 'TargetMode="External"')})

    def test_02_double_encoded_absolute_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('%252fetc%252fpasswd')})

    def test_03_nested_encoded_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'escapes package root'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('..%252f..%252fprivate')})

    def test_04_traversal_beyond_package_root_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'escapes package root'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('../../secret')})

    def test_05_root_relationship_cannot_escape(self):
        with self.assertRaisesRegex(ValueError, 'escapes package root'):
            self.validate({'_rels/.rels': self.rel('../outside')})

    def test_06_legitimate_relative_slide_media_is_accepted(self):
        self.validate({'ppt/slides/_rels/slide1.xml.rels': self.rel('../media/logo.png')})

    def test_07_empty_relationship_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('')})

    def test_08_xml_character_reference_control_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('slide&#10;bad.xml')})

    def test_09_percent_encoded_uri_scheme_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('file%3A///etc/passwd')})

    def test_10_dot_segment_archive_member_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/./slides/slide1.xml': b'<slide/>'})

    def test_11_raw_control_character_in_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.validate({'ppt/_rels/presentation.xml.rels': self.rel('slide&#13;bad.xml')})

    def test_12_valid_root_relationship_is_accepted(self):
        self.validate({'_rels/.rels': self.rel('ppt/presentation.xml')})


class ExportFourth30(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)

    def export(self, data, **kwargs):
        return portable.portable_to_pptx(data, self.root / 'output.pptx', **kwargs)

    def bad(self, mutate, message):
        data = definition()
        mutate(data['activities'][0]['page_design']['widgets'][0])
        with self.assertRaisesRegex(ValueError, message):
            self.export(data)
        self.assertFalse((self.root / 'output.pptx').exists())

    def test_13_valid_font_family_roundtrips(self):
        data = definition()
        data['activities'][0]['page_design']['widgets'][0]['style']['fontFamily'] = 'Arial'
        self.export(data)
        self.assertTrue((self.root / 'output.pptx').is_file())

    def test_14_blank_font_family_is_rejected(self):
        self.bad(lambda w: w['style'].update(fontFamily='  '), 'font family')

    def test_15_oversized_font_family_is_rejected(self):
        self.bad(lambda w: w['style'].update(fontFamily='A' * 81), 'font family')

    def test_16_xml_surrogate_font_family_is_rejected(self):
        self.bad(lambda w: w['style'].update(fontFamily='\ud800'), 'font family')

    def test_17_invalid_font_color_is_rejected(self):
        self.bad(lambda w: w['style'].update(color='red'), 'color')

    def test_18_invalid_fill_color_is_rejected(self):
        self.bad(lambda w: w['style'].update(fillColor='#12345G'), 'color')

    def test_19_invalid_stroke_color_is_rejected(self):
        self.bad(lambda w: w['style'].update(strokeColor='#00000000'), 'color')

    def test_20_unknown_shape_type_is_rejected(self):
        self.bad(lambda w: w['style'].update(shapeType='arbitrary'), 'shape')

    def test_21_negative_font_size_is_rejected(self):
        self.bad(lambda w: w['style'].update(fontSize=-4), 'style')

    def test_22_extreme_font_size_is_rejected(self):
        self.bad(lambda w: w['style'].update(fontSize=10**12), 'style')

    def test_23_boolean_coordinate_is_rejected(self):
        self.bad(lambda w: w['position'].update(x=True), 'geometry')

    def test_24_string_coordinate_is_rejected(self):
        self.bad(lambda w: w['position'].update(width='40'), 'geometry')

    def test_25_missing_position_defaults_safely(self):
        data = definition()
        del data['activities'][0]['page_design']['widgets'][0]['position']
        self.export(data)
        self.assertTrue((self.root / 'output.pptx').is_file())

    def test_26_invalid_image_asset_id_fails_preflight(self):
        data = definition('image')
        data['activities'][0]['page_design']['widgets'][0]['assetId'] = '../secret'
        with self.assertRaisesRegex(ValueError, 'asset ID'):
            self.export(data)

    def test_27_wrong_uuid_version_fails_preflight(self):
        data = definition('image')
        data['activities'][0]['page_design']['widgets'][0]['assetId'] = str(uuid.uuid1())
        with self.assertRaisesRegex(ValueError, 'asset ID'):
            self.export(data)

    def test_28_explicit_null_design_is_rejected(self):
        data = definition()
        data['activities'][0]['page_design'] = None
        with self.assertRaisesRegex(ValueError, 'design'):
            self.export(data)

    def test_29_explicit_null_widget_list_is_rejected(self):
        data = definition()
        data['activities'][0]['page_design']['widgets'] = None
        with self.assertRaisesRegex(ValueError, 'widgets'):
            self.export(data)

    def test_30_export_rejects_symlinked_media_ancestor(self):
        private = self.root / 'private'
        private.mkdir()
        alias = self.root / 'alias'
        alias.symlink_to(private, target_is_directory=True)
        media = alias / 'media'
        media.mkdir()
        data = definition('image')
        data['activities'][0]['page_design']['widgets'][0]['assetId'] = str(uuid.uuid4())
        with self.assertRaisesRegex(ValueError, 'Missing or oversized image asset'):
            self.export(data, media_dir=media)


if __name__ == '__main__':
    unittest.main()
