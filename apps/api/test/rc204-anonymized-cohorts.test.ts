import test from 'node:test';
import assert from 'node:assert/strict';
import {inflateRawSync} from 'node:zlib';
import {ANONYMOUS_MIN_PARTICIPANTS,exportStatisticRows,statisticsCsv,statisticsXlsx, type StatisticRecord} from '../src/statistics-export.ts';

const record=(participantId:string,answer:string,changes:Partial<StatisticRecord>={}):StatisticRecord=>({
 kind:'Risposta widget',page:'Pagina 1',question:'Domanda A',answer,correct:'',
 participantId,pseudonym:`Persona privata ${participantId}`,submittedAt:`2026-11-05T09:00:00Z`,...changes
});
const cohort=(answer:string,n:number)=>Array.from({length:n},(_,i)=>record(`test-participant-${i+1}`,answer));

test('RC204 anonymous exports suppress cohorts with fewer than five distinct participants',()=>{
 assert.equal(ANONYMOUS_MIN_PARTICIPANTS,5);
 for(let n=0;n<ANONYMOUS_MIN_PARTICIPANTS;n++){
  assert.deepEqual(exportStatisticRows(cohort('Sì',n),true),[]);
 }
 const rows=exportStatisticRows(cohort('Sì',5),true);
 assert.equal(rows.length,1);assert.equal(rows[0][3],'Sì');assert.equal(rows[0][5],'5');
 assert.deepEqual(rows[0].slice(6),['','','']);
});

test('RC204 repeat submissions cannot masquerade as independent respondents',()=>{
 const repeated=Array.from({length:200},()=>record('single-person','Sì'));
 assert.deepEqual(exportStatisticRows(repeated,true),[]);
 const oneUnknown=cohort('No',4).concat(record('','No'));
 assert.deepEqual(exportStatisticRows(oneUnknown,true),[]);
 const five=cohort('Sì',5).concat(repeated.map(r=>({...r,participantId:'test-participant-1'})));
 const rows=exportStatisticRows(five,true);
 assert.equal(rows.length,1);assert.equal(rows[0][5],'5'); // Count unique respondents, never raw repeated events
});

test('RC204 answer suppression is per question, kind, and answer, not across unrelated responses',()=>{
 const data=[...cohort('Sì',5),...cohort('No',3),...cohort('Sì',4).map(r=>({...r,question:'Domanda B'}))];
 const rows=exportStatisticRows(data,true);
 assert.equal(rows.length,1);assert.equal(rows[0][2],'Domanda A');assert.equal(rows[0][3],'Sì');
});

test('RC204 anonymous privacy guard covers private free text, file IDs, rating comments and CSV/XLSX bytes',()=>{
 const answers=cohort('=HYPERLINK("private")',5).map((r,i)=>({...r,isFreeText:true,participantId:`user-secret-${i}`,pseudonym:`name-${i}`,submittedAt:'private-time'}));
 const comment=answers.map(x=>({...x,kind:'Commento gradimento',answer:'very private feeling'}));
 const files=answers.map(x=>({...x,kind:'Allegato',answer:'private-file-asset-uuid'}));
 const rows=exportStatisticRows([...answers,...comment,...files],true);
 assert.equal(rows.length,3);
 assert.ok(rows.every(r=>r[3]==='[contenuto personale omesso]'));
 const csv=statisticsCsv(rows);
 const xlsx=statisticsXlsx(rows);
 for(const secret of ['user-secret-', 'name-', 'private-time', 'very private feeling', 'private-file-asset-uuid', 'HYPERLINK']){
  assert.ok(!csv.includes(secret),`CSV leaks ${secret}`);
  assert.ok(!xlsx.includes(Buffer.from(secret)),`XLSX leaks ${secret}`);
 }
});

test('RC204 named exports remain complete for authorized call path, independent of cohort size',()=>{
 const single=[record('single-person','=1+1')];
 const rows=exportStatisticRows(single,false);
 assert.equal(rows.length,1);
 assert.equal(rows[0][3],'=1+1');assert.equal(rows[0][6],'single-person');
 assert.match(statisticsCsv(rows),/"'=1\+1"/);
});

function unpackXlsxWorksheet(bytes:Buffer):string{
 let offset=0;
 while(offset<bytes.length-30&&bytes.readUInt32LE(offset)===0x04034b50){
  const method=bytes.readUInt16LE(offset+8),compressed=bytes.readUInt32LE(offset+18);
  const nameSize=bytes.readUInt16LE(offset+26),extraSize=bytes.readUInt16LE(offset+28);
  const name=bytes.subarray(offset+30,offset+30+nameSize).toString('utf8');
  const start=offset+30+nameSize+extraSize;
  if(name==='xl/worksheets/sheet1.xml'){
   assert.equal(method,8);
   return inflateRawSync(bytes.subarray(start,start+compressed)).toString('utf8');
  }
  offset=start+compressed;
 }
 throw new Error('missing spreadsheet XML');
}

test('RC204 XLSX worksheet contains only safe literal cells for released cohort counts',()=>{
 const rows=exportStatisticRows(cohort('=cmd|private',5),true);
 const worksheet=unpackXlsxWorksheet(statisticsXlsx(rows));
 assert.match(worksheet,/<c r="D2" t="inlineStr">/);
 assert.match(worksheet,/<t xml:space="preserve">=cmd\|private<\/t>/);
 assert.ok(!worksheet.includes('<f>'), 'No executable spreadsheet formulas are serialized');
 assert.ok(!worksheet.includes('test-participant-'));
 assert.match(worksheet,/<t xml:space="preserve">5<\/t>/);
});
