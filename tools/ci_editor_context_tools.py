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
        trigger=page.get_by_role('button',name='Apri menu contestuale canvas, sfondi e proprietà pagina')
        await trigger.click()  # Real pointer path; never force clicks or mutate DOM state.
    await expect(group).to_be_visible()
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
        trigger=page.get_by_role('button',name='Apri menu contestuale canvas, sfondi e proprietà pagina')
        await trigger.click()
    await expect(group).to_be_hidden()

