/** Filesystem capacity monitoring for the app asset PVC and PostgreSQL data PVC.
 * PostgreSQL pg_database_size() is NOT a filesystem capacity metric: WAL, other
 * databases and filesystem overhead make it unsuitable for 90% alerts. */
import {statfs} from 'node:fs/promises';

export const DISK_ALERT_THRESHOLD_PERCENT=90;
export const DISK_ALERT_RECOVERY_PERCENT=85;
export const DB_DISK_SAMPLE_MAX_AGE_SECONDS=900;
export const DISK_MONITOR_INTERVAL_MS=300_000;
export type DiskVolume='application'|'conversion'|'database';
export type DiskReading={status:'ok'|'warning'|'unavailable';usedBytes:number|null;totalBytes:number|null;availableBytes:number|null;usedPercent:number|null;observedAt:string|null;source:string;reason?:string};
export const unavailableDisk=(source:string,reason='probe_unavailable'):DiskReading=>({status:'unavailable',usedBytes:null,totalBytes:null,availableBytes:null,usedPercent:null,observedAt:null,source,reason});

export function diskReading(totalBytes:unknown,availableBytes:unknown,source:string,observedAt=new Date().toISOString()):DiskReading{
 const total=Number(totalBytes),available=Number(availableBytes);
 if(!Number.isSafeInteger(total)||total<=0||!Number.isSafeInteger(available)||available<0||available>total)return unavailableDisk(source,'invalid_sample');
 const used=total-available,percent=Math.round(10000*used/total)/100;
 return {status:percent>=DISK_ALERT_THRESHOLD_PERCENT?'warning':'ok',usedBytes:used,totalBytes:total,availableBytes:available,usedPercent:percent,observedAt,source};
}
export async function readApplicationDisk(path:string,source='asset_volume'):Promise<DiskReading>{
 try{
  const fs=await statfs(path,{bigint:true});
  const total=fs.blocks*fs.bsize,available=fs.bavail*fs.bsize;
  if(total>BigInt(Number.MAX_SAFE_INTEGER)||available>BigInt(Number.MAX_SAFE_INTEGER))return unavailableDisk(source,'capacity_overflow');
  return diskReading(Number(total),Number(available),source);
 }catch{return unavailableDisk(source)}
}
export function readDatabaseDisk(row:Record<string,unknown>|null,now=Date.now()):DiskReading{
 if(!row)return unavailableDisk('postgres_volume_probe');
 const at=Date.parse(String(row.observed_at||''));
 if(!Number.isFinite(at)||at>now+60000||now-at>DB_DISK_SAMPLE_MAX_AGE_SECONDS*1000)return unavailableDisk('postgres_volume_probe','stale_sample');
 return diskReading(row.total_bytes,row.available_bytes,'postgres_volume_probe',new Date(at).toISOString());
}
/** Scratch emptyDir is pod-local even when application assets use RWX.
 * Key its email state per pod so a healthy replica cannot re-arm a full one. */
export function diskAlertStateKey(volume:DiskVolume,podName:string):string{
 if(volume!=='conversion')return volume;
 const safe=podName.replace(/[^a-zA-Z0-9._-]/g,'_').slice(0,80);
 return 'conversion:'+(safe||'unknown');
}
export type DiskAlertState='normal'|'alert';
export function nextDiskAlertAction(percentage:number,state:DiskAlertState):'send'|'rearm'|'hold'{
 if(!Number.isFinite(percentage)||percentage<0||percentage>100)return 'hold';
 if(percentage>=DISK_ALERT_THRESHOLD_PERCENT&&state==='normal')return 'send';
 if(percentage<=DISK_ALERT_RECOVERY_PERCENT&&state==='alert')return 'rearm';
 return 'hold';
}
