import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
test('question widget offers persisted frequency cloud with explicit numeric counts',()=>{
 assert.match(src,/\['bars','pie','table','cloud'\]\.includes\(widget\.resultsView\)/);
 assert.match(src,/className="result-cloud-word"/);
 assert.match(src,/<small> \{count\}<\/small>/);
 assert.match(src,/Grafico risultati del widget<select/);
 assert.match(src,/<option value="cloud">Nuvola<\/option>/);
});
test('aggregate results control does not offer unsupported cloud mode',()=>{
 const field=src.split('Visualizzazione risultati<select')[1].split('</select>')[0];
 assert.doesNotMatch(field,/value="cloud"/);
});
