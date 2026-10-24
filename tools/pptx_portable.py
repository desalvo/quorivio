#!/usr/bin/env python3
"""Native OOXML PPTX import/export for supported editable text and image widgets.

The parser does not execute embedded content. Unsupported native features (animations,
SmartArt, complex charts and masters) are reported separately rather than silently
claimed as editable.
"""
import argparse
import json
import math
import hashlib
import uuid
from datetime import date
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import re

MAX_PPTX_BYTES = 50 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
MAX_ZIP_ENTRIES = 3000
MAX_ZIP_MEMBER_BYTES = 80 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 1000
def _supported_image(blob, mime):
    """Accept recognized image bytes, not only the untrusted OOXML content type."""
    if not isinstance(blob, bytes) or not 0 < len(blob) <= 10 * 1024 * 1024:
        return False
    if mime == 'image/png':
        return blob.startswith(b'\x89PNG\r\n\x1a\n')
    if mime == 'image/jpeg':
        return blob.startswith(b'\xff\xd8\xff')
    return False


SUPPORTED_FONTS = {"Arial", "Georgia", "Verdana", "Tahoma", "Trebuchet MS", "monospace"}

def validate_pptx_archive(source):
    """Reject oversized/bomb-like OOXML packages before python-pptx parses them."""
    path = Path(source)
    if path.stat().st_size > MAX_PPTX_BYTES:
        raise ValueError("PPTX exceeds 50 MiB import limit")
    try:
        with ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ZIP_ENTRIES or sum(e.file_size for e in entries) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("PPTX decompression limits exceeded")
            if any(e.file_size > MAX_ZIP_MEMBER_BYTES or
                   (e.file_size > 1024 * 1024 and e.file_size > max(e.compress_size, 1) * MAX_ZIP_COMPRESSION_RATIO)
                   for e in entries):
                raise ValueError('Suspicious OOXML compression ratio or member size')
            if any(((e.external_attr >> 16) & 0o170000) == 0o120000 for e in entries):
                raise ValueError('OOXML symbolic links are forbidden')
            if any(e.filename.startswith('/') or '..' in e.filename.split('/') or '\\' in e.filename or (e.flag_bits & 1) for e in entries):
                raise ValueError('Unsafe OOXML archive member')
            if len({e.filename for e in entries}) != len(entries):
                raise ValueError('Duplicate OOXML archive member')
            if any(e.filename.lower().endswith(("vbaproject.bin", ".exe", ".dll", ".vbs", ".js")) for e in entries):
                raise ValueError("Macro or executable content is not supported")
            if not {'[Content_Types].xml', 'ppt/presentation.xml'}.issubset({e.filename for e in entries}):
                raise ValueError("Not an OOXML presentation")
            # OOXML relationship parts can reference external resources; never
            # let a document import silently carry active external references.
            for entry in entries:
                if entry.filename.endswith('.rels'):
                    if entry.file_size > 2 * 1024 * 1024:
                        raise ValueError('Oversized OOXML relationships')
                    payload = archive.read(entry)
                    if re.search(rb'TargetMode\s*=\s*[\"\']External[\"\']', payload, re.I):
                        raise ValueError('External OOXML relationships are not supported')
    except BadZipFile as exc:
        raise ValueError("Invalid PPTX archive") from exc



def _position(shape, width, height):
    """Preserve small objects instead of enlarging logos/text to legacy 12%/8% minima.

    Off-canvas elements are clipped because the editable Quorivio canvas cannot
    represent them without invalid coordinates. Report that loss separately.
    """
    x = max(0.0, min(99.0, shape.left / width * 100))
    y = max(0.0, min(99.0, shape.top / height * 100))
    w = max(0.01, min(100.0 - x, shape.width / width * 100))
    h = max(0.01, min(100.0 - y, shape.height / height * 100))
    return {'x': round(x, 4), 'y': round(y, 4),
            'width': round(w, 4), 'height': round(h, 4)}


class _PositionedShape:
    """Read-only proxy for a child positioned inside one or more PPTX groups."""
    def __init__(self, original, left, top, width, height, rotation):
        self._original = original
        self.left, self.top = left, top
        self.width, self.height = width, height
        self.rotation = rotation

    def __getattr__(self, name):
        return getattr(self._original, name)


