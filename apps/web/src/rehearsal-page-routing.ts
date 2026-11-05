/** One presenter slide can route the audience to a distinct page. The same
 * presenter-hidden policy is applied to live and to both rehearsal panes. */
import {presenterVisiblePages} from './presenter-navigation.ts';

export type RehearsalPage={id:string;page_design?:{presenterHidden?:boolean;audiencePageId?:string}|null};

export function rehearsalPresenterPages<T extends RehearsalPage>(pages:readonly T[]):T[]{
 return presenterVisiblePages(pages);
}

/** Never follow a cross-session or missing audience page. The server already
 * rejects invalid saved IDs; a stale local draft must also fail closed. */
export function rehearsalAudiencePage<T extends RehearsalPage>(presenter:T|undefined,pages:readonly T[]):T|undefined{
 if(!presenter)return undefined;
 const target=presenter.page_design?.audiencePageId;
 return (target&&pages.find(page=>page.id===target))||presenter;
}

/** If the editor opens the rehearsal on a page hidden from the presenter,
 * show its owner-facing partner instead of an invisible presenter slide. */
export function rehearsalStartIndex<T extends RehearsalPage>(pages:readonly T[],selectedId?:string):number{
 const visible=rehearsalPresenterPages(pages);
 const selected=visible.findIndex(page=>page.id===selectedId);
 if(selected>=0)return selected;
 const linked=visible.findIndex(page=>page.page_design?.audiencePageId===selectedId);
 return linked>=0?linked:0;
}
