/** Safe, owner-private demonstration template for an explicitly authorized 500-answer trial. */
export const LOAD_DEMO_KEY = 'load-500-v1';
export const LOAD_DEMO_TITLE = 'Quorivio · Prova tecnica 500 partecipanti';
export const LOAD_DEMO_QUESTION = 'Prova 500 risposte: quale funzionalità vuoi esplorare?';
export const LOAD_DEMO_ACTIVITY_TYPE = 'poll';
export const LOAD_DEMO_OPTIONS = [
  {id: 'live', label: 'Sondaggi in diretta'},
  {id: 'quiz', label: 'Quiz interattivi'},
  {id: 'questions', label: 'Domande dal pubblico'},
] as const;
const title = (label: string) => ({id:'load-500-title', kind:'title', label,
  titleFollowPage: true, titleUseMaster: true,
  style:{fontFamily:'Arial',fontSize:27,bold:true,color:'#0f2741',fillNone:true,strokeNone:true},
  position:{x:7,y:5,width:86,height:15,rotation:0}});
// Each page is deliberately a valid editable page; no runtime session is started.
const counter=(id:string,x=72,y=20)=>({id,kind:'participant-count',label:'Utenti connessi',showTitle:true,
 style:{fontFamily:'Arial',fontSize:18,fillNone:false,fillColor:'#e0f2fe',color:'#075985'},
 position:{x,y,width:22,height:17,rotation:0}});
const rating=(id:string,y:number)=>({id,kind:'rating',label:'Quanto valuti la prova?',targetKind:'session',
 style:{fontFamily:'Arial',fontSize:17,fillNone:true},position:{x:71,y,width:22,height:24,rotation:0}});
const reactions=(id:string,x:number,y:number,w:number)=>({id,kind:'reactions',label:'Reazioni in tempo reale',reactionIconSize:32,
 style:{fontFamily:'Arial',fontSize:16,fillNone:true},position:{x,y,width:w,height:18,rotation:0}});
export function loadDemoPages(){
 return [
  {type:'slide',title:'Benvenuto · prova tecnica 500 partecipanti',options:[],
   page_design:{backgroundColor:'#edf5ff',widgets:[title('Prova tecnica Quorivio'),
    {id:'load-500-guide',kind:'text',label:'Sessione di collaudo, dati sintetici. Avvia la presentazione, apri la pagina successiva e confronta il contatore utenti con il report CLI. Puoi resettare i risultati e ripetere il test.',
     style:{fontFamily:'Arial',fontSize:21,color:'#1f3b59',fillNone:true},position:{x:8,y:28,width:57,height:44,rotation:0}},
    counter('load-500-intro-presence'),reactions('load-500-intro-reactions',8,75,63)]}},
  {type:'poll',title:LOAD_DEMO_QUESTION,options:LOAD_DEMO_OPTIONS,
   page_design:{backgroundColor:'#f8fafc',widgets:[title(LOAD_DEMO_QUESTION),
    {id:'load-500-question',kind:'question',label:LOAD_DEMO_QUESTION,
     answerMode:'single',required:true,options:LOAD_DEMO_OPTIONS,
     style:{fontFamily:'Arial',fontSize:22,color:'#112b4c',fillNone:true},
     position:{x:8,y:24,width:58,height:42,rotation:0}},
    counter('load-500-poll-presence'),rating('load-500-poll-rating',42),
    reactions('load-500-poll-reactions',8,72,46),
    {id:'load-500-results',kind:'results-button',label:'Risultati della domanda',targetWidgetId:'load-500-question',
     resultsView:'bars',showTitle:false,resultsOnly:true,
     style:{fontFamily:'Arial',fontSize:18,fillNone:true},position:{x:57,y:72,width:36,height:20,rotation:0}}]}},
  {type:'poll',title:'Prova facoltativa · seconda domanda',options:[
   {id:'clear',label:'Chiarezza della domanda'},{id:'speed',label:'Velocità dei risultati'},
   {id:'layout',label:'Layout smartphone'}],
   page_design:{backgroundColor:'#f1f5f9',widgets:[title('Seconda domanda e gradimento'),
    {id:'load-500-extra-question',kind:'question',label:'Quale aspetto desideri verificare?',answerMode:'single',required:true,
     options:[{id:'clear',label:'Chiarezza della domanda'},{id:'speed',label:'Velocità dei risultati'},{id:'layout',label:'Layout smartphone'}],
     style:{fontFamily:'Arial',fontSize:22,fillNone:true},position:{x:8,y:25,width:59,height:42,rotation:0}},
    counter('load-500-extra-presence'),rating('load-500-extra-rating',43),
    reactions('load-500-extra-reactions',8,74,55)]}}
 ];
}
