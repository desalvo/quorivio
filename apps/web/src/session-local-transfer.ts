/** UI-only preflight for the self-contained session format. The API revalidates
 * archive entries, MIME signatures, digests, ownership and ClamAV on import. */
export const LOCAL_SESSION_ARCHIVE_MIME='application/vnd.quorivio.session+zip';
export const LOCAL_SESSION_ARCHIVE_MAX_BYTES=100*1024*1024;

export function localSessionArchiveFilename(title:unknown):string{
 const base=String(title||'sessione').normalize('NFKC')
  .replace(/[\\/:*?"<>|\x00-\x1f\x7f.]/g,'-')
  .replace(/-{2,}/g,'-')
  .replace(/[.\s-]+$/g,'').trim().slice(0,90);
 return `quorivio-${base||'sessione'}.quo`;
}

export function localSessionImportError(file:{name:string;size:number}|null|undefined):string|null{
 if(!file)return 'Seleziona un archivio .quo.';
 if(!file.name.toLowerCase().endsWith('.quo'))return 'Formato non valido: seleziona un archivio .quo.';
 if(!Number.isSafeInteger(file.size)||file.size<22)return 'L’archivio selezionato è vuoto o non valido.';
 if(file.size>LOCAL_SESSION_ARCHIVE_MAX_BYTES)return 'Archivio superiore al limite di 100 MiB.';
 return null;
}

export function isLocalSessionArchiveMime(contentType:string|null):boolean{
 return contentType?.split(';',1)[0].trim().toLowerCase()===LOCAL_SESSION_ARCHIVE_MIME;
}
