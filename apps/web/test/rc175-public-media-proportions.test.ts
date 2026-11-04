import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const participant=ui.slice(ui.indexOf('{joinPath?<main id="main-content"'),ui.indexOf('publicPath?<PresenterLiveScreen'));

test('RC175 participant image and video are media widgets, not intrinsic-size blocks',()=>{
 assert.match(participant,/w\.kind==='video'&&w\.assetId\?<video className="projection-media" controls/);
 assert.match(participant,/<CroppedImage className="projection-media"/);
 assert.match(css,/:is\(\.audience-widget-layout\.stage-fidelity,\.audience-widget-layout\.stage-phone\)[\s\S]*?>\.page-widget \.widget-fit-content > :is\(img\.projection-media,video\.projection-media\)\{[\s\S]*?height:100%!important/);
 assert.match(css,/>\.page-widget:is\(\[data-widget-kind="image"\],\[data-widget-kind="logo"\],\[data-widget-kind="video"\]\)[\s\S]*?>\.widget-fit-frame>\.widget-fit-content\{height:100%!important/);
});

test('RC175 reading mode remains independent of faithful media sizing',()=>{
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-reading\{\s*background:#fff!important;background-image:none!important/);
 assert.doesNotMatch(css,/\.audience-widget-layout\.stage-reading\)\s*>\.page-widget:is\(\[data-widget-kind="image"/);
});
