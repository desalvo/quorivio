#!/usr/bin/env python3
"""Release guard for generated IT/EN searchable A4 portrait marketing brochures.

The source photo uses 'contain' only. Check page dimensions, real bitmap evidence,
text block bounds, and build metadata before staging brochures into both Docker images.
"""
from pathlib import Path
import argparse
import fitz


def verify(folder: Path) -> None:
    for lang in ('it','en'):
        file=folder/f'quorivio-brochure-{lang}.pdf'
        if not file.is_file() or file.stat().st_size < 20_000:
            raise ValueError(f'Missing {lang} PDF brochure')
        with fitz.open(file) as pdf:
            if len(pdf) != 6:
                raise ValueError(f'{lang}: expected 6 pages, got {len(pdf)}')
            combined=[]
            for i,page in enumerate(pdf,1):
                width,height=page.rect.width,page.rect.height
                if not (590 <= width <= 597 and 840 <= height <= 845 and height > width):
                    raise ValueError(f'{lang} page {i}: not A4 portrait')
                if not page.get_image_info():
                    raise ValueError(f'{lang} page {i}: no illustrative or UI image')
                text=page.get_text()
                if len(text.strip()) < 110:
                    raise ValueError(f'{lang} page {i}: insufficient searchable text')
                combined.append(text)
                for block in page.get_text('dict')['blocks']:
                    if block['type'] != 0:
                        continue
                    for line in block['lines']:
                        for span in line['spans']:
                            x0,y0,x1,y1=span['bbox']
                            if (x0 < -.6 or y0 < -.6 or x1 > width+.6 or y1 > height+.6):
                                raise ValueError(f'{lang} page {i}: clipped text')
            source='\n'.join(combined)
            for required in ('Quorivio','.quo','EUPL-1.2','github.com/desalvo/quorivio'):
                if required not in source:
                    raise ValueError(f'{lang}: missing {required}')
    print('PASS: bilingual six-page A4 portrait PDF brochures, searchable and in-bounds')


if __name__ == '__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('folder',type=Path)
    verify(cli.parse_args().folder)
