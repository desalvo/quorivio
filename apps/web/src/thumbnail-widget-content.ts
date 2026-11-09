/** Compact factual rendering model for real authoring-page thumbnails.
 * This only reads the widget definition; never queries or invents live results.
 * It is safe for a 100px preview, including unsaved widget changes. */
export type ThumbnailWidgetModel={
 type:'choice'|'chart'|'timer'|'rating'|'reaction'|'qr'|'media'|'line'|'shape'|'text'|'title'|'footer'|'postit'|'other';
 label:string;options:string[];multi:boolean;timer?:string;description?:string;isImage?:boolean;
};
function plain(value:unknown,max=200){return typeof value==='string'?value.replace(/\s+/g,' ').trim().slice(0,max):''}
export function thumbnailWidgetModel(widget:any):ThumbnailWidgetModel{
 const kind=plain(widget?.kind,40);
 const label=plain(widget?.label||widget?.title||'',220);
 const base={label:label||kind||'Widget',options:[] as string[],multi:false,description:undefined as string|undefined};
 const options=(Array.isArray(widget?.options)?widget.options:[]).slice(0,6).map((x:any)=>plain(x?.label||x?.text||'',120)).filter(Boolean);
 if(kind==='question'||kind==='timed-quiz'){
  const independent=Array.isArray(widget?.questions)?widget.questions:[];
  const first=independent[0];
  const mainOptions=options.length?options:(Array.isArray(first?.options)?first.options:[]).slice(0,6).map((x:any)=>plain(x?.label||'',120)).filter(Boolean);
  const mode=widget.answerMode||first?.answerMode||'text';
  return {...base,type:'choice',label:label||plain(first?.label)||'Domanda',options:mainOptions.length?mainOptions:[mode==='file'?'Allegato':'Risposta libera'],multi:mode==='multiple'};
 }
 if(kind==='results-button'||kind==='results'||kind==='chart'||kind==='poll'||kind==='statistics')return {...base,type:'chart',label:label||'Risultati'};
 if(kind==='timer'){const seconds=Math.max(0,Math.floor(Number(widget.durationSeconds)||60));return {...base,type:'timer',label:label||'Timer',timer:`${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`}}
 if(kind==='rating')return {...base,type:'rating',label:label||'Gradimento'};
 if(kind==='reactions')return {...base,type:'reaction',label:label||'Reazioni'};
 if(kind==='qrcode'||kind==='qr-code'||kind==='qr')return {...base,type:'qr',label:label||'Codice QR'};
 if(['image','logo','video','pdf'].includes(kind))return {...base,type:'media',label:label||kind.toUpperCase(),isImage:kind==='image'||kind==='logo'};
 if(kind==='line'||kind==='shape')return {...base,type:kind};
 if(kind==='title'||kind==='footer'||kind==='postit'||kind==='text')return {...base,type:kind,description:plain(widget?.description,95)};
 if(kind==='profile')return {...base,type:'other',label:label||'Presentatore',description:plain(widget?.description,95)};
 if(kind==='participants')return {...base,type:'other',label:label||'Partecipanti'};
 if(kind==='topic-question')return {...base,type:'other',label:label||'Domande aperte'};
 return {...base,type:'other'};
}
