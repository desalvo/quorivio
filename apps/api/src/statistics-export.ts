/** RC200: privacy-scoped statistics export, with dependency-free spreadsheet encoding.
 * An anonymized export is aggregated: it never retains participant IDs, pseudonyms,
 * exact timestamps, attachment IDs or free-text content that can identify a person.
 */
import {deflateRawSync} from 'node:zlib';
// Independent CRC32: report exports must remain testable without the bundle parser.
const CRC_TABLE=Array.from({length:256},(_,i)=>{let c=i;for(let j=0;j<8;j++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0});
function crc32(bytes:Uint8Array):number{let c=0xffffffff;for(const b of bytes)c=CRC_TABLE[(c^b)&255]^(c>>>8);return(c^0xffffffff)>>>0;}

export type StatisticRecord={kind:string;page:string;question:string;answer:string;correct:string;participantId:string;pseudonym:string;submittedAt:string;count?:number;isFreeText?:boolean};
export const STAT_COLUMNS=['Tipo','Pagina','Domanda/widget','Risposta','Corretta','Conteggio','ID partecipante','Pseudonimo','Data e ora'] as const;
const omitted='[contenuto personale omesso]';
const safeText=(v:unknown)=>String(v??'').slice(0,32000);

export function exportStatisticRows(records:StatisticRecord[],anonymize:boolean):string[][]{
 if(!anonymize)return records.map(x=>[x.kind,x.page,x.question,x.answer,x.correct,String(x.count||1),x.participantId,x.pseudonym,x.submittedAt].map(safeText));
 const grouped=new Map<string,{kind:string;page:string;question:string;answer:string;correct:string;count:number}>();
 for(const x of records){
  // Never leak free text, uploaded media identifiers, or participant-linked metadata.
  const answer=x.isFreeText?omitted:x.answer;
  const key=JSON.stringify([x.kind,x.page,x.question,answer,x.correct]);
  const found=grouped.get(key);
  if(found)found.count+=x.count||1;
  else grouped.set(key,{kind:x.kind,page:x.page,question:x.question,answer,correct:x.correct,count:x.count||1});
 }
 return [...grouped.values()].map(x=>[x.kind,x.page,x.question,x.answer,x.correct,String(x.count),'','',''].map(safeText));
}
export function escapeSpreadsheetCsv(v:unknown):string{
 const raw=safeText(v);
 // Protect applications that evaluate CSV content as formulas, also after whitespace.
 const guarded=/^[\s\u0000-\u001f]*[=+@-]/u.test(raw)?"'"+raw:raw;
 return '"'+guarded.replace(/"/g,'""')+'"';
}
export function statisticsCsv(rows:string[][]):string{
 return '\uFEFF'+[STAT_COLUMNS,...rows].map(row=>row.map(escapeSpreadsheetCsv).join(',')).join('\r\n')+'\r\n';
}
function xml(v:unknown):string{
 // Invalid XML 1.0 characters cannot be serialized in worksheet text.
 return safeText(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\uFFFE\uFFFF]/g,'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');
}
function cell(col:number,row:number,value:string,heading:boolean):string{
 let n=col+1,letters='';while(n){n--;letters=String.fromCharCode(65+n%26)+letters;n=Math.floor(n/26)}
 // Inline strings are deliberately NOT formulas, irrespective of their leading characters.
 return `<c r="${letters}${row}" t="inlineStr"${heading?' s="1"':''}><is><t xml:space="preserve">${xml(value)}</t></is></c>`;
}
function zipFiles(files:[string,Buffer][]):Buffer{
 const chunks:Buffer[]=[],dir:Buffer[]=[];let offset=0;
 for(const [name,bytes] of files){const filename=Buffer.from(name),packed=deflateRawSync(bytes,{level:6}),sum=crc32(bytes);
  const local=Buffer.alloc(30);local.writeUInt32LE(0x04034b50,0);local.writeUInt16LE(20,4);local.writeUInt16LE(8,8);local.writeUInt32LE(sum,14);local.writeUInt32LE(packed.length,18);local.writeUInt32LE(bytes.length,22);local.writeUInt16LE(filename.length,26);
  const central=Buffer.alloc(46);central.writeUInt32LE(0x02014b50,0);central.writeUInt16LE(20,4);central.writeUInt16LE(20,6);central.writeUInt16LE(8,10);central.writeUInt32LE(sum,16);central.writeUInt32LE(packed.length,20);central.writeUInt32LE(bytes.length,24);central.writeUInt16LE(filename.length,28);central.writeUInt32LE(offset,42);
  chunks.push(local,filename,packed);dir.push(central,filename);offset+=local.length+filename.length+packed.length;
 }
 const size=dir.reduce((n,b)=>n+b.length,0),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(files.length,8);end.writeUInt16LE(files.length,10);end.writeUInt32LE(size,12);end.writeUInt32LE(offset,16);
 return Buffer.concat([...chunks,...dir,end]);
}
export function statisticsXlsx(rows:string[][]):Buffer{
 if(rows.length>50000)throw Error('statistics_export_row_limit');
 const values=[Array.from(STAT_COLUMNS),...rows];
 const worksheet=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${[18,32,34,42,12,13,40,26,25].map((width,i)=>`<col min="${i+1}" max="${i+1}" width="${width}" customWidth="1"/>`).join('')}</cols><sheetData>${values.map((r,i)=>`<row r="${i+1}">${r.map((v,j)=>cell(j,i+1,v,i===0)).join('')}</row>`).join('')}</sheetData><autoFilter ref="A1:I${values.length}"/></worksheet>`;
 const contentTypes='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>';
 const relationships='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>';
 const workbook='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Statistiche" sheetId="1" r:id="rId1"/></sheets></workbook>';
 const workbookRels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>';
 const styles='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Arial"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Arial"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF173A55"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs></styleSheet>';
 return zipFiles([['[Content_Types].xml',Buffer.from(contentTypes)],['_rels/.rels',Buffer.from(relationships)],['xl/workbook.xml',Buffer.from(workbook)],['xl/_rels/workbook.xml.rels',Buffer.from(workbookRels)],['xl/worksheets/sheet1.xml',Buffer.from(worksheet)],['xl/styles.xml',Buffer.from(styles)]]);
}
