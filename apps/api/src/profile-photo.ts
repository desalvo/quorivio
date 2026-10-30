/** Accept only server-minted photo locations before removing a previous file.
 * Never use untrusted URL segments as filesystem paths. */
export function profilePhotoId(url:unknown):string|null{
 if(typeof url!=='string')return null;
 const match=/^\/api\/auth\/profile\/photo\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$/i.exec(url);
 return match?match[1]:null;
}

/** Public session profile projection: expose only session-scoped photo URLs,
 * never the private authenticated photo endpoint or extra user columns. */
export function publicPresenterProfiles(rows:ReadonlyArray<{id:string;name:string;email?:string;profile_photo_url:unknown}>,code:string,publicEmailIds:ReadonlySet<string>=new Set()){
 return rows.map(row=>({
  id:row.id,
  name:row.name,
  ...(publicEmailIds.has(row.id)&&typeof row.email==='string'?{email:row.email}:{}),
  photo_url:profilePhotoId(row.profile_photo_url)
   ?`/api/join/${encodeURIComponent(code)}/presenters/${encodeURIComponent(row.id)}/photo`
   :null
 }));
}
