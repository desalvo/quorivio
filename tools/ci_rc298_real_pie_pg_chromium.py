#!/usr/bin/env python3
"""RC298: real compiled React + PostgreSQL percentage/accessibility acceptance.

Two independent disposable sessions are persisted by the actual API. The real
editor, its phone layout and its presenter/participant rehearsal are exercised
in Chromium. No route interception, mocked React tree or synthetic DOM. Counts
in *rehearsal* remain intentionally simulated; physical screen readers and
provider/production acceptance remain separately required.
"""
from __future__ import annotations

import asyncio
import os
import re
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import BASE, call, open_editor
from ci_browser_participant import validate_disposable_origin

TITLE_ON = 'RC298 PostgreSQL accessibilita pie con percentuali'
TITLE_OFF = 'RC298 PostgreSQL accessibilita pie senza percentuali'
QUESTION = 'rc298-accessible-question'
CHART = 'rc298-accessible-chart'
OPTIONS = [
    {'id': 'alpha', 'label': 'Una risposta molto lunga con spazi, accenti e punteggiatura'},
    {'id': 'beta', 'label': 'Seconda possibilità'},
    {'id': 'gamma', 'label': 'Terza alternativa'},
]


async def persisted_case(context, title: str, percentages: bool) -> tuple[str, str]:
    session = await call(context, 'POST', '/api/sessions', {'title': title}, 201)
    sid = session['id']
    activity = await call(context, 'POST', f'/api/sessions/{sid}/activities', {
        'title': 'Grafico accessibile RC298', 'type': 'poll',
        'options': [{'id': 'alpha', 'label': 'Alpha'}, {'id': 'beta', 'label': 'Beta'}],
    }, 201)
    aid = activity['id']
    snapshot = await call(context, 'GET', f'/api/sessions/{sid}')
    page = next(item for item in snapshot['activities'] if item['id'] == aid)
    question = {
        'id': QUESTION, 'kind': 'question', 'label': 'Quale risposta preferisci?',
        'answerMode': 'single', 'required': True, 'resultsView': 'pie',
        'options': OPTIONS, 'style': {'fontFamily': 'Arial', 'fontSize': 18},
        'position': {'x': 3, 'y': 18, 'width': 43, 'height': 60, 'rotation': 0},
    }
    chart = {
        'id': CHART, 'kind': 'results-button', 'label': 'Risultati accessibili RC298',
        'targetWidgetId': QUESTION, 'resultsOnly': True,
        'pieShowPercentages': percentages, 'pieShowOptionNumbers': True,
        'pieSize': 85, 'autoFit': False,
        'position': {'x': 51, 'y': 12, 'width': 45, 'height': 77, 'rotation': 0},
    }
    await call(context, 'PATCH', f'/api/sessions/{sid}/activities/{aid}/design', {
        'page_design': {**page['page_design'], 'widgets': [*page['page_design'].get('widgets', []), question, chart]},
        'result_design': page.get('result_design') or {},
        'expected_design_revision': page['design_revision'],
    })
    persisted = await call(context, 'GET', f'/api/sessions/{sid}')
    saved = next(item for item in persisted['activities'] if item['id'] == aid)
    original = next(item for item in saved['page_design']['widgets'] if item['id'] == QUESTION)
    result = next(item for item in saved['page_design']['widgets'] if item['id'] == CHART)
    assert original['resultsView'] == 'pie' and original['options'] == OPTIONS
    assert result['pieShowPercentages'] is percentages and result['pieSize'] == 85
    assert result['targetWidgetId'] == QUESTION and result['pieShowOptionNumbers'] is True
    return sid, aid


def pie_widget(page):
    return page.locator('.widget-canvas-item[data-widget-kind="results-button"]').filter(
        has=page.locator('.linked-results-pie-chart'))


