#!/usr/bin/env python3
"""Six-page portrait Quorivio marketing brochures (IT/EN), with editable searchable text.

ImageGen-derived environmental photography is SYNTHETIC, while screen captures
come from a hash-verified archived CI run. Publication metadata is shared with
all six manuals, and no source-commit identifier is printed on either brochure.
"""
from pathlib import Path
import os
from io import BytesIO
import shutil
from PIL import Image,ImageOps
import cairosvg
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from manual_release_metadata import metadata,validate_release
from manual_screenshot_catalog import evidence,LATEST_ARCHIVED_SCREENSHOTS,LATEST_ARCHIVED_COMMIT
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'docs/assets/brochure-editorial'
SCREEN=ROOT/'docs/assets/manual-evidence-rc291'
OUT=Path(os.environ.get('QUORIVIO_BROCHURE_OUTPUT_DIR',str(ROOT/'docs/brochures'))); WEB=ROOT/'apps/web/public/docs/brochures'
W,H=A4
BLUE='#121f3b';TEAL='#10a99b';PURPLE='#5447ad';MUTED='#4d6078';WHITE='#ffffff';LIGHT='#f0f7f9'
pdfmetrics.registerFont(TTFont('Lato','/usr/share/fonts/truetype/lato/Lato-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LatoBold','/usr/share/fonts/truetype/lato/Lato-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LatoHeavy','/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'))

def color(c,h):
 from reportlab.lib.colors import HexColor
 c.setFillColor(HexColor(h))
def border(c,h):
 from reportlab.lib.colors import HexColor
 c.setStrokeColor(HexColor(h))
def txt(c,x,y,s,size=10,bold=False,ink=BLUE):
 color(c,ink);c.setFont('LatoBold' if bold else 'Lato',size);c.drawString(x,y,s)
def wrap(c,text,x,y,width,size=9.5,leading=13,maxlines=12,ink=BLUE,bold=False):
 ft='LatoBold' if bold else 'Lato';words=text.split();lines=[];line=''
 for w in words:
  s=f'{line} {w}'.strip()
  if pdfmetrics.stringWidth(s,ft,size)>width and line:lines.append(line);line=w
  else:line=s
 if line:lines.append(line)
 c.setFont(ft,size);color(c,ink)
 for s in lines[:maxlines]:c.drawString(x,y,s);y-=leading
 return y

def pill(c,x,y,label,fill=TEAL):
 from reportlab.lib.colors import HexColor
 w=pdfmetrics.stringWidth(label,'LatoBold',8)+20
 color(c,fill);c.roundRect(x,y-5,w,20,10,stroke=0,fill=1)
 txt(c,x+10,y+1,label,8,True,WHITE)
 return w

def panel(c,x,y,w,h,background=WHITE,outline='#d8e7ee',r=13):
 color(c,background);border(c,outline);c.roundRect(x,y,w,h,r,stroke=1,fill=1)

def image_cover(c,path,x,y,w,h):
 im=Image.open(path).convert('RGB');im=ImageOps.fit(im,(round(w*3),round(h*3)),Image.Resampling.LANCZOS)
 b=BytesIO();im.save(b,format='JPEG',quality=87,optimize=True);b.seek(0)
 c.drawImage(ImageReader(b),x,y,w,h,mask='auto')

def image_contain(c,path,x,y,w,h):
 im=Image.open(path).convert('RGB');im.thumbnail((round(w*3),round(h*3)),Image.Resampling.LANCZOS)
 nw,nh=im.size;pw=nw/3;ph=nh/3
 c.drawImage(ImageReader(im),x+(w-pw)/2,y+(h-ph)/2,pw,ph,mask='auto')

def logo_png()->Path:
 out=ART/'official-quorivio-logo.png'
 cairosvg.svg2png(url=str(ROOT/'docs/assets/quorivio-logo.svg'),write_to=str(out),output_width=540)
 return out

def small_icon(c,x,y,kind,colorhex=TEAL):
 border(c,colorhex);c.setLineWidth(2)
 if kind=='chart':
  for j,h in enumerate((11,22,15,31)):c.line(x+6+j*8,y+4,x+6+j*8,y+4+h)
 elif kind=='people':
  c.circle(x+14,y+26,5,fill=0,stroke=1);c.circle(x+27,y+26,5,fill=0,stroke=1)
  c.arc(x+4,y+4,x+24,y+24,0,180);c.arc(x+17,y+4,x+37,y+24,0,180)
 elif kind=='screen':
  c.roundRect(x+2,y+8,35,27,4,stroke=1,fill=0);c.line(x+11,y+4,x+30,y+4);c.line(x+20,y+4,x+20,y+8)
 else:
  c.circle(x+20,y+20,14,stroke=1,fill=0);c.line(x+13,y+20,x+18,y+14);c.line(x+18,y+14,x+29,y+28)

