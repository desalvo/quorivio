/** Single-flight polling: no overlapping fetches or updates after disposal. */
export function createLiveResultPoller<T>(load:()=>Promise<T>,onSuccess:(value:T)=>void,onError:(error:unknown)=>void){
 let stopped=false, busy=false;
 const refresh=async ():Promise<boolean>=>{
  if(stopped||busy)return false;
  busy=true;
  try{const value=await load();if(!stopped)onSuccess(value)}
  catch(error:unknown){if(!stopped)onError(error)}
  finally{busy=false}
  return true;
 };
 return {refresh,stop:()=>{stopped=true}};
}
