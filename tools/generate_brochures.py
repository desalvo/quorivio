#!/usr/bin/env python3
"""Two-page Quorivio marketing brochures (IT/EN), with editable searchable text.

ImageGen-derived environmental photography is SYNTHETIC, while screen captures
come from a hash-verified archived CI run. Publication metadata is shared with
all six manuals, and no source-commit identifier is printed on either brochure.
"""
from pathlib import Path
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
OUT=ROOT/'docs/brochures'; WEB=ROOT/'apps/web/public/docs/brochures'
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
 'it':{'tag':'BROCHURE DI PRODOTTO','sub':'Presentazioni interattive, quiz e pubblico protagonista',
  'hero':'Dalla progettazione delle pagine alle risposte in diretta: un solo ambiente per preparare, provare e condurre eventi con partecipanti su smartphone o desktop.',
  'pills':['EDITOR VISUALE','SESSIONI LIVE','OPEN SOURCE'],
  'three':[('Crea', 'Pagine, widget, schemi e anteprime con controlli di formattazione.'),('Coinvolgi','QR e codici sessione; sondaggi, quiz e domande aperte.'),('Analizza','Risultati, grafici e feedback durante la presentazione.')],
  'why':'Dall’aula alla conferenza: rendi il pubblico parte attiva',
  'whytext':'Presentatore, partecipante e amministratore hanno viste dedicate. Il sistema può essere installato e gestito sulla propria infrastruttura, con accessi autorizzati e strumenti di audit.',
  'workflow':'DALL’IDEA ALL’EVENTO LIVE',
  'steps':['Crea una sessione','Progetta pagine e schemi','Prova le anteprime','Conduci e raccogli risposte'],
  'features':'FUNZIONI CHE FANNO LA DIFFERENZA',
  'blocks':[('Contenuti e interazione','Testi, immagini, video, QR, titoli, footer, timer, quiz singoli/multipli, domande aperte e gradimento.'),
   ('Risultati e controllo','Grafici a barre e torta, word cloud, partecipanti connessi, evidenziazione R delle opzioni corrette.'),
   ('Portabilità','Copia di sessione .quo con contenuti, allegati e calendario; import locale che crea una nuova sessione.'),
   ('Amministrazione','Utenti e ruoli, LDAP/SSO, ClamAV, backup, restore, audit, scaling e scenari DR documentati.')],
  'screens':'INTERFACCIA AUTENTICA · ARCHIVIO DI COLLAUDO',
  'tech':'INFRASTRUTTURA E GOVERNANCE',
  'techlines':['Server Linux, Docker, Podman e Kubernetes','PostgreSQL 18; ingress NGINX o HAProxy','GDPR: strumenti privacy by design, non certificazione automatica'],
  'meta':'DATI DI PUBBLICAZIONE',
  'min':'Minimo indicativo per una prova: 2 vCPU, 4 GiB RAM e 20 GiB di disco più DB/media; produzione da dimensionare.',
  'note':'Foto ambientali e alcuni mock sono illustrazioni sintetiche. Le schermate dell’app sono immagini vere di una build di prova archiviata; possono variare.',
  'footer':'Quorivio — crea, coinvolgi, misura. Sul tuo server.'},
 'en':{'tag':'PRODUCT BROCHURE','sub':'Interactive presentations, quizzes and audience engagement',
  'hero':'From designing slides to receiving live answers: one environment to prepare, rehearse and run events with participants on smartphones or desktops.',
  'pills':['VISUAL EDITOR','LIVE SESSIONS','OPEN SOURCE'],
  'three':[('Create','Pages, widgets, masters and previews with advanced formatting.'),('Engage','QR and session codes; polls, quizzes and open questions.'),('Understand','Results, charts and feedback during the presentation.')],
  'why':'From classrooms to conferences: let your audience take part',
  'whytext':'Presenters, participants and administrators have dedicated views. Deploy on infrastructure you manage, with authorised access and auditing tools.',
  'workflow':'FROM IDEA TO LIVE EVENT',
  'steps':['Create a session','Design pages and masters','Rehearse all previews','Go live and collect answers'],
  'features':'FEATURES THAT MAKE A DIFFERENCE',
  'blocks':[('Content and interaction','Text, images, video, QR, title/footer, timers, single/multiple choice quizzes, open questions and ratings.'),
   ('Results and control','Bar/pie charts, word clouds, connected participant counts and R-based correct-answer highlighting.'),
   ('Portability','Portable .quo session bundle with content, media and calendar; local import creates a new session.'),
   ('Administration','Users and roles, LDAP/SSO, ClamAV, backups, restore, audit, scaling and documented DR workflows.')],
  'screens':'AUTHENTIC UI · ARCHIVED TEST BUILD',
  'tech':'INFRASTRUCTURE AND GOVERNANCE',
  'techlines':['Linux server, Docker, Podman and Kubernetes','PostgreSQL 18; NGINX or HAProxy ingress','GDPR-oriented privacy tools; no automatic certification'],
  'meta':'PUBLICATION DETAILS',
  'min':'Indicative evaluation minimum: 2 vCPU, 4 GiB RAM and 20 GiB disk plus database/media; size production by measurement.',
  'note':'Environmental photos and some mockups are synthetic illustrations. UI screenshots are genuine captures from an archived test build and may differ.',
  'footer':'Quorivio — create, engage, understand. On your infrastructure.'},
}

