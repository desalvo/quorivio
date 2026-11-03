/** Shared ten-value rating scale on all Quorivio surfaces. */
export const RATING_MIN=0;
export const RATING_MAX=9;
export const RATING_VALUES=Array.from({length:RATING_MAX-RATING_MIN+1},(_,i)=>i+RATING_MIN);
