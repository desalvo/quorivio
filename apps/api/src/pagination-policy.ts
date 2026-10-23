/** Reject ambiguous/fractional pagination and pathological offsets. */
export function parseLeaderboardPage(raw:unknown):number|null {
 if(raw===undefined)return 1;
 if(typeof raw!=='string'||!/^\d{1,6}$/.test(raw))return null;
 const page=Number(raw);
 return Number.isSafeInteger(page)&&page>=1&&page<=100000?page:null;
}
