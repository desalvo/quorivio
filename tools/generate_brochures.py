#!/usr/bin/env python3
"""Quorivio mock-faithful A4 portrait, six-page IT/EN brochure.

All copy, badges, charts and diagrams are vector PDF objects. Artwork is either
existing checked-in Quorivio editorial photography/screenshots or a local
reference mock for visual preview only. Never rely on a remote image URL.

Usage: python tools/generate_brochures.py [--output-dir docs/brochures] [--reference /path/mock.jpg]
"""
from __future__ import annotations
import argparse
import math
import os
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageEnhance
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'docs/assets/brochure-editorial'
ILL = ROOT / 'docs/assets/manual-illustrations'
EVIDENCE = ROOT / 'docs/assets/manual-evidence-rc291'
W,H=A4
NAVY='#111943'; INK='#11163c'; PURPLE='#6535df'; VIOLET='#8a33ef'; CYAN='#00c6dc'; BLUE='#0876e8'; PINK='#f52f96'; GREEN='#0fbe8c'; YELLOW='#ffb400'; LIGHT='#f5f7ff'; PALE='#eaf1ff'; WHITE='#ffffff'; MUTED='#344166'; BORDER='#dce1f0'
for name,fname in [('Lato','Lato-Regular.ttf'),('LatoBold','Lato-Bold.ttf'),('LatoHeavy','Lato-Heavy.ttf'),('LatoBlack','Lato-Black.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/lato/'+fname))

def fill(c,col): c.setFillColor(HexColor(col) if isinstance(col,str) else col)
def stroke(c,col): c.setStrokeColor(HexColor(col) if isinstance(col,str) else col)
def rect(c,x,y,w,h,color,rad=0,outline=None):
    fill(c,color)
    if outline:stroke(c,outline)
    if rad:c.roundRect(x,y,w,h,rad,fill=1,stroke=int(bool(outline)))
    else:c.rect(x,y,w,h,fill=1,stroke=int(bool(outline)))
def text(c,s,x,y,size=11,color=INK,font='Lato',center=False):
    fill(c,color);c.setFont(font,size)
    (c.drawCentredString if center else c.drawString)(x,y,s)
def lines(c,s,x,y,width,size=10,leading=None,color=INK,font='Lato',max_lines=None):
    leading=leading or size*1.25; result=[]
    for paragraph in str(s).split('\n'):
        words=paragraph.split(); cur=''
        for w in words:
            v=(cur+' '+w).strip()
            if cur and pdfmetrics.stringWidth(v,font,size)>width:
                result.append(cur);cur=w
            else:cur=v
        if cur:result.append(cur)
    if max_lines is not None and len(result)>max_lines: raise ValueError(f'Overflow: {s[:60]}: {len(result)}>{max_lines}')
    for row in result:text(c,row,x,y,size,color,font);y-=leading
    return y

def chip(c,x,y,label,col=PURPLE,size=9):
    w=pdfmetrics.stringWidth(label,'LatoBold',size)+24
    rect(c,x,y-6,w,25,col,11);text(c,label,x+12,y+2,size,WHITE,'LatoBold');return w

def ring(c,x,y,r,thick,col,start=0,extent=360):
    stroke(c,col);c.setLineWidth(thick);c.arc(x-r,y-r,x+r,y+r,start,extent)

def icon(c,cx,cy,symbol,col=PURPLE):
    # Quorivio-style round icon badges; glyph remains readable even in grayscale.
    fill(c,col);c.circle(cx,cy,18,fill=1,stroke=0)
    stroke(c,WHITE);c.setLineWidth(2)
    if symbol=='bars':
        for i,h in enumerate([9,17,13,24]):c.line(cx-11+i*7,cy-10,cx-11+i*7,cy-10+h)
    elif symbol=='people':
        c.circle(cx-5,cy+6,4,stroke=1,fill=0);c.circle(cx+6,cy+6,4,stroke=1,fill=0)
        c.arc(cx-13,cy-11,cx+1,cy+4,0,175);c.arc(cx,cy-11,cx+14,cy+4,0,175)
    elif symbol=='chat':
        c.roundRect(cx-11,cy-7,22,15,5,stroke=1,fill=0);c.line(cx-6,cy-8,cx-9,cy-12)
    elif symbol=='play':
        p=c.beginPath();p.moveTo(cx-5,cy-9);p.lineTo(cx+9,cy);p.lineTo(cx-5,cy+9);p.close();fill(c,WHITE);c.drawPath(p,stroke=0,fill=1)
    elif symbol=='star':
        p=c.beginPath()
        for i in range(10):
            a=math.pi/2+i*math.pi/5;rr=12 if i%2==0 else 5.5
            xx=cx+rr*math.cos(a); yy=cy+rr*math.sin(a)
            if i==0:p.moveTo(xx,yy)
            else:p.lineTo(xx,yy)
        p.close();fill(c,WHITE);c.drawPath(p,fill=1,stroke=0)
    elif symbol=='check':
        c.line(cx-8,cy,cx-2,cy-6);c.line(cx-2,cy-6,cx+10,cy+9)
    elif symbol=='screen':
        c.roundRect(cx-11,cy-7,22,17,2,stroke=1,fill=0);c.line(cx-6,cy-12,cx+6,cy-12);c.line(cx,cy-8,cx,cy-12)
    elif symbol=='send':
        p=c.beginPath();p.moveTo(cx-11,cy-5);p.lineTo(cx+12,cy+10);p.lineTo(cx+5,cy-12);p.lineTo(cx+1,cy-2);p.close();c.drawPath(p,stroke=1,fill=0)
    else:
        c.circle(cx,cy,9,fill=0,stroke=1);c.circle(cx,cy,3,fill=0,stroke=1)

