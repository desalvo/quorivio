/** Keyboard geometry for an editable free-text response box.
 * Height is stored as whole logical pixels on the 1280px-wide slide.
 * Pointer and keyboard editing both use the same bounds, and changes flow
 * through the normal page design state/undo/autosave pipeline. */
export const MIN_ANSWER_FIELD_HEIGHT = 48;
export const MAX_ANSWER_FIELD_HEIGHT = 400;
export const DEFAULT_ANSWER_FIELD_HEIGHT = 96;
export const ANSWER_FIELD_HEIGHT_STEP = 8;
export function answerFieldHeight(value:unknown):number{
 return typeof value === 'number' && Number.isInteger(value) && value>=MIN_ANSWER_FIELD_HEIGHT && value<=MAX_ANSWER_FIELD_HEIGHT ? value : DEFAULT_ANSWER_FIELD_HEIGHT;
}
/** Return null for keys that belong to the editor/OS instead of the handle. */
export function answerFieldHeightForKey(current:number,key:string,shift=false):number|null{
 const height=answerFieldHeight(current);
 const clamp=(n:number)=>Math.max(MIN_ANSWER_FIELD_HEIGHT,Math.min(MAX_ANSWER_FIELD_HEIGHT,n));
 switch(key){
  case 'ArrowDown': return clamp(height+(shift?32:ANSWER_FIELD_HEIGHT_STEP));
  case 'ArrowUp': return clamp(height-(shift?32:ANSWER_FIELD_HEIGHT_STEP));
  case 'PageDown': return clamp(height+32);
  case 'PageUp': return clamp(height-32);
  case 'Home': return MIN_ANSWER_FIELD_HEIGHT;
  case 'End': return MAX_ANSWER_FIELD_HEIGHT;
  default: return null;
 }
}
