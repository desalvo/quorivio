import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const participant=ui.slice(ui.indexOf('{joinPath?<main id="main-content"'),ui.indexOf('publicPath?<PresenterLiveScreen'));

test('RC266 inherited RC173 background contract follows the current canvas spread',()=>{
 assert.match(participant,/style=\{\{backgroundColor:"transparent",backgroundImage:"none"\}\}/,'outer participant wrapper must have no background');
 assert.match(participant,/\.\.\.slideBackgroundCss\(entry\.activity\.page_design,entry\.theme,/,'the stage must paint the authored background');
 assert.equal((participant.match(/slideBackgroundCss\(entry\.activity\.page_design/g)||[]).length,1,'background must be painted exactly once');
 assert.match(participant,/audiencePortrait&&!entry\.activity\.page_design\?\.importedImageFit\?/,'imported full-canvas images must not be replaced by the phone fallback background');
 assert.match(participant,/participantReadingMode\?\{backgroundImage:"none",backgroundColor:"#ffffff",backgroundSize:"auto"\}/,'accessible reading mode must keep white background');
});

test('RC266 full-canvas imports suppress master widgets consistently for both audience and presenter',()=>{
 assert.match(ui,/const audienceAuthoredWidgets=entry\?\.activity\?\(entry\.activity\.page_design\?\.suppressMaster\?/);
 assert.match(participant,/<SlideCanvasNumber widgets=\{entry\.activity\.page_design\?\.suppressMaster\?/);
 assert.match(ui,/const widgets=activity\.page_design\?\.suppressMaster\?/);
 assert.match(ui,/const presenterWidgets=activity\?\.page_design\?\.suppressMaster\?/);
});
