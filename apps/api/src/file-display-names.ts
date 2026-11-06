/** Human-facing names are metadata only; file paths always use opaque UUIDs. */
export function normalizedFileName(raw:unknown,fallback:string):string {
 if(typeof raw!=='string'||!raw.trim())return fallback;
 const name=raw.replace(/\\/g,'/').split('/').pop()!.replace(/[\x00-\x1f\x7f]/g,'').trim();
 return name.slice(0,120).trim()||fallback;
}
export function numberedFileName(name:string,n:number):string {
 if(!Number.isInteger(n)||n<1||n>9999)throw Error('invalid_suffix');
 const dot=name.lastIndexOf('.');const ext=dot>0?name.slice(dot):'';const base=dot>0?name.slice(0,dot):name;
 const suffix=` (${n})`;return base.slice(0,120-ext.length-suffix.length)+suffix+ext;
}
export async function findAvailableFileName(name:string,exists:(name:string)=>Promise<boolean>):Promise<{duplicate:boolean;name:string}> {
 if(!await exists(name))return {duplicate:false,name};
 for(let n=2;n<=9999;n++){const candidate=numberedFileName(name,n);if(!await exists(candidate))return {duplicate:true,name:candidate}}
 throw Error('filename_namespace_full');
}
