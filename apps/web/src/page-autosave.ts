/** Recovery decisions for an autosave whose HTTP response was lost.
 * A failed PATCH is NOT proof that PostgreSQL rejected the write. Always read
 * the authoritative revision before considering a retry. */
import {pageDraftFromActivity, type EditablePageDraft, validDesignRevision} from './page-draft.ts';

export type AutosaveRecovery = 'persisted'|'unchanged'|'conflict'|'unverifiable';

function canonical(value:unknown):string {
 return JSON.stringify(value, (_,v)=>v && typeof v==='object' && !Array.isArray(v)
  ? Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))) : v);
}

export function autosaveRecoveryDecision(
 remote:{design_revision?:unknown;page_design?:unknown;result_design?:unknown}|undefined,
 requested:EditablePageDraft,
 expectedRevision:number,
 confirmedRevision?:number
):AutosaveRecovery {
 if(!remote || !validDesignRevision(remote.design_revision) || !validDesignRevision(expectedRevision))return 'unverifiable';
 const revision=remote.design_revision;
 if(revision===expectedRevision && confirmedRevision===undefined)return 'unchanged';
 // PostgreSQL has committed exactly this write. Do not resend the PATCH.
 if(revision===confirmedRevision || (confirmedRevision===undefined && revision===expectedRevision+1)) {
  const actual=pageDraftFromActivity(remote);
  return canonical(actual)===canonical(requested)?'persisted':'conflict';
 }
 return 'conflict';
}

export function recoverableAutosaveTransportError(error:unknown):boolean {
 const text=error instanceof Error?error.message:String(error);
 return /Failed to fetch|NetworkError|Load failed|AbortError|Timeout|HTTP (502|503|504)\b/i.test(text);
}

export function retryAutosaveDelay(attempts:number):number {
 return Math.min(850 * Math.pow(2,Math.max(0,Math.min(6,attempts))),6500);
}