def _flatten_shapes(shapes, transform=None, parent_rotation=0.0, depth=0):
    """Flatten nested OOXML groups while preserving their child coordinate systems.

    This preserves text and supported primitives; the grouping relation, rotations
    involving non-right-angle group transforms and effects are inherently lossy.
    A depth limit rejects pathological nesting instead of exhausting recursion.
    """
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    if depth > 12:
        raise ValueError('PowerPoint groups exceed maximum nesting depth')
    for shape in shapes:
        if transform is None:
            left, top, width, height = shape.left, shape.top, shape.width, shape.height
        else:
            ox, oy, sx, sy = transform
            left = int(round(ox + shape.left * sx))
            top = int(round(oy + shape.top * sy))
            width = int(round(shape.width * sx))
            height = int(round(shape.height * sy))
        rotation = (parent_rotation + float(shape.rotation or 0)) % 360
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            child = shape.shapes
            if not shape.width or not shape.height or not shape._element.grpSpPr.xfrm.chExt.cx or not shape._element.grpSpPr.xfrm.chExt.cy:
                continue
            child_transform = (left - shape._element.grpSpPr.xfrm.chOff.x * width / shape._element.grpSpPr.xfrm.chExt.cx,
                               top - shape._element.grpSpPr.xfrm.chOff.y * height / shape._element.grpSpPr.xfrm.chExt.cy,
                               width / shape._element.grpSpPr.xfrm.chExt.cx, height / shape._element.grpSpPr.xfrm.chExt.cy)
            yield from _flatten_shapes(child, child_transform, rotation, depth + 1)
        else:
            yield _PositionedShape(shape, left, top, width, height, rotation)


