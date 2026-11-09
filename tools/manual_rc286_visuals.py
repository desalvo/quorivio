#!/usr/bin/env python3
"""Regenerate original bilingual workflow diagrams for the Quorivio manuals.
All diagrams are conceptual drawings, NOT screenshots of the running app.
Optional editorial photo inserts are synthetic illustrative crops, never UI evidence.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets/manual-illustrations';OUT.mkdir(parents=True,exist_ok=True)
PURPLE='#5b57c8';TEAL='#008d82';INK='#1b2b4d';MUTED='#586987'
try:
 F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
 SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
 BOLD=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
except OSError:F=SMALL=BOLD=ImageFont.load_default()

def scene(filename,title,steps,rows=1):
 im=Image.new('RGB',(1640,580 if rows==1 else 760),'#f7f9fd');d=ImageDraw.Draw(im)
 d.rounded_rectangle((25,25,1615,im.height-26),24,fill='#ffffff',outline='#d7dfef',width=4)
 d.text((65,62),title,font=BOLD,fill=INK)
 count=len(steps);cols=math.ceil(count/rows);step_w=min(460,int((1510-(cols-1)*35)/cols))
 for n,(heading,body,color) in enumerate(steps):
  col=n%cols;row=n//cols;x=63+col*(step_w+35);y=150+row*295
  d.rounded_rectangle((x,y,x+step_w,y+215),18,fill='#f9faff',outline='#c8d4e9',width=3)
  d.rounded_rectangle((x,y,x+step_w,y+64),18,fill=color)
  d.text((x+20,y+15),heading,font=F,fill='#ffffff')
  for i,line in enumerate(body.split('|')):
   d.text((x+18,y+92+i*31),line[:38],font=SMALL,fill=INK)
  if col<cols-1:
   arrowx=x+step_w+8;d.line((arrowx,y+112,arrowx+22,y+112),fill=TEAL,width=6)
   d.polygon(((arrowx+22,y+103),(arrowx+34,y+112),(arrowx+22,y+121)),fill=TEAL)
 d.text((65,im.height-80),'SCHEMA ESPLICATIVO / CONCEPTUAL DIAGRAM — non è una schermata reale',font=SMALL,fill=MUTED)
 im.save(OUT/filename,optimize=True)

scene('workflow-page-editor-rc286.png','EDITOR DI PAGINA / PAGE EDITOR',[
 ('1. Pagine / Pages','Apri la sessione|Seleziona una pagina',PURPLE),
 ('2. Widget','Inserisci domanda, testo,|grafico, forma o media',TEAL),
 ('3. Configurazione','Proprieta e formato|Anteprima nella miniatura',PURPLE),
 ('4. Prova / Test','Desktop, presentatore,|pubblico o smartphone',TEAL)])
scene('workflow-scheme-editor-rc286.png','SCHEMI E PAGINE / MASTER INHERITANCE',[
 ('Schema globale','Titolo, footer, logo,|sfondo e stile comune',PURPLE),
 ('Pagina A','Contenuto locale|eredita schema globale',TEAL),
 ('Pagina B','Widget indipendenti|personalizzazione locale',TEAL),
 ('Presentazione','Controlla le anteprime|e salva lo schema',PURPLE)])
scene('workflow-preview-live-rc286.png','ANTEPRIME E LIVE / PREVIEW AND LIVE',[
 ('Presentatore','Pagina senza input|Risultati e pulsante R',PURPLE),
 ('Partecipante','Risposte di prova|Senza invio al server',TEAL),
 ('Affiancate','Confronto dei layout|Desktop e smartphone',PURPLE),
 ('Sessione live','Invio reale, sincronizzazione|statistiche aggiornate',TEAL)])
scene('workflow-local-quo-rc286.png','ARCHIVIO DI SESSIONE .quo / PORTABLE SESSION',[
 ('Esporta','Sidebar della sessione|Salva un file .quo',PURPLE),
 ('Archivio','Pagine, schemi, widget|media e appuntamenti',TEAL),
 ('Importa','Scegli il file da locale|Verifica ZIP e antivirus',PURPLE),
 ('Nuova bozza','Nuovi ID e codice accesso|Originale invariato',TEAL)])
scene('workflow-live-presenter-user-rc286.png','EVENTO LIVE / SHARED SESSION WORKFLOW',[
 ('Prepara','Pagine, schema, QR code|e prove in anteprima',PURPLE),
 ('Avvia','Il pubblico entra tramite|codice, link o QR',TEAL),
 ('Interagisci','Domande, reazioni, voti|feedback delle risposte',PURPLE),
 ('Concludi','Controlla risultati,|retention e report',TEAL)])
scene('workflow-widget-context-rc286.png','MENU WIDGET / SCROLLABLE CONTEXT MENU',[
 ('Apri menu','Tasto destro del mouse|o pressione prolungata',PURPLE),
 ('Scorri','Usa touch, rotellina|o frecce: menu aperto',TEAL),
 ('V/F compatto','Seleziona V o F|per ogni opzione',PURPLE),
 ('Conferma','Chiudi con Esc|o clic fuori dal menu',TEAL)])
if __name__=='__main__':print('Created 6 source diagrams in',OUT)
