/** File picker MIME fallback is restricted to known extensions; server also verifies bytes. */
export function mediaUploadMime(file:{name:string;type:string},kind:string):string|null{
 const raw=file.type.toLowerCase().split(';')[0].trim();
 const fromName=/\.(jpe?g|png|gif|webp|pdf|mp4|webm)$/i.exec(file.name)?.[1]?.toLowerCase();
 const table:Record<string,string>={jpg:'image/jpeg',jpeg:'image/jpeg',png:'image/png',gif:'image/gif',webp:'image/webp',pdf:'application/pdf',mp4:'video/mp4',webm:'video/webm'};
 const normalized=raw==='image/jpg'||raw==='image/pjpeg'?'image/jpeg':raw;
 const supported=new Set(Object.values(table));
 // A browser can report a vendor MIME even for a valid .jpg/.png file.
 // The backend independently verifies bytes and cannot be bypassed.
 const fallbackAllowed=!normalized||normalized==='application/octet-stream'||normalized==='application/x-jpeg'||normalized==='image/x-jpeg';
 const mime=supported.has(normalized)?normalized:(fallbackAllowed?table[fromName||'']||'':normalized);
 return kind==='pdf'?(mime==='application/pdf'?mime:null):kind==='video'?(['video/mp4','video/webm'].includes(mime)?mime:null):kind==='asset'?(['image/jpeg','image/png','image/gif','image/webp','application/pdf','video/mp4','video/webm'].includes(mime)?mime:null):(['image/jpeg','image/png','image/gif','image/webp'].includes(mime)?mime:null);
}