def label_list(c,x,y,items,size=9,lead=17,ink=BLUE):
 for item in items:
  color(c,TEAL);c.circle(x+4,y+3,3,stroke=0,fill=1)
  wrap(c,item,x+14,y,235,size,lead,maxlines=2,ink=ink)
  y-=lead+3
 return y

DATA={
 'it':{'tag':'BROCHURE ILLUSTRATIVA','sub':'Presentazioni interattive, quiz e pubblico protagonista',
  'hero':'Dalla progettazione delle pagine alle risposte in diretta: un solo ambiente per preparare, provare e condurre eventi con partecipanti su smartphone o desktop.',
  'pills':['EDITOR VISUALE','SESSIONI LIVE','OPEN SOURCE'],
  'three':[('Crea', 'Pagine, widget, schemi e anteprime con controlli di formattazione.'),('Coinvolgi','QR e codici sessione; sondaggi, quiz e domande aperte anche da mobile.'),('Analizza','Risultati, grafici e feedback durante la presentazione.')],
  'why':'In presenza, da remoto o ibrido: pubblico sempre protagonista',
  'whytext':'Il pubblico entra con un QR code, risponde a sondaggi e quiz da smartphone, invia domande e segue i risultati in tempo reale mentre il presentatore conduce le slide.',
  'workflow':'DALL’IDEA ALL’EVENTO LIVE',
  'steps':['Crea una sessione','Progetta pagine e schemi','Prova le anteprime','Conduci e raccogli risposte'],
  'features':'FUNZIONI CHE FANNO LA DIFFERENZA',
  'blocks':[('Contenuti e interazione','Testi, immagini, video, QR, titoli, footer, timer, quiz singoli/multipli, domande aperte e gradimento.'),
   ('Risultati e controllo','Grafici a barre, torta, gauge, bolle, tabelle e word cloud, partecipanti connessi, evidenziazione R delle opzioni corrette.'),
   ('Portabilità','Copia di sessione .quo con contenuti, allegati e calendario; import locale che crea una nuova sessione.'),
   ('Coinvolgimento del pubblico','Sondaggi dal vivo, quiz e competizioni, Q&A, reazioni, risultati immediati e percentuale di partecipazione per chi presenta.')],
  'screens':'INTERFACCIA AUTENTICA · ARCHIVIO DI COLLAUDO',
  'tech':'INFRASTRUTTURA E GOVERNANCE',
  'techlines':['In presenza e da remoto, fino a 500 teorici','Linux, Docker, Podman e Kubernetes','GDPR: privacy by design; carico da validare'],
  'meta':'DATI DI PUBBLICAZIONE',
  'min':'Minimo indicativo per una prova: 2 vCPU, 4 GiB RAM e 20 GiB di disco più DB/media; produzione da dimensionare.',
  'note':'Foto ambientali e alcuni mock sono illustrazioni sintetiche. Le schermate dell’app sono immagini vere di una build di prova archiviata; possono variare.',
  'footer':'Quorivio — crea, coinvolgi, misura. Sul tuo server.'},
 'en':{'tag':'ILLUSTRATIVE BROCHURE','sub':'Interactive presentations, quizzes and audience engagement',
  'hero':'From designing slides to receiving live answers: one environment to prepare, rehearse and run events with participants on smartphones or desktops.',
  'pills':['VISUAL EDITOR','LIVE SESSIONS','OPEN SOURCE'],
  'three':[('Create','Pages, widgets, masters and previews with advanced formatting.'),('Engage','QR and session codes; polls, quizzes and open questions on mobile.'),('Understand','Results, charts and feedback during the presentation.')],
  'why':'In person, remotely or hybrid: engage everyone',
  'whytext':'Attendees join with a QR code, answer live polls and quizzes on their phones, submit questions and watch real-time results while the presenter controls the slides.',
  'workflow':'FROM IDEA TO LIVE EVENT',
  'steps':['Create a session','Design pages and masters','Rehearse all previews','Go live and collect answers'],
  'features':'FEATURES THAT MAKE A DIFFERENCE',
  'blocks':[('Content and interaction','Text, images, video, QR, title/footer, timers, single/multiple choice quizzes, open questions and ratings.'),
   ('Results and control','Bars, pies, gauges, bubbles, tables, word clouds, connected participant counts and R-based correct-answer highlighting.'),
   ('Portability','Portable .quo session bundle with content, media and calendar; local import creates a new session.'),
   ('Audience engagement','Live polls, quizzes and competitions, Q&A, reactions, instant charts and response-participation percentage for presenters.')],
  'screens':'AUTHENTIC UI · ARCHIVED TEST BUILD',
  'tech':'INFRASTRUCTURE AND GOVERNANCE',
  'techlines':['In-person and remote; 500 theoretical users','Linux, Docker, Podman and Kubernetes','GDPR-aware; load testing still required'],
  'meta':'PUBLICATION DETAILS',
  'min':'Indicative evaluation minimum: 2 vCPU, 4 GiB RAM and 20 GiB disk plus database/media; size production by measurement.',
  'note':'Environmental photos and some mockups are synthetic illustrations. UI screenshots are genuine captures from an archived test build and may differ.',
  'footer':'Quorivio — create, engage, understand. On your infrastructure.'},
}

