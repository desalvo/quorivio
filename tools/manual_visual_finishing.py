#!/usr/bin/env python3
"""Editorially finish already rendered manuals without weakening screenshot evidence.

Add an explanatory photo/header and, when a chapter leaves a large unoccupied
area, a contextual reference card with an authentic ARCHIVED screenshot. This
is not used in CI's current-commit screenshot verification and never invents a
new capture or modifies the caption count controlled by the screenshot catalog.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/'docs/assets/manual-evidence-rc291'
ILL=ROOT/'docs/assets/manual-illustrations'
PHOTOGRAPH=ILL/'editorial-live-presentation-rc286.jpg'
COLORS=[(0.06,0.16,0.27),(0.08,0.55,0.52),(0.34,0.37,0.75)]
PHOTOS={
 'user':['participant-question-smartphone','participant-feedback-smartphone','participant-entry-smartphone','rehearsal-side-by-side-smartphone'],
 'presenter':['editor-canvas','editor-thumbnails-widgets','editor-widget-format','editor-schema','rehearsal-side-by-side','presenter-live'],
 'admin':['admin-server-settings','admin-backups','admin-audit','admin-users','workspace-desktop'],
}
CAPTIONS={
 'it':{'user':('PARTECIPARE','Segui il contenuto mostrato dal relatore; invia la risposta soltanto quando la domanda è aperta.'),
       'presenter':('PROVA VISUALE','Confronta editor, schemi e anteprime prima di iniziare la sessione dal vivo.'),
       'admin':('CONTROLLO OPERATIVO','Verifica permessi, stato del sistema, backup e audit prima della messa in produzione.')},
 'en':{'user':('TAKE PART','Follow the presenter\u2019s current page; submit only while the question is open.'),
       'presenter':('VISUAL ACCEPTANCE','Compare editor, master layout and previews before starting a live session.'),
       'admin':('OPERATIONS CHECK','Review access, service health, backups and audit before production use.')},
}

def crop_jpg(path:Path,w:int,h:int)->bytes:
 img=Image.open(path).convert('RGB')
 image=ImageOps.fit(img,(w,h),method=Image.Resampling.LANCZOS,centering=(0.5,0.42))
 out=BytesIO();image.save(out,'JPEG',quality=81,optimize=True);return out.getvalue()

def contain_jpg(path:Path,w:int,h:int)->bytes:
 image=Image.open(path).convert('RGB')
 target=Image.new('RGB',(w,h),'#13243d')
 image.thumbnail((w-12,h-12),Image.Resampling.LANCZOS)
 target.paste(image,((w-image.width)//2,(h-image.height)//2))
 output=BytesIO();target.save(output,'JPEG',quality=84,optimize=True)
 return output.getvalue()

def finish(pdf_path:Path,role:str,lang:str)->dict:
 doc=fitz.open(pdf_path)
 W,H=doc[0].rect.width,doc[0].rect.height
 header_photo=crop_jpg(PHOTOGRAPH,400,105)
 # Avoid extra file bloat by preparing a single compressed card per source.
 shot={name:contain_jpg(ARCH/(name+'.png'),620,520) for name in PHOTOS[role] if (ARCH/(name+'.png')).exists()}
 overlaid=[]
 for i,page in enumerate(doc):
  if i==0:continue # cover already includes a large visual and factual metadata
  # Repeating visual identity on every reading page, including the TOC.
  page.draw_line((42,43),(W-42,43),color=(.77,.83,.88),width=.4,overlay=True)
  page.insert_text((44,24),'QUORIVIO  /  '+('GUIDA ILLUSTRATA' if lang=='it' else 'ILLUSTRATED GUIDE'),fontname='helv',fontsize=7.8,color=COLORS[0],overlay=True)
  page.insert_image(fitz.Rect(W-152,10,W-45,36),stream=header_photo,keep_proportion=False,overlay=True)
  page.draw_rect(fitz.Rect(W-152,10,W-45,36),color=(.26,.68,.64),width=.75,overlay=True)
  # The content is measured on the original body before adding the card.
  blocks=page.get_text('blocks')
  content=[b[3] for b in blocks if 48<b[1]<H-62 and b[3]<H-62 and str(b[4]).strip()]
  content += [entry['bbox'][3] for entry in page.get_image_info() if entry['bbox'][1]>=45 and entry['bbox'][3]<H-58]
  lowest=max(content) if content else 72
  available=H-73-lowest
  if available<70 or not shot:continue
  if available<113:
   micro=fitz.Rect(45,lowest+8,W-45,H-74)
   page.draw_rect(micro,color=(.14,.53,.56),fill=(.952,.974,.979),width=.8,overlay=True)
   frame=fitz.Rect(micro.x0+5,micro.y0+5,micro.x0+81,micro.y1-5)
   page.insert_image(frame,stream=header_photo,keep_proportion=False,overlay=True)
   title,description=CAPTIONS[lang][role]
   page.insert_text((micro.x0+93,micro.y0+17),title,fontname='hebo',fontsize=9,color=COLORS[0],overlay=True)
   page.insert_textbox(fitz.Rect(micro.x0+93,micro.y0+23,micro.x1-6,micro.y1-5),description,fontname='helv',fontsize=7.5,lineheight=1.2,color=COLORS[0],overlay=True)
   overlaid.append(i+1)
   continue
  name=PHOTOS[role][i%len(PHOTOS[role])]
  if name not in shot:name=next(iter(shot))
  top=lowest+14
  h=min(250,max(104,(available-20)/2 if available>330 else available-18))
  rect=fitz.Rect(45,top,W-45,min(top+h,H-72))
  if rect.height<101:continue
  page.draw_rect(rect,color=(.16,.57,.58),fill=(.954,.974,.983),width=1.0,overlay=True)
  in_rect=fitz.Rect(rect.x0+9,rect.y0+9,rect.x0+min(207,rect.width*.44),rect.y1-9)
  # Archival REAL screenshot with clearly separated explanatory caption.
  page.insert_image(in_rect,stream=shot[name],keep_proportion=False,overlay=True)
  text_x=in_rect.x1+13
  title,description=CAPTIONS[lang][role]
  page.insert_text((text_x,rect.y0+26),title,fontname='hebo',fontsize=10.6,color=COLORS[0],overlay=True)
  callout=('SCHERMATA AUTENTICA ARCHIVIATA · RC291' if lang=='it' else 'VERIFIED ARCHIVED SCREENSHOT · RC291')
  page.insert_text((text_x,rect.y0+42),callout,fontname='helv',fontsize=7,color=(.12,.50,.51),overlay=True)
  desc=fitz.Rect(text_x,rect.y0+54,rect.x1-12,rect.y1-13)
  page.insert_textbox(desc,description,fontname='helv',fontsize=9.0,lineheight=1.32,color=COLORS[0],overlay=True)
  # If chapter end leaves a second large white zone, add an educational
  # photorealistic environmental insert. It is explicitly labelled synthetic.
  remaining=H-74-rect.y1
  if remaining>=115:
   y2=rect.y1+9
   second=fitz.Rect(45,y2,W-45,H-74)
   if second.height>105:
    page.draw_rect(second,color=(.21,.56,.64),fill=(.95,.968,.978),width=.8,overlay=True)
    ph=fitz.Rect(second.x0+9,second.y0+9,second.x0+min(207,second.width*.44),second.y1-9)
    page.insert_image(ph,stream=crop_jpg(PHOTOGRAPH,620,375),keep_proportion=False,overlay=True)
    tx=ph.x1+13
    heading=('EVENTO: COSA VERIFICARE' if lang=='it' else 'EVENT: WHAT TO VERIFY')
    page.insert_text((tx,second.y0+25),heading,fontname='hebo',fontsize=10,color=COLORS[0],overlay=True)
    label=('FOTOGRAFIA ILLUSTRATIVA SINTETICA' if lang=='it' else 'SYNTHETIC EDITORIAL PHOTOGRAPH')
    page.insert_text((tx,second.y0+41),label,fontname='helv',fontsize=6.8,color=(.15,.5,.56),overlay=True)
    expl=('Confronta sempre editor e partecipante in anteprima; prova audio, testi, invio e rete prima di usare il sistema con il pubblico.' if lang=='it' else 'Compare editor and audience views; test audio, text, submission and connectivity before your live event.')
    page.insert_textbox(fitz.Rect(tx,second.y0+55,second.x1-12,second.y1-13),expl,fontname='helv',fontsize=8.8,lineheight=1.32,color=COLORS[0],overlay=True)
  overlaid.append(i+1)
 tmp=pdf_path.with_suffix('.visually-verified.pdf')
 doc.save(tmp,garbage=3,deflate=True)
 doc.close();tmp.replace(pdf_path)
 return {'pages_with_context_cards':overlaid,'pages_total':len(fitz.open(pdf_path))}