async def verify_enabled(widget, *, expected_phone: bool) -> None:
    await expect(widget).to_have_count(1, timeout=12000)
    chart = widget.locator('.linked-results-pie-chart')
    await expect(chart).to_have_count(1)
    await expect(chart).to_have_attribute('data-pie-size', '85')
    legend = widget.get_by_role('list', name='Percentuali delle risposte')
    await expect(legend).to_have_count(1)
    items = legend.get_by_role('listitem')
    await expect(items).to_have_count(3)
    # A configured sort changes slice order but never option identity.
    labels = [await item.get_attribute('aria-label') for item in await items.all()]
    for option in OPTIONS:
        assert any(label and label.startswith(option['label'] + ': ') for label in labels), (option, labels)
    for index, label in enumerate(labels):
        assert label and re.fullmatch(r'.+: [1-9][0-9]* rispost[ae], (?:[0-9]+(?:\.[0-9]+)?%|<0\.0001%)', label), (index, label)
        visible_percent = (await items.nth(index).locator('.linked-results-pie-mobile-percent').inner_text()).strip()
        assert label.endswith(', ' + visible_percent), label
    state = await legend.evaluate('''node=>{
        const css=getComputedStyle(node),bounds=node.getBoundingClientRect();
        return {clip:css.clipPath,position:css.position,width:bounds.width,
                overflow:node.scrollWidth>node.clientWidth+1};
    }''')
    if expected_phone:
        assert state['clip'] == 'none' and state['width'] > 20, state
        assert not state['overflow'], state
    else:
        assert state['clip'] != 'none' and state['position'] == 'absolute' and state['width'] <= 2, state
    await expect(chart).to_have_attribute('aria-label', re.compile('Distribuzione percentuale'))


async def run() -> None:
    validate_disposable_origin(BASE)
    if not all(os.environ.get(key) for key in (
        'QUORIVIO_CI_ADMIN_EMAIL', 'QUORIVIO_CI_NEW_PASSWORD', 'QUORIVIO_CI_LOAD_TOKEN'
    )):
        raise RuntimeError('RC298 requires disposable CI administrator and load token')
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'),
            headless=True, args=['--no-sandbox'],
        )
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 940}, locale='it-IT',
            extra_http_headers={'X-Quorivio-Load-Token': os.environ['QUORIVIO_CI_LOAD_TOKEN']},
        )
        try:
            await call(context, 'POST', '/api/auth/login', {
                'email': os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                'password': os.environ['QUORIVIO_CI_NEW_PASSWORD'],
            })
            sid, aid = await persisted_case(context, TITLE_ON, True)
            await persisted_case(context, TITLE_OFF, False)
            page = await context.new_page()
            errors: list[str] = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            await open_editor(page, TITLE_ON)
            await verify_enabled(pie_widget(page), expected_phone=False)
            print('RC298 PASS: persisted live React editor and desktop accessibility')

            await page.get_by_role('switch', name='Modifica layout Smartphone').check()
            await expect(page.locator('.canvas-editor-group[data-canvas-device="phone"]')).to_have_count(1)
            await verify_enabled(pie_widget(page), expected_phone=True)
            print('RC298 PASS: real editor smartphone layout and source-labelled percentages')

            await page.get_by_role('switch', name='Modifica layout Smartphone').uncheck()
            await expect(page.locator('.canvas-editor-group[data-canvas-device="desktop"]')).to_have_count(1)
            await verify_enabled(pie_widget(page), expected_phone=False)
            await page.locator('button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]').click()
            dialog = page.get_by_role('dialog', name='Anteprima interattiva della sessione')
            await expect(dialog).to_be_visible()
            presenter_chart = dialog.locator('.rehearsal-pane .rehearsal-widget[data-widget-kind="results-button"]')
            await expect(presenter_chart).to_have_count(1)
            await expect(presenter_chart.get_by_role('list', name='Percentuali delle risposte')).to_have_count(1)
            await dialog.get_by_role('button', name='Partecipante', exact=True).click()
            await expect(dialog.locator('.rehearsal-widget[data-widget-kind="results-button"]')).to_have_count(0)
            await dialog.get_by_role('button', name='Chiudi anteprima').click()
            print('RC298 PASS: real presenter rehearsal results and participant privacy')

            actual = await call(context, 'GET', f'/api/sessions/{sid}')
            activity = next(x for x in actual['activities'] if x['id'] == aid)
            assert any(x['id'] == CHART and x.get('pieShowPercentages') is True
                       for x in activity['page_design']['widgets'])

            hidden = await context.new_page()
            hidden.on('pageerror', lambda error: errors.append(str(error)))
            await open_editor(hidden, TITLE_OFF)
            missing = pie_widget(hidden)
            await expect(missing).to_have_count(1)
            await expect(missing.get_by_role('list', name='Percentuali delle risposte')).to_have_count(0)
            await expect(missing.locator('.linked-results-pie-chart')).to_have_attribute(
                'aria-label', 'Distribuzione delle risposte.')
            tooltip = await missing.locator('.linked-results-pie-chart path title').all_text_contents()
            assert len(tooltip) == 3 and all('%' not in label for label in tooltip), tooltip
            assert not errors, 'Runtime React page errors: ' + '; '.join(errors[:3])
            print('RC298 PASS: hidden percentages persist and never leak via SVG; no JS errors')
        finally:
            await context.close()
            await browser.close()


if __name__ == '__main__':
    asyncio.run(run())
