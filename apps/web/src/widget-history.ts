/** Bounded, page-scoped undo/redo for editable widget drafts. */
export type WidgetHistory<T> = {
  past: T[][];
  present: T[];
  future: T[][];
  gestureBase: T[] | null;
};
export const MAX_WIDGET_UNDO = 60;
export function newWidgetHistory<T>(widgets: T[] = []): WidgetHistory<T> {
  return {past: [], present: widgets, future: [], gestureBase: null};
}
const same = <T>(a: T[], b: T[]) => JSON.stringify(a) === JSON.stringify(b);
export function editWidgets<T>(state: WidgetHistory<T>, widgets: T[]): WidgetHistory<T> {
  if (same(state.present, widgets)) return state;
  if (state.gestureBase !== null) return {...state, present: widgets, future: []};
  return {past: [...state.past, state.present].slice(-MAX_WIDGET_UNDO), present: widgets, future: [], gestureBase: null};
}
export function beginWidgetGesture<T>(state: WidgetHistory<T>): WidgetHistory<T> {
  return state.gestureBase === null ? {...state, gestureBase: state.present} : state;
}
export function endWidgetGesture<T>(state: WidgetHistory<T>): WidgetHistory<T> {
  if (state.gestureBase === null) return state;
  const base = state.gestureBase;
  if (same(base, state.present)) return {...state, gestureBase: null};
  return {...state, past: [...state.past, base].slice(-MAX_WIDGET_UNDO), gestureBase: null};
}
export function undoWidgets<T>(state: WidgetHistory<T>): WidgetHistory<T> {
  if (state.gestureBase !== null || !state.past.length) return state;
  return {past: state.past.slice(0, -1), present: state.past[state.past.length-1], future: [state.present, ...state.future].slice(0, MAX_WIDGET_UNDO), gestureBase: null};
}
export function redoWidgets<T>(state: WidgetHistory<T>): WidgetHistory<T> {
  if (state.gestureBase !== null || !state.future.length) return state;
  return {past: [...state.past, state.present].slice(-MAX_WIDGET_UNDO), present: state.future[0], future: state.future.slice(1), gestureBase: null};
}
