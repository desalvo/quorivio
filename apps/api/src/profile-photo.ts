/** Accept only server-minted photo locations before removing a previous file.
 * Never use untrusted URL segments as filesystem paths. */
export function profilePhotoId(url:unknown):string|null{
 if(typeof url!=='string')return null;
 const match=/^\/api\/auth\/profile\/photo\/([0-9a-f]{8}-[0-9a-f-]{27,})$/i.exec(url);
 return match?match[1]:null;
}
