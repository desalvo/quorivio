/** The author selects both ends of each result bar gradient.
 * The end is interpolated by that option's relative response count. */
const HEX_COLOR = /^#[0-9a-fA-F]{6}$/;
export const DEFAULT_BAR_GRADIENT_START = '#cbd5e1';
export const DEFAULT_BAR_GRADIENT_END = '#1a9e8b';
export function resultBarGradient(start: string | undefined, end: string | undefined, intensity: number): string {
 const from=HEX_COLOR.test(start||'')?start!:DEFAULT_BAR_GRADIENT_START;
 const to=HEX_COLOR.test(end||'')?end!:DEFAULT_BAR_GRADIENT_END;
 const ratio=Number.isFinite(intensity)?Math.max(0,Math.min(1,intensity)):0;
 const final='#'+[1,3,5].map(i=>{const a=parseInt(from.slice(i,i+2),16),b=parseInt(to.slice(i,i+2),16);return Math.round(a+(b-a)*ratio).toString(16).padStart(2,'0')}).join('');
 return `linear-gradient(90deg, ${from}, ${final})`;
}
