import test from 'node:test';
import assert from 'node:assert/strict';
import {applySelectionInlineStyle,selectionUniformValue,styledSegments,inlineMarkCss,type TextMark} from '../src/widget-text-marks.ts';
import {DEFAULT_TITLE_STYLE,newTitleWidget,newFooterWidget,widgetDisplay} from '../src/slide-master.ts';
import {readFileSync} from 'node:fs';
const text='Prima seconda terza';
const range={start:6,end:13};

test('RC95: bold is toggled off when highlighted title text inherits bold',()=>{
 const before:TextMark[]=[];
 assert.equal(selectionUniformValue(text,before,'label',range.start,range.end,DEFAULT_TITLE_STYLE,'bold'),true);
 const marks=applySelectionInlineStyle(before,'label',text,range.start,range.end,{bold:false});
 assert.equal(selectionUniformValue(text,marks,'label',range.start,range.end,DEFAULT_TITLE_STYLE,'bold'),false);
 assert.equal(selectionUniformValue(text,marks,'label',0,5,DEFAULT_TITLE_STYLE,'bold'),true);
 const on=applySelectionInlineStyle(marks,'label',text,range.start,range.end,{bold:true});
 assert.equal(selectionUniformValue(text,on,'label',range.start,range.end,DEFAULT_TITLE_STYLE,'bold'),true);
 assert.equal(styledSegments(text,on,'label').map(part=>part.text).join(''),text);
});

test('RC95: repeated italic, underline and strikethrough use explicit false overrides',()=>{
 let marks:TextMark[]=[];
 for(const field of ['italic','underline','strikethrough'] as const){
  marks=applySelectionInlineStyle(marks,'label',text,range.start,range.end,{[field]:true});
  assert.equal(selectionUniformValue(text,marks,'label',range.start,range.end,{},field),true);
  marks=applySelectionInlineStyle(marks,'label',text,range.start,range.end,{[field]:false});
  assert.equal(selectionUniformValue(text,marks,'label',range.start,range.end,{},field),false);
 }
 assert.equal(inlineMarkCss({underline:false,strikethrough:false}).textDecoration,'none');
});

test('RC95: font family, size and color target ONLY highlighted characters and preserve other fields',()=>{
 const initial:TextMark[]=[{field:'description',start:0,end:4,style:{bold:true}}];
 const next=applySelectionInlineStyle(initial,'label',text,range.start,range.end,{fontFamily:'Georgia',fontSize:35,color:'#123456'});
 assert.deepEqual(next.filter(m=>m.field==='description'),initial);
 assert.equal(selectionUniformValue(text,next,'label',range.start,range.end,{},'fontFamily'),'Georgia');
 assert.equal(selectionUniformValue(text,next,'label',range.start,range.end,{},'fontSize'),35);
 assert.equal(selectionUniformValue(text,next,'label',range.start,range.end,{},'color'),'#123456');
 assert.equal(selectionUniformValue(text,next,'label',0,5,{fontFamily:'Arial'},'fontFamily'),'Arial');
});

test('RC95: partial selection across mixed bold runs is not presented as uniformly bold',()=>{
 const marks=[{field:'label',start:6,end:10,style:{bold:true}}];
 assert.equal(selectionUniformValue(text,marks,'label',6,13,{},'bold'),undefined);
 assert.equal(selectionUniformValue(text,marks,'label',6,10,{},'bold'),true);
});

test('RC95: changes to adjacent regions coalesce; invalid ranges are rejected',()=>{
 let marks:TextMark[]=[];
 for(let i=0;i<5;i++)marks=applySelectionInlineStyle(marks,'label',text,6,13,{italic:i%2===0});
 assert.equal(marks.length,1);
 assert.equal(marks[0].style.italic,true);
 assert.deepEqual(applySelectionInlineStyle(marks,'label',text,-1,100,{bold:true}),marks);
});

test('RC95: default title is 24px bold black, without fill or border',()=>{
 const title=newTitleWidget('Titolo');
 assert.equal(DEFAULT_TITLE_STYLE.fontSize,24);
 assert.equal(DEFAULT_TITLE_STYLE.bold,true);
 assert.equal(DEFAULT_TITLE_STYLE.color,'#000000');
 assert.equal(title.style?.fillNone,true);
 assert.equal(title.style?.strokeNone,true);
 assert.equal(widgetDisplay(title,{pageTitle:'Prova'}).style.fontSize,24);
 const footer=newFooterWidget('f');
 assert.equal(footer.style?.fillNone,true);
});

test('RC95: ribbon is divided into functional groups with toggles tied to selected text',()=>{
 const code=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 for(const section of ['Carattere','Paragrafo','Formato forma','Disponi'])assert.ok(code.includes(`aria-label="${section}"`),section);
 for(const flag of ['bold','italic','underline','strikethrough'])assert.ok(code.includes(`setStyle({${flag}:!selectedFlag('${flag}')})`),flag);
 assert.ok(code.includes("kind==='title'?newTitleWidget(pageTitle||'Titolo')"));
 assert.ok(code.includes('onMouseDownCapture={e=>{if((e.target as HTMLElement).closest("button"))e.preventDefault()}}'));
 assert.ok(css.includes('.palette-ribbon-groups'));
});
