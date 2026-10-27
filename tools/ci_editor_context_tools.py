#!/usr/bin/env python3
"""Shared, real-pointer helpers for editor Chromium acceptance flows.

Never bypass the editor's contextual menu or use Playwright force-click:
arrangement, clipboard and layer controls are intentionally hidden until a
user opens the canvas menu, including after React rerenders or undo/reload.
"""
from playwright.async_api import expect

async def ensure_canvas_tools_open(page):
    """Enter the actual contextual canvas UI before using arrangement actions.

    With the redesigned editor, selection/order tools are intentionally hidden
    when the canvas menu is dismissed. A browser test must reopen the real menu,
    rather than targeting an invisible button left in the document tree.
    """
    group=page.get_by_role('group',name='Allineamento widget selezionati')
    if not await group.is_visible():
        canvas=page.get_by_role('group',name='Canvas grafico widget')
        # If the background/context menu is already open, use its selection entry.
        entry=page.get_by_role('button',name='Strumenti di selezione e allineamento')
        if not await entry.is_visible():
            await canvas.click(button='right',position={'x':7,'y':7})  # Native context menu; no synthetic DOM mutation.
        await page.get_by_role('button',name='Strumenti di selezione e allineamento').click()
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
        canvas=page.get_by_role('group',name='Canvas grafico widget')
        await canvas.click(button='right',position={'x':7,'y':7})
    await expect(group).to_be_hidden()




async def wait_for_editor_sync(page,timeout=12000):
    """Wait for the *server-verified* autosave state instead of pressing a removed Save button."""
    from playwright.async_api import expect
    return await expect(page.get_by_role('region',name='Editor grafico delle pagine').get_by_role('status').filter(has_text='Salvato automaticamente')).to_be_visible(timeout=timeout)