def pptx_to_portable(source, title=None, media_dir=None):
    from pptx import Presentation
    validate_pptx_archive(source)
    presentation = Presentation(str(source))
    activities = []
    imported_assets = []
    total_media_bytes = 0
    media_by_digest = {}  # Share identical embedded pictures across slides.
    if media_dir is not None:
        Path(media_dir).mkdir(parents=True, exist_ok=True, mode=0o700)
    if len(presentation.slides) > 200:
        raise ValueError('Quorivio supports at most 200 pages per import')
    for index, slide in enumerate(presentation.slides):
        widgets = []
        slide_heading = None
        for shape in _flatten_shapes(slide.shapes):
            if shape.shape_type == 13 and media_dir is not None and len(widgets) < 16:
                image = shape.image
                mime = image.content_type
                blob = image.blob
                # Validate MIME and bytes before applying deduplication or media budgets.
                # The previous mixed `and/or` condition could accept unsupported
                # formats whenever an unused media budget was available.
                supported = _supported_image(blob, mime)
                digest = hashlib.sha256(blob).hexdigest() if supported else None
                existing = media_by_digest.get((digest, mime)) if supported else None
                within_budget = (len(imported_assets) < 200 and
                                 total_media_bytes + len(blob) <= 50 * 1024 * 1024)
                if supported and (existing is not None or within_budget):
                    existing = media_by_digest.get((digest, mime))
                    if existing is None:
                        asset_id = str(uuid.uuid4())
                        (Path(media_dir) / asset_id).write_bytes(blob)
                        total_media_bytes += len(blob)
                        imported_assets.append({'id': asset_id, 'mime': mime,
                                                'bytes': len(blob), 'sha256': digest})
                        media_by_digest[(digest, mime)] = asset_id
                    else:
                        asset_id = existing
                    position = _position(shape, presentation.slide_width, presentation.slide_height)
                    rotation = float(shape.rotation or 0)
                    if math.isfinite(rotation) and rotation:
                        position['rotation'] = round(rotation % 360, 2)
                    widgets.append({'id': f'pptx_{index+1}_{len(widgets)+1}', 'kind': 'image',
                                    'label': f'PowerPoint image {len(widgets)+1}',
                                    'assetId': asset_id, 'position': position})
                continue
            # Flatten native PPTX tables to independently editable cell text widgets.
            # Preserve cell coordinates rather than discarding textual information.
            # Table semantics/borders remain explicitly lossy in fidelity reporting.
            if shape.has_table:
                table = shape.table
                left, top = int(shape.left), int(shape.top)
                row_y = top
                for row in table.rows:
                    col_x = left
                    for column_index, cell in enumerate(row.cells):
                        cell_width = int(table.columns[column_index].width)
                        content = cell.text.strip()
                        if content and len(widgets) < 16:
                            class _CellGeometry:
                                pass
                            geometry = _CellGeometry()
                            geometry.left, geometry.top = col_x, row_y
                            geometry.width, geometry.height = cell_width, int(row.height)
                            position = _position(geometry, presentation.slide_width, presentation.slide_height)
                            widgets.append({'id': f'pptx_{index+1}_{len(widgets)+1}',
                                            'kind': 'text', 'label': content[:240],
                                            'description': content[:500], 'position': position,
                                            'style': {}})
                            if slide_heading is None:
                                slide_heading = content.splitlines()[0][:160]
                        col_x += cell_width
                    row_y += int(row.height)
                continue
            # Preserve chart titles as editable text, without claiming to preserve
            # chart series, axes or styling. Charts without a title remain reported.
            if shape.has_chart:
                chart = shape.chart
                chart_title = ''
                if chart.has_title:
                    chart_title = chart.chart_title.text_frame.text.strip()
                if chart_title and len(widgets) < 16:
                    position = _position(shape, presentation.slide_width, presentation.slide_height)
                    widgets.append({'id': f'pptx_{index+1}_{len(widgets)+1}',
                                    'kind': 'text', 'label': chart_title[:240],
                                    'description': chart_title[:500],
                                    'position': position, 'style': {}})
                    if slide_heading is None:
                        slide_heading = chart_title.splitlines()[0][:160]
                continue
            from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_AUTO_SHAPE_TYPE
            editable_shape = (shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and
                              shape.auto_shape_type in (MSO_AUTO_SHAPE_TYPE.RECTANGLE,
                                  MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, MSO_AUTO_SHAPE_TYPE.OVAL,
                                  MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE))
            if not editable_shape and (not shape.has_text_frame or not shape.text.strip()):
                continue
            # Explicitly limit to supported editable elements. Warn separately.
            if len(widgets) >= 16:
                break
            text = shape.text.strip() if shape.has_text_frame else ''
            if slide_heading is None:
                slide_heading = next((line.strip() for line in text.splitlines() if line.strip()), None)
            first_run = next((run for paragraph in shape.text_frame.paragraphs for run in paragraph.runs if run.text.strip()), None) if shape.has_text_frame else None
            style = {}
            if first_run is not None:
                font = first_run.font
                if font.name and font.name in SUPPORTED_FONTS: style['fontFamily'] = font.name
                if font.size: style['fontSize'] = max(10, min(96, round(font.size.pt)))
                if font.bold is not None: style['bold'] = bool(font.bold)
                if font.italic is not None: style['italic'] = bool(font.italic)
                if font.underline is not None: style['underline'] = bool(font.underline)
                try:
                    if font.color and font.color.type is not None and font.color.rgb is not None:
                        style['color'] = '#' + str(font.color.rgb)
                except (AttributeError, TypeError, ValueError):
                    pass  # Theme colors cannot be represented as a fixed RGB value.
            position = _position(shape, presentation.slide_width, presentation.slide_height)
            rotation = float(shape.rotation or 0)
            if math.isfinite(rotation) and rotation:
                position['rotation'] = round(rotation % 360, 2)
            # Supported auto-shapes, including decorative shapes without text,
            # become independent editable canvas widgets.
            from pptx.enum.shapes import MSO_SHAPE_TYPE
            from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
            widget_kind = 'postit' if editable_shape else 'text'
            if widget_kind == 'postit':
                try:
                    from pptx.enum.dml import MSO_FILL
                    if shape.fill.type == MSO_FILL.SOLID and shape.fill.fore_color.rgb is not None:
                        style['fillColor'] = '#' + str(shape.fill.fore_color.rgb)
                except (AttributeError, TypeError, ValueError):
                    pass
                try:
                    if shape.line.color.rgb is not None:
                        style['strokeColor'] = '#' + str(shape.line.color.rgb)
                except (AttributeError, TypeError, ValueError):
                    pass
                if shape.auto_shape_type == MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE:
                    style['rounded'] = True
                elif shape.auto_shape_type == MSO_AUTO_SHAPE_TYPE.OVAL:
                    style['shapeType'] = 'ellipse'
                elif shape.auto_shape_type == MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE:
                    style['shapeType'] = 'triangle'
            widgets.append({'id': f'pptx_{index+1}_{len(widgets)+1}', 'kind': widget_kind,
                            'label': text[:240], 'description': text[:500],
                            'position': position, 'style': style})
        activities.append({'type': 'slide', 'title': (slide_heading or f'Slide {index+1}')[:160], 'options': [],
                           'correct_option_id': None, 'correct_option_ids': [],
                           'answer_mode': 'text', 'answer_required': False,
                           'duration_seconds': None, 'page_design': {'widgets': widgets},
                           'result_design': {}})
    return {'import_assets': imported_assets, 'format': 'quorivio-session', 'version': 1,
            'session': {'title': (title or Path(source).stem)[:160],
                        'reference_date': date.today().isoformat(), 'theme': {},
                        'allow_anonymous': True, 'show_results': False},
            'activities': activities}


