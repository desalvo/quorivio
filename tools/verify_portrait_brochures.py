#!/usr/bin/env python3
"""Fail-closed visual/content contracts for six-page Quorivio brochures."""
from pathlib import Path
import argparse
import fitz

REQUIRED={
 'it':('Presenta,','Una sessione Quorivio','Widget potenti per','Percentuale di risposte','Per ogni tipo di evento','Condividi, esporta e riutilizza'),
 'en':('Present,','A Quorivio session','Powerful widgets for','Response participation','For every event format','Share, export and reuse')
}

def verify(folder:Path):
    for lang in ('it','en'):
        file=folder/f'quorivio-brochure-{lang}.pdf'
        if not file.is_file() or file.stat().st_size<30_000:raise ValueError(f'{lang}: brochure missing/empty')
        with fitz.open(file) as doc:
            if doc.page_count!=6:raise ValueError(f'{lang}: expected 6 pages')
            all_text=[]
            for idx,p in enumerate(doc):
                if not (594.9<p.rect.width<595.5 and 841.5<p.rect.height<842.3):raise ValueError(f'{lang} p{idx+1}: non-A4 portrait')
                drawings=p.get_drawings();imgs=p.get_image_info()
                if len(drawings)<12 and not imgs:raise ValueError(f'{lang} p{idx+1}: no substantial vector/photographic graphics')
                text=p.get_text()
                if len(text.strip())<110:raise ValueError(f'{lang} p{idx+1}: image-only or insufficient live text')
                if REQUIRED[lang][idx] not in text:raise ValueError(f'{lang} p{idx+1}: wrong mock section')
                all_text.append(text)
                for b in p.get_text('dict')['blocks']:
                    if b['type']!=0:continue
                    for line in b['lines']:
                        for s in line['spans']:
                            a,b_,c,d=s['bbox']
                            if min(a,b_)<-.6 or c>p.rect.width+.6 or d>p.rect.height+.6:
                                raise ValueError(f'{lang} p{idx+1}: clipped: {s["text"]!r}')
            if sum(len(p.get_image_info()) for p in doc)<3:raise ValueError(f'{lang}: not enough photographs')
            combined='\n'.join(all_text)
            for term in ('Quorivio','.quo','EUPL-1.2','github.com/desalvo/quorivio','Alessandro De Salvo'):
                if term not in combined:raise ValueError(f'{lang}: missing {term}')
    print('PASS: two mock-faithful 6-page full-bleed A4 portrait brochures, vector text, no clipping')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);verify(ap.parse_args().folder)
