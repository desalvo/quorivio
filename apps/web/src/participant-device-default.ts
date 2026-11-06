/** Determine only the initial participant presentation mode, never override a manual selection. */
export function defaultParticipantPhoneMode(viewportWidth:number,coarsePointer:boolean):boolean {
 if(!Number.isFinite(viewportWidth)||viewportWidth<=0)return false;
 return viewportWidth<=700||(coarsePointer&&viewportWidth<=960);
}