def inspect_pptx_fidelity(source):
    """Report exactly which imported PowerPoint elements cannot become editable widgets.

    This intentionally returns metadata only: never media bytes or slide text.
    """
    from pptx import Presentation
    validate_pptx_archive(source)
    deck = Presentation(str(source))
    report = {'slide_count': len(deck.slides), 'editable_text_boxes': 0, 'editable_decorative_shapes': 0,
              'unsupported_pictures': 0, 'editable_pictures': 0, 'unsupported_tables': 0,
              'unsupported_charts': 0, 'editable_chart_titles': 0, 'chart_titles_over_page_limit': 0, 'unsupported_other_shapes': 0,
              'editable_table_cells': 0, 'table_cells_over_page_limit': 0,
              'text_boxes_over_page_limit': 0, 'truncated_text_boxes': 0, 'non_16_9_aspect_ratio': False,
              'off_canvas_shapes': 0, 'flattened_groups': 0}
    report['non_16_9_aspect_ratio'] = abs(deck.slide_width / deck.slide_height - 16 / 9) > 0.01
    media_seen = set()
    media_total = 0
    for slide in deck.slides:
        # A group is rendered as editable independent elements, not a native
        # grouping relationship. Explicitly account for that lossy conversion.
        def group_count(shapes):
            from pptx.enum.shapes import MSO_SHAPE_TYPE
            return sum(1 + group_count(item.shapes) for item in shapes
                       if item.shape_type == MSO_SHAPE_TYPE.GROUP)
        report['flattened_groups'] += group_count(slide.shapes)
        retained = 0
        for shape in _flatten_shapes(slide.shapes):
            if (shape.left < 0 or shape.top < 0 or
                    shape.left + shape.width > deck.slide_width or
                    shape.top + shape.height > deck.slide_height):
                report['off_canvas_shapes'] += 1
            from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_AUTO_SHAPE_TYPE
            supported_shape = (shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and
                               shape.auto_shape_type in (MSO_AUTO_SHAPE_TYPE.RECTANGLE,
                                   MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                                   MSO_AUTO_SHAPE_TYPE.OVAL,
                                   MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE))
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    image = shape.image
                    blob, mime = image.blob, image.content_type
                    supported = _supported_image(blob, mime)
                    digest = (hashlib.sha256(blob).hexdigest(), mime) if supported else None
                    within_budget = digest in media_seen or (len(media_seen) < 200 and
                                     media_total + len(blob) <= 50 * 1024 * 1024)
                except (AttributeError, TypeError, ValueError):
                    supported, within_budget = False, False
                if supported and within_budget and retained < 16:
                    report['editable_pictures'] += 1
                    retained += 1
                    if digest not in media_seen:
                        media_seen.add(digest)
                        media_total += len(blob)
                else:
                    report['unsupported_pictures'] += 1
            elif supported_shape or (shape.has_text_frame and shape.text.strip()):
                if shape.has_text_frame and len(shape.text.strip()) > 500:
                    report['truncated_text_boxes'] += 1
                if retained < 16:
                    if supported_shape and not (shape.has_text_frame and shape.text.strip()):
                        report['editable_decorative_shapes'] += 1
                    else:
                        report['editable_text_boxes'] += 1
                    retained += 1
                else:
                    report['text_boxes_over_page_limit'] += 1
            elif shape.has_table:
                # The native table structure, styles and merging are not retained,
                # even when its cell text is imported as editable elements.
                report['unsupported_tables'] += 1
                for row in shape.table.rows:
                    for cell in row.cells:
                        if not cell.text.strip():
                            continue
                        if retained < 16:
                            report['editable_table_cells'] += 1
                            retained += 1
                        else:
                            report['table_cells_over_page_limit'] += 1
            elif shape.has_chart:
                # Native data series are always lossy. The title can be recovered
                # as editable text when the page still has capacity.
                report['unsupported_charts'] += 1
                try:
                    has_title = shape.chart.has_title and bool(shape.chart.chart_title.text_frame.text.strip())
                except (AttributeError, ValueError):
                    has_title = False
                if has_title:
                    if retained < 16:
                        retained += 1
                        report['editable_chart_titles'] += 1
                    else:
                        report['chart_titles_over_page_limit'] += 1
            else:
                report['unsupported_other_shapes'] += 1
    report['lossy'] = any(report[k] for k in (
        'unsupported_pictures', 'unsupported_tables', 'unsupported_charts',
        'unsupported_other_shapes', 'text_boxes_over_page_limit', 'table_cells_over_page_limit', 'flattened_groups',
        'non_16_9_aspect_ratio', 'off_canvas_shapes', 'truncated_text_boxes'))
    return report


