/** Display filenames for both independent views. Never interpolate user titles
 * directly into an HTTP header; RFC 5987 preserves accented session names. */
export type PresentationExportView='presenter'|'participant';
export type PresentationExportFormat='pdf'|'pptx';

export function presentationExportView(value:unknown):PresentationExportView|null{
 return value==='presenter'||value==='participant'?value:null;
}

export function exportFileName(title:unknown,view:PresentationExportView,format:PresentationExportFormat):string{
 const stem=(typeof title==='string'?title:'').normalize('NFKC')
  .replace(/[\x00-\x1f\x7f/\\<>:"|?*]+/g,'-')
  .replace(/\s+/g,' ').trim().replace(/^[. ]+|[. ]+$/g,'').slice(0,100).trim()||'Sessione';
 const role=view==='presenter'?'presentatore':'partecipante';
 return `${stem} - ${role}.${format}`;
}

export function presentationContentDisposition(title:unknown,view:PresentationExportView,format:PresentationExportFormat):string{
 const original=exportFileName(title,view,format);
 // Older browsers need an ASCII-safe fallback; UTF-8 clients use filename*.
 const ascii=original.normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
  .replace(/[^\x20-\x7e]/g,'_').replace(/["\\]/g,'_');
 return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(original)}`;
}
