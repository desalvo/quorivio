/** Shared public projection contract.  A real participant must see exactly the
 * same authored widgets as the participant rehearsal, never presenter tools.
 * Geometry is left untouched so master inheritance and mobile overrides remain
 * owned by the common page-layout pipeline.
 */
import {mobilePageWidgets,mobileStageHeight,type MobileWidget} from './mobile-page-layout.ts';
import type {MobilePageLayout} from '../../api/src/domain';

export type LiveSlideWidget = {
  kind: string; showTitle?: boolean; label?: string;
  position?: {x: number; y: number; width: number; height?: number};
};

const PRESENTER_ONLY_WIDGETS = new Set(['results-button', 'participant-count']);
const LABELLESS_GRAPHICS = new Set(['line', 'shape']);

/** Some older slides have an independent, unlabelled shape painted exactly
 * behind a result widget. The result itself is private, and the painted backing
 * must not remain as an orphaned fill on the audience slide. Do not hide large
 * slide decorations or named shapes: only a matched, unlabelled result backing. */
function isOrphanResultFill(widget: LiveSlideWidget, results: readonly LiveSlideWidget[]): boolean {
  if(widget.kind !== 'shape' || (widget.label||'').trim() && !['Forma','shape'].includes(widget.label||'')) return false;
  const p=widget.position;
  if(!p) return false;
  return results.some(result=>{
    const r=result.position;
    if(!r || r.width<=0 || p.width<=0) return false;
    const rh=r.height??24, ph=p.height??24;
    return Math.abs(p.x-r.x)<=3 && Math.abs(p.y-r.y)<=3
      && Math.abs(p.width-r.width)<=6 && Math.abs(ph-rh)<=6;
  });
}

export function participantVisibleWidgets<W extends LiveSlideWidget>(widgets: readonly W[]): W[] {
  const results=widgets.filter(widget=>widget.kind==='results-button');
  return widgets.filter(widget => !PRESENTER_ONLY_WIDGETS.has(widget.kind)
    && !isOrphanResultFill(widget,results));
}

/** Accessible reading is a document, not a visually repositioned slide.
 * The DOM/tab order must match the reading order: visual top-to-bottom,
 * left-to-right for equal rows, with the footer last. CSS `order` alone does
 * not change the order reported to a screen reader or keyboard users.
 * Exclude decoration and private result shells before ordering. The 16:9 and
 * independent phone canvases retain their own original stacking/layout.
 */
export function participantReadingWidgets<W extends LiveSlideWidget>(widgets: readonly W[]): W[] {
  return participantVisibleWidgets(widgets)
    .map((widget, index) => ({widget, index}))
    .filter(({widget}) => !LABELLESS_GRAPHICS.has(widget.kind))
    .sort((a, b) => {
      if (a.widget.kind === 'footer' || b.widget.kind === 'footer')
        return a.widget.kind === b.widget.kind ? a.index - b.index : a.widget.kind === 'footer' ? 1 : -1;
      const aY = a.widget.position?.y ?? Number.POSITIVE_INFINITY;
      const bY = b.widget.position?.y ?? Number.POSITIVE_INFINITY;
      const aX = a.widget.position?.x ?? Number.POSITIVE_INFINITY;
      const bX = b.widget.position?.x ?? Number.POSITIVE_INFINITY;
      return aY - bY || aX - bX || a.index - b.index;
    })
    .map(({widget}) => widget);
}

/** Graphic widgets are graphical ONLY.  Legacy projects may have showTitle=true
 * or a label, but neither is allowed to create live/preview text for them.
 * QR captions are opt-in even for old saved project documents.
 */
export function widgetTitleVisible(widget: LiveSlideWidget): boolean {
  if (LABELLESS_GRAPHICS.has(widget.kind)) return false;
  if (widget.kind === 'qr') return widget.showTitle === true;
  return widget.showTitle !== false;
}

/** One participant-only phone geometry plan shared by rehearsal and live view.
 * Excluding presenter controls AFTER stacking creates phantom vertical gaps and
 * an oversized stage even though those controls are invisible. Filter FIRST,
 * then compute both stage height and auto-positions from identical widgets.
 * Explicit mobile overrides for visible widgets remain unchanged.
 */
export function participantPhoneLayout<W extends MobileWidget & LiveSlideWidget>(
  widgets: readonly W[], mobile?: MobilePageLayout
): {widgets: W[]; height: number} {
  const visible = participantVisibleWidgets(widgets);
  return {widgets: mobilePageWidgets(visible, mobile), height: mobileStageHeight(visible, mobile)};
}