def portable_to_pptx(data, destination, media_dir=None):
    from pptx import Presentation
    from pptx.util import Inches
    if data.get('format') != 'quorivio-session' or data.get('version') != 1:
        raise ValueError('Not a Quorivio session definition')
    activities = data.get('activities')
    if not isinstance(activities, list) or len(activities) > 200:
        raise ValueError('Invalid page count')
    p = Presentation()
    p.slide_width, p.slide_height = Inches(13.333), Inches(7.5)
    for activity in activities:
        slide = p.slides.add_slide(p.slide_layouts[6])
        widgets = (activity.get('page_design') or {}).get('widgets') or []
        if len(widgets) > 16:
            raise ValueError('Too many widgets')
        for widget in widgets:
            if widget.get('kind') not in ('text', 'postit', 'question', 'timed-quiz', 'image', 'logo'):
                continue
            position = widget.get('position') or {'x': 5, 'y': 5, 'width': 90, 'height': 20}
            x, y, w, h = (float(position.get(k, v)) for k, v in [('x', 5), ('y', 5), ('width', 90), ('height', 20)])
            if not all(math.isfinite(v) for v in (x, y, w, h)) or x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > 100 or y+h > 100:
                raise ValueError('Invalid widget geometry')
            if widget.get('kind') in ('image', 'logo'):
                asset_id = widget.get('assetId')
                try:
                    valid_asset_id = isinstance(asset_id, str) and str(uuid.UUID(asset_id)) == asset_id and uuid.UUID(asset_id).version == 4
                except (ValueError, AttributeError, TypeError):
                    valid_asset_id = False
                if not valid_asset_id:
                    raise ValueError('Invalid image asset ID')
                if media_dir is None:
                    raise ValueError('Image export requires a private media directory')
                picture_path = Path(media_dir) / asset_id
                if (Path(media_dir).is_symlink() or picture_path.is_symlink() or
                        not picture_path.is_file() or picture_path.stat().st_size > 10 * 1024 * 1024):
                    raise ValueError('Missing or oversized image asset')
                blob = picture_path.read_bytes()
                if not (_supported_image(blob, 'image/png') or _supported_image(blob, 'image/jpeg')):
                    raise ValueError('Unsupported or invalid image asset')
                from pptx.enum.shapes import MSO_SHAPE_TYPE
                shape = slide.shapes.add_picture(str(picture_path), int(p.slide_width*x/100),
                                                 int(p.slide_height*y/100), int(p.slide_width*w/100),
                                                 int(p.slide_height*h/100))
                rotation = position.get('rotation', 0)
                if isinstance(rotation, (int, float)) and math.isfinite(rotation):
                    shape.rotation = rotation % 360
                continue
            if widget.get('kind') == 'postit':
                from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
                style = widget.get('style') or {}
                box = slide.shapes.add_shape(
                    ({'ellipse': MSO_AUTO_SHAPE_TYPE.OVAL, 'triangle': MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE}.get(style.get('shapeType'))
                     or (MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if style.get('rounded') is True else MSO_AUTO_SHAPE_TYPE.RECTANGLE)),
                    int(p.slide_width*x/100), int(p.slide_height*y/100),
                    int(p.slide_width*w/100), int(p.slide_height*h/100))
            else:
                box = slide.shapes.add_textbox(int(p.slide_width*x/100), int(p.slide_height*y/100),
                    int(p.slide_width*w/100), int(p.slide_height*h/100))
            content = str(widget.get('label') or '')
            # Imports keep the short UI label and a longer editable description.
            # Export the full text once, instead of repeating the truncated label.
            description = widget.get('description')
            if widget.get('kind') in ('text', 'postit') and isinstance(description, str) and description.startswith(content):
                content = description
            if widget.get('kind') in ('question', 'timed-quiz'):
                content += '\n' + '\n'.join(str(o.get('label', '')) for o in widget.get('options', [])[:12])
            elif widget.get('description') and widget.get('description') != content and widget.get('kind') not in ('text', 'postit'):
                content += '\n' + str(widget['description'])
            box.text = content[:6000]
            if widget.get('kind') == 'postit' and isinstance(widget.get('style'), dict):
                from pptx.dml.color import RGBColor
                colors = widget['style']
                for key, target in (('fillColor', 'fill'), ('strokeColor', 'line')):
                    value = colors.get(key)
                    if isinstance(value, str) and len(value) == 7 and value.startswith('#'):
                        try:
                            rgb = RGBColor.from_string(value[1:])
                            if target == 'fill':
                                box.fill.solid()
                                box.fill.fore_color.rgb = rgb
                            else:
                                box.line.color.rgb = rgb
                        except ValueError:
                            pass
            rotation = position.get('rotation', 0)
            if isinstance(rotation, (int, float)) and math.isfinite(rotation):
                box.rotation = rotation % 360
            style = widget.get('style') or {}
            if isinstance(style, dict):
                from pptx.util import Pt
                from pptx.dml.color import RGBColor
                for paragraph in box.text_frame.paragraphs:
                    for run in paragraph.runs:
                        font = run.font
                        if isinstance(style.get('fontFamily'), str) and style['fontFamily']:
                            font.name = style['fontFamily'][:80]
                        size = style.get('fontSize')
                        if isinstance(size, (int, float)) and math.isfinite(size):
                            font.size = Pt(max(10, min(96, size)))
                        if isinstance(style.get('bold'), bool): font.bold = style['bold']
                        if isinstance(style.get('italic'), bool): font.italic = style['italic']
                        if isinstance(style.get('underline'), bool): font.underline = style['underline']
                        color = style.get('color')
                        if isinstance(color, str) and len(color) == 7 and color.startswith('#'):
                            try: font.color.rgb = RGBColor.from_string(color[1:])
                            except ValueError: pass
    p.save(str(destination))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for command in ('import', 'export'):
        action = sub.add_parser(command)
        action.add_argument('source')
        action.add_argument('destination')
    args = parser.parse_args()
    if args.operation == 'import':
        Path(args.destination).write_text(json.dumps(pptx_to_portable(args.source), ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        portable_to_pptx(json.loads(Path(args.source).read_text(encoding='utf-8')), args.destination)


if __name__ == '__main__':
    main()
