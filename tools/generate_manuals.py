#!/usr/bin/env python3
"""Quorivio RC282 manual publication pipeline.

Six role-specific bilingual Markdown sources are the editorial source of truth.
This renders their tables, diagrams and labelled illustrative UI captures into
PDFs in *both* published locations. Run only on a controlled authoring host:
    python3 tools/manual_visual_assets.py
    python3 tools/generate_manuals.py

Requires mistune 3, WeasyPrint, and the checked-in visual assets. Generating PDFs
is explicit; application startup does not rewrite the documents.
"""
from __future__ import annotations
from pathlib import Path
import html
import re
import shutil
import hashlib
from manual_release_metadata import metadata, validate_release
from manual_screenshot_catalog import gallery

import mistune
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/manuals-src'
OUTPUT = ROOT / 'docs/manuals'
WEB = ROOT / 'apps/web/public/docs/manuals'
ASSETS = ROOT / 'docs/assets'
ROLES = {'user': {'it':'Partecipante','en':'Participant'},
         'presenter':{'it':'Presentatore','en':'Presenter'},
         'admin':{'it':'Amministratore','en':'Administrator'}}

CSS = r'''@page {
    size: A4;
    margin: 17mm 16mm 18mm 16mm;
    @bottom-left { content: 'Quorivio | RC282 documentation'; font-size: 8pt; color: #5b6680; }
    @bottom-right { content: counter(page) ' / ' counter(pages); font-size: 8pt; color: #5b6680; }
}
@page:first { margin: 0; @bottom-left {content:normal} @bottom-right{content:normal} }
html{font-size: 10pt;}body{font-family: 'DejaVu Sans',Arial,sans-serif;color:#1f293b;margin:0;line-height:1.53}
h1,h2,h3{font-family:'DejaVu Sans',Arial,sans-serif;line-height:1.25;color:#1f2854}
h2{font-size:17.5pt;margin:0 0 14pt;break-before:page;border-bottom:2px solid #5f56d9;padding-bottom:8pt}
h3{font-size:11.5pt;color:#5746bc;margin:17pt 0 8pt;break-after:avoid}
h2 + h3{margin-top:11pt}p{margin:0 0 9pt;text-align:left;orphans:2;widows:2}strong{color:#1e2850}
li{margin-bottom:5pt}ul,ol{padding-left:19pt;margin:7pt 0 12pt}li>ul{margin:4pt 0}
table{width:100%;border-collapse:collapse;margin:12pt 0 16pt;table-layout:fixed;break-inside:auto;font-size:8.25pt}
thead{display:table-header-group}tr{break-inside:avoid}th{background:#262a68;color:#fff;text-align:left;font-weight:bold}
th,td{vertical-align:top;padding:7pt 7pt;border:1px solid #dbe0ed;overflow-wrap:anywhere;word-wrap:break-word}
tbody tr:nth-child(even){background:#f5f6fc}tbody tr:nth-child(odd){background:#fff}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:8.4pt;line-height:1.4;background:#f3f5fa;border-left:4px solid #5c50cd;border-radius:3px;padding:12pt;margin:12pt 0 17pt;break-inside:avoid}
code{font-family:'DejaVu Sans Mono',monospace;font-size:0.90em;color:#28345f}
a{color:#5446d0;text-decoration:none}
figure{margin:13pt 0 18pt;break-inside:avoid;background:#f7f8fd;border:1px solid #e2e5f0;padding:5pt;border-radius:6pt}
figure img{display:block;max-width:100%;width:100%;height:auto;object-fit:contain}
figcaption{font-size:7.8pt;color:#576278;padding:6pt 5pt 2pt;line-height:1.4}
hr{margin:14pt 0;border:none;border-top:1px solid #ddd}
.cover{break-after:page;height:277mm;position:relative;padding:0;background:#fff}
.cover-head{padding:22mm 17mm 6mm;background:linear-gradient(130deg,#f5f5ff,#fff);border-bottom:4pt solid #604cdc}
.brand{font-weight:900;font-size:24pt;color:#5446ce;letter-spacing:-1pt}
.cover-kicker{color:#5d6b7e;font-size:9pt;margin-top:7mm;text-transform:uppercase;letter-spacing:1.8pt}
.cover-title{font-size:31pt;font-weight:900;color:#22285a;line-height:1.24;margin-top:6mm}
.cover-version{font-size:11pt;color:#4c556c;margin-top:7mm}
.cover-picture{margin:8mm 17mm 0;width:176mm;height:auto;border-radius:7pt}
.cover-foot{margin:10mm 17mm;color:#5b6780;font-size:9pt}
.cover-details{margin:3mm 17mm 0;font-size:8pt;line-height:1.5;color:#34405c;background:#f8f9fe;border:1px solid #eceef8;padding:6pt 9pt;border-radius:4pt}
.cover-brand-logo{vertical-align:middle;width:41mm;max-height:16mm;object-fit:contain;margin:0 5mm 0 0}
.cover-disclaimer{margin:8mm 17mm;padding:9pt 12pt;background:#fdf6e9;color:#7c531a;border-left:4px solid #e3b866;font-size:9pt}
.toc{break-after:page;padding-top:12mm}
.toc h1{font-size:22pt;color:#1d2854}
.toc ul{list-style:none;margin:20pt 0 0;padding:0}
.toc li{padding:2pt 0;margin:0;border-bottom:1px dotted #d3d7e5;font-size:9pt;line-height:1.22}
.toc a{display:block;color:#2b305e}
.toc a::after{content:leader('.') target-counter(attr(href),page);font-size:9pt;color:#79829a}
.content{margin:0}
.content>p:first-of-type{font-size:10pt}
.section-mark{font-size:8pt;color:#6b7280}
'''


