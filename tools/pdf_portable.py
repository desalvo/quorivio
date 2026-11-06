#!/usr/bin/env python3
"""Bounded, partial PDF-to-editable session import in the isolated converter.

Use Poppler's XML geometry for native text and embedded raster pictures. Complex
vector paths, fonts and annotations are NOT reconstructed; no OCR or scripting.
"""
from datetime import date
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pptx_portable import _supported_image

MAX_BYTES=50*1024*1024
MAX_XML_BYTES=15*1024*1024

def _run(args,timeout=120):
 try:
  result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,timeout=timeout,check=False)
 except (OSError,subprocess.TimeoutExpired) as exc:
  raise ValueError('PDF extraction unavailable') from exc
 if result.returncode:
  raise ValueError('PDF extraction failed')

def pdf_to_portable(source,media_dir=None):
 source=Path(source)
 if source.is_symlink() or not source.is_file() or not 8<=source.stat().st_size<=MAX_BYTES:
  raise ValueError('Invalid PDF source size')
 with source.open('rb') as stream:
  if stream.read(5)!=b'%PDF-':raise ValueError('PDF signature missing')
 if media_dir is not None:
  dest=Path(media_dir)
  if dest.exists() or any(item.is_symlink() for item in (dest,*dest.parents)):
   raise ValueError('Unsafe media folder')
  dest.mkdir(mode=0o700)
 with tempfile.TemporaryDirectory(prefix='pdf-text-') as scratch:
  root=Path(scratch)
  out=root/'pages'
  _run(['pdftohtml','-xml','-hidden','-enc','UTF-8',str(source),str(out)])
  xml=root/'pages.xml'
  if xml.is_symlink() or not xml.is_file() or xml.stat().st_size>MAX_XML_BYTES:
   raise ValueError('Invalid or oversized PDF text extraction')
  # ElementTree never resolves external DTDs; reject document entity extensions.
  content=xml.read_bytes()
  if b'<!ENTITY' in content.upper():raise ValueError('Unsafe PDF XML')
  doc=ET.fromstring(content)
  pages=doc.findall('page')
  if not 1<=len(pages)<=200:raise ValueError('Unsupported PDF page count')
  assets=[];activities=[];text_count=0;image_count=0;omitted=0;total_media=0
  for i,page in enumerate(pages):
   width=float(page.attrib.get('width','0'));height=float(page.attrib.get('height','0'))
   if not 100<=width<=20000 or not 100<=height<=20000:raise ValueError('Invalid PDF page geometry')
   fonts={node.attrib.get('id'):{'size':node.attrib.get('size','16'),'color':node.attrib.get('color','#000000'),'family':node.attrib.get('family','Arial')} for node in page.findall('fontspec')}
   widgets=[];title=None
   def position(node):
    a=node.attrib
    try: x=float(a.get('left','0'))/width*100;y=float(a.get('top','0'))/height*100;w=float(a.get('width','0'))/width*100;h=float(a.get('height','0'))/height*100
    except ValueError:return None
    if not all(map(lambda v:float('-inf')<v<float('inf'),(x,y,w,h))):return None
    if x<0 or y<0 or x>=100 or y>=99:return None
    x=round(min(99.9,max(0,x)),3);y=round(min(98.9,max(0,y)),3)
    w=round(min(100-x,max(.01,w)),3);h=round(min(100-y,max(.01,h)),3)
    return {'x':x,'y':y,'width':w,'height':h}
   for child in page:
    if child.tag not in ('text','image'):continue
    if len(widgets)>=16:omitted+=1;continue
    pos=position(child)
    if pos is None:omitted+=1;continue
    if child.tag=='text':
     text=''.join(child.itertext()).strip()
     if not text:continue
     if len(text)>500:text=text[:500];omitted+=1
     if title is None:title=text[:160]
     font=fonts.get(child.attrib.get('font'),{})
     try:size=max(8,min(96,round(float(font.get('size',16))/1.5)))
     except ValueError:size=16
     color=font.get('color','#000000')
     if not re.fullmatch(r'#[a-fA-F0-9]{6}',color):color='#000000'
     family=font.get('family','Arial')
     family=next((f for f in ('Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace') if f.lower() in family.lower()),'Arial')
     widgets.append({'id':f'pdf_{i+1}_{len(widgets)+1}','kind':'text','label':text[:240],
                     'description':text,'position':pos,'style':{'fontFamily':family,'fontSize':size,'color':color}})
     text_count+=1
    else:
     if media_dir is None:omitted+=1;continue
     filename=Path(child.attrib.get('src','')).name  # Poppler can emit absolute filenames; read ONLY from our scratch root
     if not re.fullmatch(r'pages-[0-9_]+\.(png|jpg|jpeg)',filename,re.I):omitted+=1;continue
     image=root/filename
     if image.is_symlink() or not image.is_file():omitted+=1;continue
     blob=image.read_bytes();mime='image/png' if filename.lower().endswith('.png') else 'image/jpeg'
     if not _supported_image(blob,mime) or len(assets)>=200 or total_media+len(blob)>MAX_BYTES:omitted+=1;continue
     digest=hashlib.sha256(blob).hexdigest();asset=next((item for item in assets if item['sha256']==digest and item['mime']==mime),None)
     if asset is None:
      aid=str(uuid.uuid4());(dest/aid).write_bytes(blob);os.chmod(dest/aid,0o600)
      asset={'id':aid,'mime':mime,'bytes':len(blob),'sha256':digest};assets.append(asset);total_media+=len(blob)
     widgets.append({'id':f'pdf_{i+1}_{len(widgets)+1}','kind':'image','label':'Immagine PDF','assetId':asset['id'],'position':pos})
     image_count+=1
   activities.append({'type':'slide','title':title or f'Pagina PDF {i+1}','options':[],
                      'correct_option_id':None,'correct_option_ids':[],
                      'answer_mode':'text','answer_required':False,'duration_seconds':None,
                      'page_design':{'widgets':widgets},'result_design':{}})
 return ({'format':'quorivio-session','version':1,
         'session':{'title':source.stem[:160] or 'PDF importato','reference_date':date.today().isoformat(),
                    'theme':{},'allow_anonymous':True,'show_results':False},
         'activities':activities,'import_assets':assets},
        {'page_count':len(activities),'editable_text_boxes':text_count,'editable_images':image_count,
         'omitted_elements':omitted,'limited_fidelity':True,'ocr_performed':False})