def page_footer(c,i,lang):
 color(c,BLUE);c.rect(0,0,W,43,stroke=0,fill=1)
 txt(c,39,18,DATA[lang]['footer'],9.2,True,WHITE)
 txt(c,W-52,18,f'{i}/6',9,True,'#93e4df')

def build_one(lang):
 d=DATA[lang];meta=metadata();validate_release(meta)
 evidence(SCREEN,expected_commit=__import__('manual_screenshot_catalog').LATEST_ARCHIVED_COMMIT,minimum=20)
 OUT.mkdir(parents=True,exist_ok=True)
 if not os.environ.get('QUORIVIO_BROCHURE_NO_WEB'):WEB.mkdir(parents=True,exist_ok=True)
 dest=OUT/('quorivio-brochure-'+lang+'.pdf');c=Canvas(str(dest),pagesize=A4,pageCompression=1)
 c.setTitle('Quorivio | '+('Brochure illustrativa - sei pagine verticali' if lang=='it' else 'Six-page portrait brochure'))
 c.setAuthor(meta['author'])
 logo=logo_png()
 def header(number,section):
  color(c,'#f7fbff');c.rect(0,0,W,H,fill=1,stroke=0)
  color(c,BLUE);c.rect(0,H-78,W,78,stroke=0,fill=1)
  color(c,WHITE);c.roundRect(31,H-64,168,47,9,stroke=0,fill=1)
  c.drawImage(ImageReader(logo),36,H-61,158,42,mask='auto')
  font_size=13
  while pdfmetrics.stringWidth(section,'LatoBold',font_size)>W-252 and font_size>8:font_size-=.5
  txt(c,225,H-43,section,font_size,True,WHITE)
  page_footer(c,number,lang)
 def line(text,x,y,width,size=10,leading=14,bold=False,ink=BLUE,low=50):
  font='LatoBold' if bold else 'Lato'
  chunks=[];part=''
  for word in str(text).split():
   candidate=(part+' '+word).strip()
   if part and pdfmetrics.stringWidth(candidate,font,size)>width:
    chunks.append(part);part=word
   else:part=candidate
  if part:chunks.append(part)
  if y-(len(chunks)-1)*leading<low:raise ValueError('brochure text crosses a card or footer: '+str(text)[:50])
  for chunk in chunks:
   if pdfmetrics.stringWidth(chunk,font,size)>width:raise ValueError('oversized brochure word: '+chunk)
   txt(c,x,y,chunk,size,bold,ink);y-=leading
  return y
 def headline(s,x,y,width,size=19):
  while pdfmetrics.stringWidth(s,'LatoBold',size)>width and size>10:size-=.5
  txt(c,x,y,s,size,True,BLUE)
 def photo_whole(source,x,y,w,h):
  # Contain, never crop. Every source pixel remains visible.
  image_contain(c,source,x,y,w,h)
 # 1: cover, full photograph and real UI screenshot.
 header(1,d['tag'])
 headline(d['sub'],36,718,520,19)
 line(d['hero'],36,684,520,11,16,False,MUTED,620)
 panel(c,36,277,523,319,background=WHITE)
 photo_whole(ART/('marketing-photo-'+lang+'.jpg'),46,286,503,300)
 headline(('Presenta, interagisci, coinvolgi!' if lang=='it' else 'Present. Interact. Engage.'),37,251,519,17)
 line(d['whytext'],38,225,516,9.6,14,False,MUTED,175)
 line(('Slide, QR, sondaggi live, quiz, reazioni, grafici e domande del pubblico.' if lang=='it' else 'Slides, QR, live polls, quizzes, reactions, charts and audience questions.'),38,133,512,9.4,14,True,PURPLE,95)
 line(d['note'],38,91,512,7.8,11,False,MUTED,51)
 c.showPage()
 # 2: product workflow and authentic screenshots.
 header(2,d['workflow'])
 headline(d['workflow'],37,725,520,20)
 for i,step in enumerate(d['steps']):
  y=634-i*94;panel(c,37,y,522,80,background=WHITE)
  color(c,TEAL if i%2==0 else PURPLE);c.circle(62,y+40,14,fill=1,stroke=0)
  txt(c,57,y+36,str(i+1),11,True,WHITE)
  line(step,91,y+45,447,12,16,True,BLUE,y+15)
 headline(d['screens'],38,240,510,12.5)
 panel(c,37,75,520,155,background='#edf4f9')
 photo_whole(SCREEN/'rehearsal-side-by-side.png',48,85,498,135)
 c.showPage()
 # 3: rich widgets and features with actual editor screenshot.
 header(3,d['features'])
 headline(d['features'],38,726,515,19)
 for i,(title,body) in enumerate(d['blocks']):
  x=37+(i%2)*266;y=427-(i//2)*216
  panel(c,x,y,257,203,background=WHITE)
  color(c,TEAL if i%2==0 else PURPLE);c.roundRect(x+12,y+156,31,30,7,fill=1,stroke=0)
  txt(c,x+23,y+166,str(i+1),11,True,WHITE)
  headline(title,x+12,y+132,231,12.5)
  line(body,x+12,y+112,231,10,15,False,MUTED,y+47)
  small_icon(c,x+13,y+13,['screen','chart','screen','people'][i])
 panel(c,37,75,520,122,background='#ebf6f3')
 photo_whole(SCREEN/'editor-canvas.png',49,83,496,105)
 c.showPage()
 # 4: live audience and participant device evidence.
 header(4,d['why'])
 headline(d['why'],37,726,517,17)
 line(d['whytext'],38,698,510,10,14,False,MUTED,643)
 panel(c,37,388,520,240,background=WHITE)
 photo_whole(SCREEN/'participant-question-smartphone.png',48,399,250,219)
 photo_whole(SCREEN/'presenter-live.png',307,399,240,219)
 for i,(title,summary) in enumerate(d['three']):
  y=305-i*78;panel(c,37,y,520,67,background=WHITE)
  headline(title,51,y+43,493,13)
  line(summary,51,y+21,490,9.4,12,False,MUTED,y+8)
 c.showPage()
 # 5: technical and infrastructure facts.
 header(5,d['tech'])
 headline(d['tech'],38,726,519,19)
 for i,content in enumerate(d['techlines']):
  y=612-i*101;panel(c,37,y,520,88,background=WHITE)
  color(c,TEAL);c.circle(58,y+47,9,stroke=0,fill=1)
  line(content,79,y+51,457,11.3,16,True,BLUE,y+15)
 panel(c,37,178,520,107,background='#edf8f6')
 headline(d['why'],52,255,484,13)
 line(d['min'],52,226,486,9.6,14,False,MUTED,186)
 panel(c,37,75,520,92,background=WHITE)
 photo_whole(SCREEN/'editor-canvas.png',45,83,505,75)
 c.showPage()
 # 6: features and publication metadata.
 header(6,d['meta'])
 headline(d['meta'],38,727,517,19)
 for i,(title,body) in enumerate(d['three']):
  y=622-i*88;panel(c,38,y,519,77,background=WHITE)
  headline(title,51,y+49,485,13.5)
  line(body,51,y+26,484,9.6,13,False,MUTED,y+10)
 panel(c,38,200,519,139,background='#edf8f6')
 txt(c,53,310,'Version: '+meta['version']+'  •  '+meta['build'],10.2,True)
 txt(c,53,287,('Autore: ' if lang=='it' else 'Author: ')+meta['author'],10.2)
 txt(c,53,264,meta['email'],10.2)
 txt(c,53,241,'License: '+meta['license']+'  •  github.com/desalvo/quorivio',9.9)
 line(d['note'],52,177,493,8.5,12,False,MUTED,129)
 txt(c,53,95,'PDF  •  PPTX  •  .quo  •  PostgreSQL  •  Docker  •  Kubernetes',9.5,True)
 c.showPage();c.save()
 if not os.environ.get('QUORIVIO_BROCHURE_NO_WEB'):shutil.copy2(dest,WEB/dest.name)
 print(dest.name,'bytes',dest.stat().st_size)
 return dest

if __name__=='__main__':
 for lang in ('it','en'):build_one(lang)