def render_one(role: str, lang: str, *, require_real: bool = False) -> tuple[Path,int]:
    source = SOURCE / f'{role}-guide.{lang}.md'
    md = source.read_text(encoding='utf-8')
    meta = metadata()
    validate_release(meta)
    real_gallery = gallery(role, lang, require=require_real, commit=meta['commit'] or None)
    no_live = ('Le schermate autentiche vengono generate dalla CI su un server temporaneo e distribuite come allegato al job; questa edizione locale non contiene immagini non verificate.' if lang == 'it' else 'Authentic screenshots are generated by CI on a disposable server and published as job artifacts; this local edition embeds no unverified images.')
    md = md.replace('<!-- REAL_SCREENSHOT_GALLERY -->', real_gallery if real_gallery else '<p>'+no_live+'</p>')
    title_match = re.search(r'^# (.+)$',md,re.M)
    if not title_match:raise ValueError(f'Missing top title: {source}')
    title=title_match.group(1)
    headings = re.findall(r'^## (.+)$',md,re.M)
    if len(headings)<10:raise ValueError(f'Manual unexpectedly short: {source}')
    img_names=re.findall(r'<img\s+src="([^"]+)"',md)
    for uri in img_names:
        if uri.startswith('http') or not (SOURCE/uri).resolve().is_file():
            raise ValueError(f'Invalid or missing local manual image: {uri}')
    markup=mistune.create_markdown(plugins=['table','strikethrough','task_lists','url'])(md)
    # The separate cover carries title and build metadata; avoid duplicate mastheads.
    markup=re.sub(r'^<h1>.*?</h1>\s*','',markup,count=1,flags=re.S)
    anchors=[]
    def anchor(m):
        index=len(anchors)+1
        anchors.append((f'chapter-{index}',headings[index-1]))
        return f'<h2 id="chapter-{index}">{m.group(1)}</h2>'
    markup=re.sub(r'<h2>(.*?)</h2>',anchor,markup)
    if len(anchors)!=len(headings):raise ValueError('Heading mismatch')
    # The cover already identifies this guide. Move the Markdown lead-in below
    # chapter 1 so its mandatory chapter page break does not strand a near-empty
    # introductory page between the index and the first chapter.
    first_heading=markup.find('<h2 id="chapter-1">')
    if first_heading>0:
        lead,chapters_markup=markup[:first_heading],markup[first_heading:]
        close=chapters_markup.index('</h2>')+len('</h2>')
        markup=chapters_markup[:close]+lead+chapters_markup[close:]
    toc=''.join(f'<li><a href="#{id}">{html.escape(head)}</a></li>' for id,head in anchors)
    cover_image=(ASSETS/'quorivio-manual-cover.png').as_uri()
    role_label=ROLES[role][lang]
    caption=('FIGURE: ricostruzioni etichettate; screenshot reali solo con prove verificate' if lang=='it' else 'FIGURES: labelled reconstructions; live screenshots only with verified evidence')
    info=('Documentazione tecnica | 9 novembre 2026' if lang=='it' else 'Technical documentation | 9 November 2026')
    subtitle=('Guida operativa illustrata' if lang=='it' else 'Illustrated operational guide')
    toc_title='Indice' if lang=='it' else 'Contents'
    note=('Edizione RC282; certificazioni di sicurezza e infrastrutture reali restano separate.' if lang=='it' else 'RC282 edition; security and real infrastructure certifications remain separate.')
    contact=html.escape(meta['author'])
    platform=('Server Linux amd64/arm64 (Docker, Podman, Kubernetes). Client via browser su Windows, macOS, Linux, iOS e Android.' if lang=='it' else 'Linux amd64/arm64 server (Docker, Podman, Kubernetes). Web clients on Windows, macOS, Linux, iOS and Android.')
    minimum=('Minimo indicativo per valutazione: 2 vCPU, 4 GiB RAM, 20 GiB disco oltre ai dati persistenti; dimensionare la produzione con misure.' if lang=='it' else 'Indicative evaluation minimum: 2 vCPU, 4 GiB RAM, 20 GiB disk plus persistent data; benchmark production sizing.')
    brand_logo=(ASSETS/'quorivio-logo.svg').as_uri()
    details=(f'<strong>{html.escape(meta["name"])} · {html.escape(meta["version"])} · Build {html.escape(meta["build"])}</strong>'
      f'<div>{contact} · <a href="mailto:{html.escape(meta["email"])}">{html.escape(meta["email"])}</a></div>'
      f'<div>{html.escape(meta["published"])} · {html.escape(meta["license"])} · <a href="{html.escape(meta["repository"])}">{html.escape(meta["repository"])}</a></div>'
      f'<div>{html.escape(platform)}</div><div>{html.escape(minimum)}</div>')
    document=f'''<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{html.escape(title)} | Quorivio</title><style>{CSS}</style></head><body>
    <section class="cover"><div class="cover-head"><div class="brand"><img class="cover-brand-logo" src="{brand_logo}" alt="Logo ufficiale Quorivio"/> Quorivio</div><div class="cover-kicker">{html.escape(subtitle)} · {html.escape(role_label)}</div><div class="cover-title">{html.escape(title)}</div><div class="cover-version">{html.escape(meta['version'])} • {html.escape(meta['build'])} • {info}</div></div>
    <img class="cover-picture" src="{cover_image}" alt="Quorivio event illustration"/>
    <div class="cover-details">{details}</div><div class="cover-disclaimer">{caption}<br>{note}</div></section>
    <section class="toc"><h1>{toc_title}</h1><p>{len(anchors)} {"capitoli" if lang=='it' else 'chapters'} · {"Edizione" if lang=='it' else 'Edition'} RC282</p><ul>{toc}</ul></section>
    <main class="content">{markup}</main></body></html>'''
    OUTPUT.mkdir(parents=True,exist_ok=True)
    dest=OUTPUT/f'{role}-guide.{lang}.pdf'
    HTML(string=document,base_url=str(SOURCE)).write_pdf(dest)
    WEB.mkdir(parents=True,exist_ok=True)
    shutil.copy2(dest,WEB/dest.name)
    if hashlib.sha256(dest.read_bytes()).digest()!=hashlib.sha256((WEB/dest.name).read_bytes()).digest():
        raise ValueError('Published PDF mismatch')
    return dest,len(anchors)


def main():
    import argparse
    global OUTPUT, WEB
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-real',action='store_true',help='Require verified real screenshots for every manual')
    parser.add_argument('--output-dir',type=Path,help='Write PDF artifacts here rather than mutating the checked-in release')
    args=parser.parse_args()
    if args.output_dir:
        OUTPUT=args.output_dir.resolve()
        WEB=OUTPUT/'public-copies'
    import fitz
    total=0
    for lang in ('it','en'):
        for role in ('user','presenter','admin'):
            dest,chapters=render_one(role,lang,require_real=args.require_real)
            pdf=fitz.open(dest)
            pages=pdf.page_count
            if pages<14 or not any('Quorivio' in p.get_text() for p in pdf):
                raise ValueError('Broken or unexpectedly short PDF: '+str(dest))
            if not any('RC282' in p.get_text() for p in pdf):
                raise ValueError('Missing RC282 build identification: '+str(dest))
            print(dest.name,'chapters',chapters,'pages',pages,'bytes',dest.stat().st_size)
            total+=pages
            pdf.close()
    print('Generated six fully bilingual manuals,',total,'PDF pages total')

if __name__=='__main__':main()
