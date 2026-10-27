#!/usr/bin/env python3
"""Shared, real-pointer helpers for editor Chromium acceptance flows.

Never bypass the editor's contextual menu or use Playwright force-click:
arrangement, clipboard and layer controls are intentionally hidden until a
user opens the canvas menu, including after React rerenders or undo/reload.
"""
from playwright.async_api import expect

async def canvas_background_point(page):
    """Find a real, uncovered background hit-target inside the visible canvas.

    After scrolling, the editor's fixed header can cover the old (7, 7)
    locator-relative context-click position. Only read DOM hit-testing here;
    never mutate UI state or bypass normal browser pointer validation.
    """
    canvas = page.get_by_role('group', name='Canvas grafico widget')
    await canvas.scroll_into_view_if_needed()
    point = await canvas.evaluate("""el => {
      const rect = el.getBoundingClientRect();
      const stage = el.closest('.editor-stage');
      const clip = stage ? stage.getBoundingClientRect() : rect;
      const vv = window.visualViewport;
      const viewLeft = vv ? vv.offsetLeft : 0;
      const viewTop = vv ? vv.offsetTop : 0;
      const viewRight = viewLeft + (vv ? vv.width : window.innerWidth);
      const viewBottom = viewTop + (vv ? vv.height : window.innerHeight);
      const left = Math.max(rect.left + 3, clip.left + 3, viewLeft + 3);
      const top = Math.max(rect.top + 3, clip.top + 3, viewTop + 3);
      const right = Math.min(rect.right - 3, clip.right - 3, viewRight - 3);
      const bottom = Math.min(rect.bottom - 3, clip.bottom - 3, viewBottom - 3);
      if (right <= left || bottom <= top) return null;
      const rows = [.85, .60, .35, .12, .95, .50, .05];
      const cols = [.03, .97, .50, .20, .80, .35, .65];
      for (const row of rows) for (const col of cols) {
        const x = left + (right - left) * col;
        const y = top + (bottom - top) * row;
        const hit = document.elementFromPoint(x, y);
        if (!hit || (hit !== el && !el.contains(hit))) continue;
        if (hit.closest('.widget-canvas-item, .canvas-background-context, .canvas-context-menu, button, input, select, textarea')) continue;
        return {x, y};
      }
      return null;
    }""")
    if not point:
        raise AssertionError('No visible uncovered canvas background for contextual pointer action')
    return point


async def open_canvas_context(page):
    """Send a genuine right-mouse click to the browser-verified canvas pixel."""
    point = await canvas_background_point(page)
    await page.mouse.click(point['x'], point['y'], button='right')


async def ensure_canvas_tools_open(page):
    """Enter the actual contextual canvas UI before using arrangement actions.

    With the redesigned editor, selection/order tools are intentionally hidden
    when the canvas menu is dismissed. A browser test must reopen the real menu,
    rather than targeting an invisible button left in the document tree.
    """
    group=page.get_by_role('group',name='Allineamento widget selezionati')
    if not await group.is_visible():
        # If the background/context menu is already open, use its selection entry.
        entry=page.get_by_role('button',name='Strumenti di selezione e allineamento')
        if not await entry.is_visible():
            await open_canvas_context(page)  # Genuine pointer to visible canvas background.
        entry=page.get_by_role('button',name='Strumenti di selezione e allineamento')
        await expect(entry).to_be_visible()
        # The actual clickable point, not merely DOM visibility, must be clear.
        # Regression: Full Chromium 40589103128 timed out because the fixed
        # editor header intercepted this menu entry after scrolling.
        await entry.scroll_into_view_if_needed()
        uncovered=await entry.evaluate("""element => {
          const b=element.getBoundingClientRect();
          const x=b.left+b.width/2, y=b.top+b.height/2;
          const hit=document.elementFromPoint(x,y);
          const viewport=window.visualViewport;
          return b.width>0 && b.height>0 && y >= 64 &&
            x >= 0 && x < (viewport?.width ?? window.innerWidth) &&
            y < (viewport?.height ?? window.innerHeight) &&
            Boolean(hit && (hit===element || element.contains(hit)));
        }""")
        assert uncovered, 'Canvas selection menu is covered by the editor header or another element'
        await entry.click()
    await expect(group).to_be_visible()
    # Layer actions live in a nested .canvas-editor-tools panel. All controls
    # must be present in the accessibility tree before the test uses them.
    await expect(group.get_by_role('group',name='Ordine e spostamento widget selezionati')).to_be_visible()
    return group


async def click_canvas_tool(page, name):
    """Use an arrangement button through the same contextual menu as an editor."""
    await ensure_canvas_tools_open(page)
    # Clipboard tools live in a sibling contextual group, so scope to the page
    # after verifying the entire contextual toolbar is actually open.
    control=page.get_by_role('button',name=name,exact=True)
    await expect(control).to_be_visible()
    await expect(control).to_be_enabled()
    await control.click()


async def close_canvas_tools(page):
    """Dismiss the contextual overlay before unrelated Save/reconcile actions."""
    group=page.get_by_role('group',name='Allineamento widget selezionati')
    if await group.is_visible():
        await open_canvas_context(page)
    await expect(group).to_be_hidden()




async def wait_for_editor_sync(page,timeout=12000):
    """Wait for the *server-verified* autosave state instead of pressing a removed Save button."""
    from playwright.async_api import expect
    return await expect(page.get_by_role('region',name='Editor grafico delle pagine').get_by_role('status').filter(has_text='Salvato automaticamente')).to_be_visible(timeout=timeout)
