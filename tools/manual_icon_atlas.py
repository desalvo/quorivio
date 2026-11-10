#!/usr/bin/env python3
"""Produce verifiable annotated editor-toolbar views from archived real Chromium captures.

The toolbar is a crop of a SHA-256-verified RC291 app screenshot, not a redraw.
The teaching legend is an editorial annotation; its location may differ in other builds.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'docs/assets/manual-illustrations'
SCREEN=ROOT/'docs/assets/manual-evidence-rc291/editor-canvas.png'
FONTS=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
FONTS_BOLD=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
FONT=lambda size,bold=False:ImageFont.truetype(FONTS_BOLD[0] if bold else FONTS[0],size)
BG='#f5f8fb';INK='#101f38';MUTED='#52657b';NAVY='#11233f';ACC='#19a99b'
NAMES=[
 ('Gradimento','Rating','Voto numerico 0–9','Numeric rating 0–9'),
 ('Reazioni','Reactions','Reazioni del pubblico','Audience reactions'),
 ('Testo','Text','Testo libero','Free text'),
 ('Forme','Shapes','Forme geometriche','Geometric shapes'),
 ('Linee','Lines','Linee e frecce','Lines and arrows'),
 ('Timer','Timer','Conto alla rovescia','Countdown'),
 ('Codice QR','QR code','Ingresso alla sessione','Session access'),
 ('Profilo','Presenter','Dati del relatore','Speaker profile'),
 ('Sondaggio','Poll','Domanda con opzioni','Choice question'),
 ('Nota','Sticky note','Nota visiva','Visual note'),
 ('Immagine','Image','Foto e illustrazioni','Pictures and illustrations'),
 ('Video','Video','Media video','Video media'),
 ('Logo','Logo','Logo autorizzato','Approved logo'),
 ('PDF','PDF','Documento inserito','Embedded document'),
 ('Domanda libera','Open question','Testo del partecipante','Participant text'),
 ('Quiz a tempo','Timed quiz','Domanda con tempo','Timed question'),
 ('Risultati','Results','Grafici e conteggi','Charts and counts'),
 ('Partecipanti','Participants','Contatore collegati','Connected count'),
 ('Titolo','Title','Titolo della pagina','Page title'),
 ('Footer','Footer','Piè di pagina e numero','Footer and page number'),
]

def make(lang):
 src=Image.open(SCREEN).convert('RGB')
 out=Image.new('RGB',(1660,1320),BG);d=ImageDraw.Draw(out)
 d.rounded_rectangle((22,20,1638,1300),radius=26,fill='white',outline='#cbdbe7',width=2)
 name='ATLANTE DELLA BARRA WIDGET' if lang=='it' else 'EDITOR WIDGET TOOLBAR ATLAS'
 d.text((66,48),name,fill=INK,font=FONT(47,True))
 s=('Icone estratte da una schermata autentica RC291; legenda esplicativa, non nuovo screenshot.' if lang=='it' else
     'Icons cropped from a verified RC291 app capture; explanatory legend, not a new screenshot.')
 d.text((70,115),s,fill=MUTED,font=FONT(19))
 crop=src.crop((156,66,1248,128)).resize((1528,87),Image.Resampling.LANCZOS)
 out.paste(crop,(66,163))
 d.rounded_rectangle((64,160,1596,253),radius=12,outline=ACC,width=3)
 item_w=385;item_h=182;top=289
 for i,(it,en,descr_it,descr_en) in enumerate(NAMES):
  col=i%4;row=i//4;x=65+col*385;y=top+row*187
  d.rounded_rectangle((x,y,x+370,y+174),radius=17,fill='#f3f7fb',outline='#d8e5ed',width=2)
  d.rounded_rectangle((x+14,y+21,x+73,y+80),radius=14,fill=NAVY)
  # True toolbar crop; each original tile width ~54 px and starts at x160
  ox=158+i*54; icon=src.crop((ox,71,min(ox+54,src.width),125))
  if icon.width==54:
   icon=icon.resize((50,50),Image.Resampling.LANCZOS);out.paste(icon,(x+18,y+25))
  else:d.text((x+29,y+28),str(i+1),font=FONT(21,True),fill='white')
  name=it if lang=='it' else en;descr=descr_it if lang=='it' else descr_en
  d.text((x+89,y+26),f'{i+1:02d}  {name}',fill=INK,font=FONT(23,True))
  d.text((x+88,y+79),descr,fill=MUTED,font=FONT(18))
  d.line((x+17,y+121,x+352,y+121),fill='#dbe6ee',width=2)
  d.text((x+22,y+137),('Apri e configura nel canvas' if lang=='it' else 'Place and configure on canvas'),font=FONT(15),fill='#42657c')
 note='Attenzione: lo schema applicato e la modalità smartphone possono modificare il risultato finale.' if lang=='it' else 'Note: master styles and smartphone mode may alter the final layout.'
 d.text((68,1267),note,font=FONT(17),fill=MUTED)
 out.save(ASSETS/f'editor-toolbar-atlas-{lang}-rc293.png',optimize=True)
 print('Wrote',lang)
if __name__=='__main__':
 for lang in ('it','en'):make(lang)
