#!/usr/bin/env python3
"""Reproducible demonstration charts and process diagrams for Quorivio manuals.
Sample data is invented for explanation and prominently labelled as such.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets/manual-illustrations'
OUT.mkdir(parents=True,exist_ok=True)
try: import matplotlib; matplotlib.use('Agg');import matplotlib.pyplot as plt
except ImportError:plt=None
if plt:
 data=[72,43,20];labels=['Option A','Option B','Option C'];colors=['#5b57d5','#36a48d','#f29b64']
 fig,ax=plt.subplots(figsize=(11,5));bars=ax.barh(labels[::-1],data[::-1],color=colors[::-1]);ax.set_xlim(0,85);ax.grid(axis='x',alpha=.13)
 for bar,n in zip(bars,data[::-1]):ax.text(bar.get_width()+1,bar.get_y()+bar.get_height()/2,f'{n} hits',va='center')
 ax.set_title('Response counts – example data only',weight='bold',fontsize=15,pad=14)
 ax.set_xlabel('Responses');fig.tight_layout();fig.savefig(OUT/'sample-bar-chart.png',dpi=140);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,5.2));ax.pie(data,labels=[f'{i+1}. {labels[i]}' for i in range(3)],colors=colors,autopct='%1.1f%%',pctdistance=.7,startangle=90)
 ax.set_title('Pie result – example data only',weight='bold',fontsize=15,pad=13);fig.tight_layout();fig.savefig(OUT/'sample-pie-chart.png',dpi=140);plt.close(fig)

try:
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
    big=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except:font=big=small=ImageFont.load_default()

def flow(name,title,nodes,note):
 im=Image.new('RGB',(1460,460),'#f5f6fc');d=ImageDraw.Draw(im);d.text((50,25),title,font=big,fill='#24315e')
 for i,(head,body) in enumerate(nodes):
  x=48+i*355
  d.rounded_rectangle((x,100,x+320,325),radius=20,fill='#ffffff',outline='#cdd1eb',width=2)
  d.rounded_rectangle((x,100,x+320,155),radius=18,fill='#5d52cc')
  d.text((x+20,111),head,font=font,fill='white')
  import textwrap
  for j,line in enumerate(textwrap.wrap(body,30)):
   d.text((x+17,180+j*32),line,font=small,fill='#34405e')
  if i<3:
   d.line((x+320,220,x+350,220),fill='#5d52cc',width=4)
   d.polygon([(x+347,212),(x+356,220),(x+347,228)],fill='#5d52cc')
 d.text((48,386),note,font=small,fill='#647186')
 im.save(OUT/name)
flow('backup-lifecycle.png','Full-instance backup and recovery — conceptual workflow',[
 ('1. Source','PostgreSQL database and private assets'),
 ('2. Create','Custom dump, tar archive, manifest and checksums'),
 ('3. Store','POSIX, NFS, S3 or WebDAV with external encryption/retention'),
 ('4. Verify','Restore on isolated staging and check data consistency')
 ],'Diagram only: the backup and asset snapshot is not atomic; restore is operator-driven.')
flow('ldap-approval.png','LDAP self-registration — authorization boundary',[
 ('1. Credentials','User enters an LDAP login and valid password'),
 ('2. Bind','Quorivio verifies credentials against the directory'),
 ('3. Pending','Account is created with approved = false; admins notified'),
 ('4. Approve','Administrator verifies identity and assigns the role')
 ],'Valid LDAP credentials do not grant access before administrator approval.')
print('Manual diagrams ready')