def logo(c,x,y,scale=1,on_dark=False):
    # Independent vector redraw of the distinctive multicolor Q mark.
    c.saveState();c.translate(x,y);c.scale(scale,scale)
    for offset,col in [(20,PURPLE),(14,BLUE),(8,CYAN)]:ring(c,16,17,11,5.5,col,offset,240)
    stroke(c,PINK);c.setLineWidth(5);c.line(22,9,31,0)
    text(c,'Quorivio',36,6,25,WHITE if on_dark else NAVY,'LatoBlack');c.restoreState()

def photo(c,path,x,y,w,h,position='center'):
    if isinstance(path,Image.Image):
        im=path.copy().convert('RGB')
    elif path is not None and Path(path).is_file():
        im=Image.open(path).convert('RGB')
    else:
        rect(c,x,y,w,h,PALE,10);return
    factor=max(1.5, min(3, 1800/max(w,h)))
    center=(.20,.5) if position=='portrait' else (.5,.5)
    if position=='contain':
        foreground=ImageOps.contain(im,(int(w*factor),int(h*factor)),Image.Resampling.LANCZOS)
        frame=Image.new('RGB',(int(w*factor),int(h*factor)),'#edf1ff')
        frame.paste(foreground,((frame.width-foreground.width)//2,(frame.height-foreground.height)//2))
        im=frame
    else:
        im=ImageOps.fit(im,(int(w*factor),int(h*factor)),Image.Resampling.LANCZOS,centering=center)
    if position=='portrait':
        # Composite a *continuous* left fade into the dark cover, eliminating
        # hard vertical crop lines and keeping the entire speaker's face visible.
        import PIL.Image as _Image
        mask=_Image.new('L',(im.width,1))
        mask.putdata([round(255*min(1,max(0,(i/im.width-.52)/.19))) for i in range(im.width)])
        im=_Image.composite(im,_Image.new('RGB',im.size,(17,25,67)),mask.resize(im.size))
    b=BytesIO();im.save(b,'JPEG',quality=90,optimize=True);b.seek(0)
    c.drawImage(ImageReader(b),x,y,w,h)

def draw_devices(c,x,y,w,h):
    """Crisp vector illustration of a presenter laptop, results tablet and poll phone.

    Avoids re-cropping low-resolution text from the panoramic reference board.
    """
    # Laptop screen with an original abstract presentation (not an app screenshot).
    rect(c,x+7,y+57,206,137,NAVY,9)
    rect(c,x+13,y+64,194,123,'#eff4ff',4)
    rect(c,x+17,y+139,187,44,PURPLE,4)
    text(c,'La nostra strategia',x+24,y+163,12,WHITE,'LatoBlack')
    text(c,'per il futuro',x+24,y+147,10,WHITE,'LatoBold')
    rect(c,x+24,y+116,83,8,BLUE,3)
    rect(c,x+24,y+102,139,6,'#cbd6f1',3)
    rect(c,x+24,y+89,104,6,'#cbd6f1',3)
    fill(c,HexColor('#7181a9'));p=c.beginPath();p.moveTo(x,y+51);p.lineTo(x+221,y+51);p.lineTo(x+235,y+43);p.lineTo(x-7,y+43);p.close();c.drawPath(p,stroke=0,fill=1)
    rect(c,x+75,y+46,70,4,'#a8b1ca',3)
    # Tablet chart screen.
    rect(c,x+220,y+36,78,144,NAVY,8)
    rect(c,x+227,y+45,64,125,WHITE,4)
    text(c,'Risultati',x+232,y+153,8,NAVY,'LatoBlack')
    for j,(v,col) in enumerate(zip([46,58,29,38],[BLUE,CYAN,PURPLE,PINK])):
        rect(c,x+234+j*13,y+83,9,v,col,2)
    # Smartphone poll card, offset in front of the laptop edge.
    rect(c,x+287,y+28,43,117,'#10183c',7)
    rect(c,x+291,y+35,35,100,'#eef2ff',3)
    fill(c,CYAN);c.circle(x+309,y+122,8,stroke=0,fill=1)
    for j,(q,col) in enumerate(zip([17,22,12],[PURPLE,BLUE,PINK])):
        rect(c,x+297,y+99-j*22,q,9,col,2)
    icon(c,x+310,y+52,'check',GREEN)

def bg(c,page):
    rect(c,0,0,W,H,WHITE)
    # diagonal soft-color swashes, full bleed
    fill(c,Color(.94,.97,1,alpha=1));p=c.beginPath();p.moveTo(W-195,H);p.curveTo(W-30,H-20,W-90,H-90,W,H-118);p.lineTo(W,H);p.close();c.drawPath(p,fill=1,stroke=0)
    fill(c,HexColor('#e7dafe'));c.circle(W+65,H-10,85,fill=1,stroke=0)
    if page!=1:
        rect(c,0,0,W,32,NAVY)
        logo(c,29,7,.37,on_dark=True)
        text(c,f'{page}/6',W-40,12,10,WHITE,'LatoBold')

def title(c,top,subtitle=None,size=27):
    y=H-49
    for s in top.split('\n'):text(c,s,32,y,size,NAVY,'LatoBlack');y-=size*1.03
    if subtitle:y=lines(c,subtitle,33,y-6,W-66,10.8,14.5,MUTED,'LatoBold')
    return y

def card(c,x,y,w,h,fillcolor=WHITE,rounding=12,outline=BORDER):rect(c,x,y,w,h,fillcolor,rounding,outline)

def footer(c,num,lang):
    if num==1:rect(c,0,0,W,35,NAVY)
    if num==1:logo(c,29,8,.4,True);text(c,'1/6',W-45,13,10,WHITE,'LatoBold')
    else:pass

def reference_files(reference):
    # Source mock is used only for local layout proofing, not needed in git.
    if not reference or not reference.is_file():return {}
    im=Image.open(reference).convert('RGB');regions={
      'hero':(170,65,515,345),
      'session':(543,191,1005,415),
      'results':(1240,307,1492,521),
      'gauge':(105,663,499,824),
      'hall':(556,624,692,716),
      'remote':(704,624,842,718),
      'hybrid':(854,623,991,719),
      'devices':(555,908,837,1013),
      'export':(1080,901,1478,1005)
    }
    return {key:im.crop(box) for key,box in regions.items()}

def choose_photo(local,key,lang):
    mapping={
      'hero':[ART/f'marketing-photo-{lang}.jpg',ILL/'editorial-live-presentation-rc286.jpg'],
      'session':[ART/f'marketing-photo-{lang}.jpg',ILL/'editorial-live-presentation-rc286.jpg'],
      'results':[ILL/'editorial-collaborative-workflow-rc286.jpg',ART/f'marketing-photo-{lang}.jpg'],
      'gauge':[EVIDENCE/'presenter-live.png'],
      'hall':[ILL/'editorial-live-presentation-rc286.jpg'],
      'remote':[ILL/'editorial-collaborative-workflow-rc286.jpg'],
      'hybrid':[ART/f'marketing-photo-{lang}.jpg'],
      'devices':[EVIDENCE/'rehearsal-side-by-side-smartphone.png'],
      'export':[EVIDENCE/'editor-canvas.png'],
    }
    if key in local: return local[key]
    for p in mapping.get(key,[]):
        if p.exists():return p
    return None

TEXT={
 'it':{
   'cover':['Presenta,','interagisci,','coinvolgi!'],'cover_sub':'Sondaggi, quiz, domande live e risultati immediati. Il tuo pubblico partecipa davvero, in presenza, da remoto o in modalità ibrida.',
   'features':['Sondaggi live','Q&A dal pubblico','Quiz e competizioni','Votazioni','Slide interattive'],
   'flow_title':'Una sessione Quorivio\nin pratica','flow_sub':'Dall’idea alla presentazione interattiva, in pochi passi.',
   'steps':[('Crea','la sessione'),('Condividi','l’accesso (QR o link)'),('Presenta','e interagisci live'),('Visualizza','i risultati')],
   'bottom_flow':['Partecipazione immediata','Risultati in tempo reale','Pubblico coinvolto','PC, tablet e smartphone'],
   'widgets_title':'Widget potenti per\npresentazioni dinamiche','widgets_sub':'Un’ampia libreria di widget, grafici professionali e contenuti multimediali.',
   'widgets':['Scelta singola e multipla','Risposta aperta','Soddisfazione 0–10','Sondaggi e votazioni','Q&A e domande live','Immagine','Video','Testo e markup','Profilo presentatore','Reazioni live'],
   'result_title':'Risultati ricchi e professionali','charts':['Barre','Torta','Linee','Area','Donut','Radar','Nuvola di parole','Tabella'],
   'gauge_title':'Percentuale di risposte\nelle widget risultati','gauge_sub':'Monitora in tempo reale la partecipazione con un grafico gauge integrato nella widget risultati.',
   'gauge_question':'Hai già usato strumenti di IA?','answers':['Sì, regolarmente','Sì, occasionalmente','No, ma sono interessato','No, non mi interessa'],
   'settings':'Formato widget (Risultati)','toggle':'Mostra percentuale di risposte','gauge_size':'Dimensione gauge',
   'details':['Calcolo automatico: utenti che hanno risposto almeno una volta / utenti connessi','Intervallo dal 0% al 100%','Dimensione regolabile dal 20% al 100%','Aggiornamento in tempo reale'],
   'event_title':'Per ogni tipo di evento','event_sub':'La stessa esperienza interattiva, ovunque si trovi il pubblico.','events':['In presenza','Da remoto','Ibrido'],
   'events_copy':['Coinvolgi la platea in sala','Partecipa ovunque, con un semplice link','Unisci persone in sala e online'],
   'attendees':'500','attendees_sub':'partecipanti testati\nin benchmark CI',
   'benefits':['Eventi, riunioni, seminari e workshop','Presentazioni con slide, PDF e PowerPoint','Interazioni live da qualsiasi dispositivo','Esperienza fluida, stabile e scalabile'],
   'qr':'Partecipa alla sessione con il QR code',
   'share_title':'Condividi, esporta e riutilizza','share_sub':'Porta i tuoi contenuti ovunque e riutilizza le presentazioni.',
   'export_pdf':'Export PDF','export_pdf_desc':'Presentazioni, layout e immagini esportabili in PDF.',
   'export_pptx':'Export PPTX','export_pptx_desc':'Esporta in PowerPoint e verifica la resa dei contenuti complessi.',
   'support_title':'Invia la tua sessione per assistenza',
   'support_desc':'Dalla dashboard puoi condividere un file .quo per consentire al supporto di esaminare la sessione. I dati sensibili richiedono il tuo consenso.',
   'last':['Archiviazione sicura','Notifiche multicanale','Installazione flessibile'],
   'last_desc':['Backup e conservazione configurabili','E-mail e integrazioni disponibili in base al server','Docker, Podman o Kubernetes'],
   'copy1':'Il tuo pubblico partecipa in tempo reale, anche da smartphone!','copy2':'Interazione immediata. Risposte e grafici davanti a tutti.','note':'Schermate illustrative; performance e formati dipendono dalla configurazione. Software EUPL-1.2.'
 },
 'en':{
   'cover':['Present,','interact,','engage!'],'cover_sub':'Live polls, quizzes, audience Q&A and instant results. Make your audience part of the event—in person, remotely or hybrid.',
   'features':['Live polling','Audience Q&A','Quizzes and competitions','Voting','Interactive slides'],
   'flow_title':'A Quorivio session\nin practice','flow_sub':'From your idea to an interactive live presentation in a few steps.',
   'steps':[('Create','your session'),('Share','a QR code or link'),('Present','and interact live'),('Show','instant results')],
   'bottom_flow':['Join instantly','Real-time results','Active engagement','PC, tablet and smartphone'],
   'widgets_title':'Powerful widgets for\ndynamic presentations','widgets_sub':'A rich widget library with professional charts and multimedia.',
   'widgets':['Single & multiple choice','Open answers','Satisfaction 0–10','Polls and votes','Live audience Q&A','Images','Video','Text and markup','Presenter profile','Live reactions'],
   'result_title':'Rich, professional results','charts':['Bar','Pie','Line','Area','Donut','Radar','Word cloud','Table'],
   'gauge_title':'Response participation\nin results widgets','gauge_sub':'Track live participation with a refined gauge chart built into results widgets.',
   'gauge_question':'Have you used AI tools?','answers':['Yes, regularly','Yes, occasionally','Not yet, but interested','No interest'],
   'settings':'Widget format (Results)','toggle':'Show response participation','gauge_size':'Gauge size',
   'details':['Automatic: users with at least one reply / all connected users','Clamped between 0% and 100%','Adjustable size from 20% to 100%','Real-time updates'],
   'event_title':'For every event format','event_sub':'The same interactive experience wherever the audience is.','events':['In person','Remote','Hybrid'],
   'events_copy':['Engage everyone in the room','Join anywhere with a simple link','Bring in-room and online together'],
   'attendees':'500','attendees_sub':'participants exercised\nin CI benchmark',
   'benefits':['Events, meetings, seminars and workshops','Present with slides, PDFs and PowerPoint','Live interaction on any device','Responsive and scalable experience'],
   'qr':'Join the session with the QR code',
   'share_title':'Share, export and reuse','share_sub':'Take your presentation content anywhere and reuse your sessions.',
   'export_pdf':'Export PDF','export_pdf_desc':'Export presentations, layouts and images to PDF.',
   'export_pptx':'Export PPTX','export_pptx_desc':'Export PowerPoint content and check complex visual fidelity.',
   'support_title':'Send your session for support',
   'support_desc':'Share a .quo bundle from the dashboard so support can review a session. Your consent is needed for sensitive data.',
   'last':['Secure retention','Multichannel alerts','Flexible deployment'],
   'last_desc':['Configurable backup and retention','E-mail and integrations depend on your server','Docker, Podman or Kubernetes'],
   'copy1':'Your audience participates live, even on smartphones!','copy2':'Instant interaction. Responses and charts everyone can see.','note':'Illustrative visuals; performance and exports depend on setup. EUPL-1.2 software.'
 }
}

def make_brochure(lang,out,reference=None):
    d=TEXT[lang];refs=reference_files(reference);out.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle('Quorivio - six page A4 portrait brochure - '+lang.upper())
    c.setAuthor('Alessandro De Salvo - INFN Sez. Roma1')
    def end(p): footer(c,p,lang);c.showPage()
    def artwork(key,x,y,w,h):photo(c,choose_photo(refs,key,lang),x,y,w,h,'portrait' if key=='hero' else 'center')
    # 1 • Immersive cover. Full bleed, like the visual reference.
    rect(c,0,0,W,H,NAVY)
    # Portrait scene sits behind the copy, like the user-provided mock.
    artwork('hero',219,220,W-219,580)
    fill(c,HexColor('#3624a6'));c.circle(W+71,H-28,88,fill=1,stroke=0)
    fill(c,HexColor(CYAN));c.circle(W+64,H-21,43,fill=1,stroke=0)
    logo(c,30,H-75,1.08,True)
    text(c,'INTERACTIVE PRESENTATIONS  •  LIVE ENGAGEMENT' if lang=='en' else 'PRESENTAZIONI INTERATTIVE  •  COINVOLGIMENTO LIVE',31,H-105,9.1,'#d6eeff','LatoBold')
    yy=H-168
    for i,t in enumerate(d['cover']):
        text(c,t,30,yy,43 if i<2 else 47,CYAN if i==2 else WHITE,'LatoBlack');yy-=51
    lines(c,d['cover_sub'],32,H-345,322,11.8,16,WHITE,'LatoBold',max_lines=6)
    # Wide, dark caption plate ties the portrait to the icon ribbon.
    rect(c,0,165,W,55,'#20185d')
    lines(c,d['copy1'],27,194,535,13,17,WHITE,'LatoHeavy',max_lines=2)
    colorbars=[PURPLE,BLUE,CYAN,PINK,PURPLE]
    for i,(name,color) in enumerate(zip(d['features'],colorbars)):
        xx=16+i*114;card(c,xx,55,107,95,'#202964',10,'#343887')
        icon(c,xx+53,121,['bars','chat','star','people','screen'][i],color)
        # wrap labels manually for precise width
        size=9.3
        words=name.split(); rows=[];row=''
        for word in words:
            attempt=(row+' '+word).strip()
            if pdfmetrics.stringWidth(attempt,'LatoBold',size)>98 and row:rows.append(row);row=word
            else:row=attempt
        if row:rows.append(row)
        for r,word in enumerate(rows):text(c,word,xx+53,97-r*13,size,WHITE,'LatoBold',center=True)
    end(1)
    # 2 • Session flow and interactive audience photo
    bg(c,2);title(c,d['flow_title'],d['flow_sub'],27)
    cols=[PURPLE,BLUE,'#02bdb9',YELLOW];steps=d['steps']
    for i,(a,b) in enumerate(steps):
        xx=26+i*138;card(c,xx,570,129,125,['#eee3ff','#e6efff','#d9fbf8','#fff2d1'][i],14,None)
        icon(c,xx+64,677,['screen','people','play','bars'][i],cols[i])
        text(c,str(i+1),xx+10,642,17,cols[i],'LatoBlack')
        text(c,a,xx+32,642,12,NAVY,'LatoHeavy')
        lines(c,b,xx+15,619,105,10,12.5,NAVY,'LatoBold',max_lines=2)
    artwork('session',0,292,W,256)
    card(c,23,295,249,77,'#ffffff',9)
    text(c,'LIVE',37,346,10,PINK,'LatoBlack');lines(c,d['copy2'],37,328,220,10,13,NAVY,'LatoBold',2)
    for i,item in enumerate(d['bottom_flow']):
        xx=26+(i%2)*275;yy=178-(i//2)*101
        card(c,xx,yy,264,90,['#eff4ff','#ebfcfa','#f5efff','#fff8e9'][i],12,None)
        icon(c,xx+37,yy+48,['play','bars','people','screen'][i],[PURPLE,CYAN,BLUE,VIOLET][i])
        lines(c,item,xx+70,yy+56,183,11,14,NAVY,'LatoHeavy',max_lines=2)
    end(2)
    # 3 • 10 widget catalogue + results visualizations
    bg(c,3);title(c,d['widgets_title'],d['widgets_sub'],27)
    tcolors=[PURPLE,VIOLET,YELLOW,PURPLE,PINK,CYAN,VIOLET,BLUE,BLUE,PINK]
    shapes=['bars','chat','star','bars','chat','screen','play','screen','people','star']
    for i,name in enumerate(d['widgets']):
        col=i%5;row=i//5;xx=25+col*110;yy=609-row*104
        card(c,xx,yy,103,96,'#f0f2ff' if row==0 else '#eaf2ff',12,None)
        icon(c,xx+51,yy+69,shapes[i],tcolors[i])
        yytext=yy+37;words=name.split();rr=[];cw=''
        for w in words:
            new=(cw+' '+w).strip()
            if pdfmetrics.stringWidth(new,'LatoBold',8.6)>93 and cw:rr.append(cw);cw=w
            else:cw=new
        if cw:rr.append(cw)
        for n,w in enumerate(rr[:3]):text(c,w,xx+51,yytext-n*11,8.6,NAVY,'LatoBold',True)
    card(c,23,395,549,94,'#f1efff',12,None)
    artwork('results',340,396,231,92)
    text(c,'Live charts at a glance' if lang=='en' else 'Grafici live a colpo d’occhio',38,452,15.5,NAVY,'LatoBlack')
    lines(c,'Instant poll outcomes, styled to fit each results widget.' if lang=='en' else 'Risposte e statistiche immediate, pronte per essere presentate.',38,428,293,10,13,MUTED,'LatoBold',max_lines=3)
    card(c,22,103,551,282,'#f3f4ff',17)
    text(c,d['result_title'],38,352,21,NAVY,'LatoBlack')
    text(c,'Bar  •  Pie  •  Line  •  Donut  •  Radar  •  Word cloud' if lang=='en' else 'Barre  •  Torta  •  Linee  •  Donut  •  Radar  •  Nuvola parole',39,333,10,MUTED,'LatoBold')
    # charts in crisp PDF vector
    card(c,39,145,226,162,WHITE,11,None)
    vals=[.85,.68,.47,.28];cs=[BLUE,CYAN,PURPLE,PINK]
    for j,v in enumerate(vals):
        yy=274-j*33;rect(c,63,yy,153*v,16,cs[j],3);text(c,f'{[42,27,18,9][j]}%',230,yy+3,10,NAVY,'LatoBold')
    card(c,281,145,271,162,WHITE,11,None)
    for j,(a,l) in enumerate(zip(d['charts'],['bars','pie','line','area','donut','radar','cloud','table'])):
        x=291+(j%4)*65;y=235-(j//4)*65
        icon(c,x+32,y+14,['bars','star','bars','bars','star','people','chat','screen'][j],[BLUE,YELLOW,CYAN,PINK,PURPLE,VIOLET,YELLOW,BLUE][j])
        text(c,a,x+32,y-13,8.2,NAVY,'LatoBold',True)
    text(c,'QUIZ  •  RISULTATI LIVE  •  ANALYTICS' if lang=='it' else 'QUIZZES  •  LIVE RESULTS  •  ANALYTICS',42,79,11,PURPLE,'LatoBlack')
    end(3)
    # 4 • Response participation gauge
    bg(c,4);title(c,d['gauge_title'],d['gauge_sub'],26)
    chip(c,29,674,'NEW FEATURE' if lang=='en' else 'NOVITÀ',PINK)
    card(c,26,355,543,299,'#f2efff',15,None)
    card(c,38,366,519,273,WHITE,11,None)
    text(c,d['gauge_question'],56,611,14,NAVY,'LatoBlack')
    ans=[52,24,18,6];cc=[PURPLE,BLUE,CYAN,'#a0a9bf']
    for j,(label,num) in enumerate(zip(d['answers'],ans)):
        yy=567-j*41
        # avoid line-breaking confusing labels
        lines(c,label,53,yy+5,155,9,11,INK,'LatoBold',max_lines=2)
        rect(c,206,yy,118*num/52,18,cc[j],2)
        text(c,str(num)+'%',330,yy+3,10,NAVY,'LatoBold')
    # polished large semicircular gauge: 76% of 200 connected participants
    cx,cy,rr=452,474,77
    ring(c,cx,cy,rr,21,'#d9deea',0,180)
    for off,col in [(0,GREEN),(50,'#6cda2f'),(95,CYAN)]:
        # approx segmented arc within the 76% progress
        ring(c,cx,cy,rr,21,col,180-off-52,52)
    ring(c,cx,cy,rr,21,GREEN,180-136.8,35)
    text(c,'76%',cx,481,34,NAVY,'LatoBlack',True)
    text(c,'152 / 200',cx,459,10,INK,'LatoBold',True)
    text(c,'received replies' if lang=='en' else 'risposte ricevute',cx,444,8.8,MUTED,'LatoBold',True)
    # widget format controls and explanatory checked points
    card(c,27,70,276,269,'#f7f8ff',13,None)
    rect(c,28,299,274,39,'#e6e7fc',10)
    text(c,d['settings'],43,310,13,NAVY,'LatoBlack')
    rect(c,43,260,18,18,PURPLE,4);icon(c,52,270,'check',PURPLE)
    lines(c,d['toggle'],74,263,209,10.2,13,NAVY,'LatoBold',max_lines=2)
    text(c,d['gauge_size'],44,221,10,NAVY,'LatoBold')
    rect(c,47,185,214,6,'#ddd8f9',3);rect(c,47,185,126,6,PURPLE,3)
    fill(c,PURPLE);c.circle(173,188,8,stroke=0,fill=1)
    card(c,225,170,63,32,WHITE,5,BORDER);text(c,'60%',242,181,11,NAVY,'LatoBlack')
    text(c,'20%',47,153,9,MUTED,'LatoBold');text(c,'100%',250,153,9,MUTED,'LatoBold')
    text(c,'Responsive gauge',46,113,10,PURPLE,'LatoHeavy')
    for i,detail in enumerate(d['details']):
        y=288-i*63
        icon(c,329,y,'check',GREEN)
        lines(c,detail,357,y+5,199,9.7,12,INK,'LatoBold',max_lines=3)
    end(4)
    # 5 • formats and 500 participant benchmark
    bg(c,5);title(c,d['event_title'],d['event_sub'],29)
    for i,(name,desc,key) in enumerate(zip(d['events'],d['events_copy'],['hall','remote','hybrid'])):
        x=25+i*186;card(c,x,527,174,183,WHITE,10,None)
        artwork(key,x+5,580,164,126)
        icon(c,x+21,558,'people' if i!=1 else 'screen',[PURPLE,BLUE,VIOLET][i])
        text(c,name,x+44,558,12,NAVY,'LatoBlack')
        lines(c,desc,x+11,542,153,9,11,MUTED,'LatoBold',max_lines=2)
    # vibrant, faithful brush-stroke highlight, but no unjustified guarantee
    rect(c,25,360,543,124,'#f0f3ff',12,None)
    rect(c,37,374,238,96,PURPLE,27,None)
    fill(c,HexColor(CYAN));p=c.beginPath();p.moveTo(90,379);p.curveTo(128,391,240,393,263,371);p.lineTo(90,364);p.close();c.drawPath(p,fill=1,stroke=0)
    text(c,d['attendees'],149,407,51,WHITE,'LatoBlack',True)
    for i,word in enumerate(d['attendees_sub'].split('\n')):text(c,word,149,392-i*12,9.1,WHITE,'LatoHeavy',True)
    for i,item in enumerate(d['benefits']):
        icon(c,290,451-i*25,'check',GREEN)
        lines(c,item,318,451-i*25,225,9.4,11,INK,'LatoBold',max_lines=2)
    card(c,25,75,543,267,'#edf1ff',12,None)
    draw_devices(c,36,130,329,201)
    # drawn QR-like mark, decorative label (not functional)
    rect(c,401,175,141,140,WHITE,8,None)
    for ix in range(11):
        for iy in range(11):
            if (ix*7+iy*11+ix*iy)%9 in (0,1,2,3):rect(c,414+ix*10.5,186+iy*10.5,8,8,NAVY)
    lines(c,d['qr'],389,131,170,10.5,14,NAVY,'LatoHeavy',max_lines=2)
    text(c,'QR ILLUSTRATIVE' if lang=='en' else 'QR ILLUSTRATIVO',412,88,8,PURPLE,'LatoBold')
    end(5)
    # 6 • portability and delivery
    bg(c,6);title(c,d['share_title'],d['share_sub'],28)
    for i in range(2):
        x=26+i*279
        card(c,x,499,265,188,'#f4f5ff',12,None)
        rect(c,x+17,606,55,57,'#e20a22' if i==0 else '#ef7525',12)
        text(c,'PDF' if i==0 else 'PPTX',x+23,622,16,WHITE,'LatoBlack')
        text(c,d['export_pdf'] if i==0 else d['export_pptx'],x+83,643,16,NAVY,'LatoBlack')
        lines(c,d['export_pdf_desc'] if i==0 else d['export_pptx_desc'],x+83,619,162,10,13,INK,'LatoBold',max_lines=4)
        # framed editable-document icon
        card(c,x+19,513,227,72,WHITE,8,None)
        rect(c,x+31,530,65,43,'#ede7fc',3)
        for k,ci in enumerate([PURPLE,BLUE,CYAN]):rect(c,x+39,560-k*13,44-k*6,5,ci,2)
        rect(c,x+110,530,124,43,PALE,3)
        for k,ci in enumerate([YELLOW,BLUE,PURPLE,CYAN,PINK]):rect(c,x+122+k*22,539,13,9+k*4,ci,2)
    card(c,25,323,543,155,'#f4eefe',13,None)
    icon(c,66,440,'send',VIOLET)
    text(c,d['support_title'],97,442,16,NAVY,'LatoBlack')
    lines(c,d['support_desc'],97,418,447,10.8,15,INK,'LatoBold',max_lines=5)
    chip(c,97,352,'.quo',PURPLE)
    for i,(a,b) in enumerate(zip(d['last'],d['last_desc'])):
        x=25+i*186;card(c,x,80,174,226,'#edf3ff',12,None)
        icon(c,x+34,267,['screen','chat','bars'][i],[BLUE,YELLOW,BLUE][i])
        lines(c,a,x+13,228,150,13,16,NAVY,'LatoBlack',max_lines=2)
        lines(c,b,x+13,177,149,10.4,14,INK,'LatoBold',max_lines=5)
    try:
        from manual_release_metadata import metadata
        publication=metadata()
        build='RC333';author=publication.get('author','Alessandro De Salvo')+' - INFN Sez. Roma1';email=publication.get('email','braket71@gmail.com')
    except ImportError:
        build='RC333';author='Alessandro De Salvo - INFN Sez. Roma1';email='braket71@gmail.com'
    text(c,'github.com/desalvo/quorivio  •  EUPL-1.2  •  .quo',26,64,8.3,MUTED,'LatoBold')
    text(c,f'{build}  •  {author}  •  {email}',26,50,7.9,MUTED,'Lato')
    text(c,d['note'],26,37,7.7,MUTED,'Lato')
    end(6)
    c.save()
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=Path(os.environ.get('QUORIVIO_BROCHURE_OUTPUT_DIR',str(ROOT/'docs/brochures'))));ap.add_argument('--reference',type=Path,default=ROOT/'docs/assets/brochure-editorial/mock-reference-6-pages-2026-11.jpg');ap.add_argument('--no-web',action='store_true')
    args=ap.parse_args()
    for lang in ('it','en'):
        dest=make_brochure(lang,args.output_dir/f'quorivio-brochure-{lang}.pdf',args.reference)
        print(dest, dest.stat().st_size)
        if not args.no_web and not os.environ.get('QUORIVIO_BROCHURE_NO_WEB'):
            import shutil
            w=ROOT/'apps/web/public/docs/brochures';w.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest,w/dest.name)
