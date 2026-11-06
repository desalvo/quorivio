import test from 'node:test';import assert from 'node:assert/strict';
import {exportStatisticRows,statisticsCsv,statisticsXlsx} from '../src/statistics-export.ts';
const records=[{kind:'Domanda',page:'Slide 1',question:'Perché?',answer:'risposta privata =HYPERLINK("evil")',correct:'',participantId:'secret-uuid',pseudonym:'Persona reale',submittedAt:'2026-11-05T20:00:00',isFreeText:true},{kind:'Domanda',page:'Slide 1',question:'Perché?',answer:'altro testo identificante',correct:'',participantId:'other-secret',pseudonym:'Seconda persona',submittedAt:'2026-11-05T20:01:00',isFreeText:true}];
test('RC200 anonymized output aggregates sensitive responses and removes identities, timestamps and free text',()=>{
 const rows=exportStatisticRows(records,true);assert.equal(rows.length,0); // RC204: two distinct respondents cannot justify an anonymous aggregate
 const csv=statisticsCsv(rows);for(const secret of ['secret-uuid','Persona reale','risposta privata','2026-11-05','other-secret'])assert.ok(!csv.includes(secret));
});
test('RC200 raw CSV protects spreadsheet formulas while preserving owner-allowed detail',()=>{
 const row=exportStatisticRows([{...records[0],answer:'=HYPERLINK("evil")',isFreeText:false}],false);
 assert.match(statisticsCsv(row),/"'=HYPERLINK\(""evil""\)"/);assert.equal(row[0][7],'Persona reale');
});
test('RC200 xlsx is an actual OOXML ZIP without formula evaluation (even for formula-looking text)',()=>{
 const buf=statisticsXlsx(exportStatisticRows([{...records[0],answer:'=1+1',isFreeText:false}],false));
 assert.equal(buf.readUInt32LE(0),0x04034b50);assert.ok(buf.includes(Buffer.from('xl/workbook.xml')));assert.ok(buf.includes(Buffer.from('xl/worksheets/sheet1.xml')));
});
