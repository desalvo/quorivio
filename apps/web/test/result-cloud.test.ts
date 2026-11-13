import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
test('question widget offers persisted frequency cloud with explicit numeric counts',()=>{
 assert.match(src,/\['bars','pie','table','cloud','gauge','line','area','donut','radar'\]\.includes\(widget\.resultsView\)/);
 assert.match(src,/className="result-cloud-word"/);
 assert.match(src,/<small> \[\{count\}\]<\/small>/);
 assert.match(src,/Grafico risultati del widget<select/);
 assert.match(src,/<option value="cloud">Nuvola<\/option>/);
});
test('cloud remains supported and no separate legacy dialog picker is needed',()=>{
 assert.match(src,/aria-label="Visualizzazione risultati della domanda"/);
 assert.match(src,/value="cloud">Nuvola animata/);
 assert.match(src,/effectiveResultView\(control,widgets\)/);
 assert.doesNotMatch(src,/aria-label="Visualizzazione autonoma del widget Risultati"/);
});