def page_footer(c,i,lang):
 color(c,BLUE);c.rect(0,0,W,43,stroke=0,fill=1)
 txt(c,39,18,DATA[lang]['footer'],9.2,True,WHITE)
 txt(c,W-52,18,f'{i}/2',9,True,'#93e4df')

def build_one(lang):
 d=DATA[lang];meta=metadata();validate_release(meta)
 evidence(SCREEN,expected_commit=__import__('manual_screenshot_catalog').LATEST_ARCHIVED_COMMIT,minimum=20)
 OUT.mkdir(parents=True,exist_ok=True);WEB.mkdir(parents=True,exist_ok=True)
 dest=OUT/('quorivio-brochure-'+lang+'.pdf');c=Canvas(str(dest),pagesize=A4,pageCompression=1)
 c.setTitle('Quorivio | '+('Brochure del prodotto' if lang=='it' else 'Product brochure'))
 c.setAuthor(meta['author'])
 # Page 1 - premium hero with photo + genuine product screenshot.
 color(c,'#f7fbff');c.rect(0,0,W,H,fill=1,stroke=0)
 color(c,BLUE);c.roundRect(0,733,W,109,19,fill=1,stroke=0)
 color(c,WHITE);c.roundRect(36,753,189,55,13,stroke=0,fill=1)
 c.drawImage(ImageReader(logo_png()),40,758,176,45,mask='auto')
 txt(c,41,742,d['tag']+'  •  '+meta['build'],8,True,'#a5e9e3')
 pill(c,418,777,d['pills'][0]);pill(c,418,748,d['pills'][2],fill=PURPLE)
 txt(c,40,691,'QUORIVIO',32,True)
 y=wrap(c,d['sub'],40,662,265,20,25,3,ink=BLUE,bold=True)
 y-=6
 wrap(c,d['hero'],40,y,260,11.3,16,7,ink=MUTED)
 image_cover(c,ART/('marketing-photo-'+lang+'.jpg'),321,499,232,218)
 border(c,TEAL);c.setLineWidth(2);c.roundRect(320,498,234,220,14,fill=0,stroke=1)
 # Three product evidence cards.
 cards=[('editor-canvas','screen'),('participant-question-smartphone','people'),('presenter-live','chart')]
 for n,((title,copy),(img,kind)) in enumerate(zip(d['three'],cards)):
  x=40+n*176
  panel(c,x,300,162,179)
  color(c,'#e9f5f5');c.roundRect(x+8,379,146,92,8,stroke=0,fill=1)
  image_contain(c,SCREEN/(img+'.png'),x+10,382,142,85)
  small_icon(c,x+12,341,kind)
  txt(c,x+55,360,title,13,True)
  wrap(c,copy,x+14,331,136,8.9,12,5,ink=MUTED)
 # Dovetailed aspirational band.
 panel(c,40,139,514,145,background='#e8f5f3',outline='#c9e6e2')
 txt(c,57,255,d['why'],13.2,True)
 wrap(c,d['whytext'],57,235,295,9.6,14,8)
 image_cover(c,ROOT/'docs/assets/manual-illustrations/editorial-collaborative-workflow-rc286.jpg',393,153,144,110)
 pill(c,56,161,d['pills'][1])
 txt(c,45,98,d['note'],7.7,False,ink=MUTED) if len(d['note'])<100 else wrap(c,d['note'],45,104,505,7.5,10,3,ink=MUTED)
 page_footer(c,1,lang);c.showPage()
 # Page 2 - functions, workflow and real screenshots.
 color(c,'#f7fafc');c.rect(0,0,W,H,stroke=0,fill=1)
 color(c,BLUE);c.roundRect(0,758,W,84,17,fill=1,stroke=0)
 txt(c,40,790,d['workflow'],18,True,WHITE)
 txt(c,40,771,meta['name']+'  •  '+meta['version']+'  •  '+meta['build'],8.5,False,'#bcf5ea')
 for k,name in enumerate(d['steps']):
  x=40+k*133
  panel(c,x,694,124,52,background='#edf8f7',outline='#bfdbda')
  color(c,TEAL);c.circle(x+15,720,11,stroke=0,fill=1)
  txt(c,x+12,716,str(k+1),9.2,True,WHITE)
  wrap(c,name,x+30,722,88,9,11,3,ink=BLUE,bold=True)
  if k<3:
   border(c,TEAL);c.setLineWidth(1.7);c.line(x+124,722,x+131,722)
 txt(c,43,673,d['features'],15.5,True)
 for k,(head,copy) in enumerate(d['blocks']):
  col=k%2;row=k//2;x=40+col*262;y=522-row*122
  panel(c,x,y,250,113)
  color(c,TEAL);c.roundRect(x+12,y+77,33,27,8,stroke=0,fill=1)
  txt(c,x+23,y+87,str(k+1),12,True,WHITE)
  txt(c,x+55,y+86,head,11.6,True)
  wrap(c,copy,x+13,y+65,223,8.7,12,5,ink=MUTED)
  color(c,'#ecf7f7');c.roundRect(x+13,y+11,223,29,6,stroke=0,fill=1)
  small_icon(c,x+18,y+8,['screen','chart','screen','people'][k])
  txt(c,x+57,y+20,['EDITOR  •  WIDGET','LIVE  •  REPORT','SESSION  .quo','SECURITY  •  OPS'][k],8,True,ink=PURPLE)
 # lower divided section: true screenshot and facts.
 txt(c,43,372,d['screens'],10,True,ink=PURPLE)
 panel(c,40,238,253,127,background='#eef4f7')
 image_contain(c,SCREEN/'rehearsal-side-by-side.png',47,246,238,111)
 txt(c,308,365,d['tech'],10.6,True)
 label_list(c,311,347,d['techlines'],7.8,16)
 panel(c,40,80,514,143,background='#edf8f6',outline='#b9dbd6')
 txt(c,53,204,d['meta'],11.8,True)
 left=[('Version',meta['version']+' · '+meta['build']),('Author' if lang=='en' else 'Autore',meta['author']),('Licenza' if lang=='it' else 'License',meta['license'])]
 yy=184
 for key,value in left:
  txt(c,53,yy,key+':',8.5,True);txt(c,117,yy,value,8.5);yy-=19
 txt(c,54,118,'GitHub:  github.com/desalvo/quorivio',8.6,True)
 txt(c,309,182,meta['email'],8.8)
 wrap(c,d['min'],309,160,230,8.1,11,5,ink=MUTED)
 page_footer(c,2,lang);c.save();shutil.copy2(dest,WEB/dest.name)
 print(dest.name,'bytes',dest.stat().st_size)
 return dest

if __name__=='__main__':
 for lang in ('it','en'):build_one(lang)
