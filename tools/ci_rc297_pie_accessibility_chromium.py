#!/usr/bin/env python3
"""RC297: real Chromium accessibility-tree checks with the shipped CSS.

Uses a representative DOM fixture, not the full React/PostgreSQL app; physical
NVDA/VoiceOver/TalkBack acceptance remains an external gate.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "apps/web/src/style.css").read_text(encoding="utf8")


def page_html(wrapper: str = "", with_percentages: bool = True) -> str:
    closing = "</div>" * wrapper.count("<div")
    items = "".join(
        '<div class="linked-results-pie-mobile-item" role="listitem" '
        f'aria-label="Risposta {i}: {i} {("risposta" if i==1 else "risposte")}, {i}.5%">'
        '<span class="linked-results-pie-mobile-swatch" aria-hidden="true"></span>'
        f'<span class="linked-results-pie-mobile-name">Risposta {i}</span>'
        f'<strong class="linked-results-pie-mobile-percent">{i}.5%</strong>'
        "</div>"
        for i in range(1, 4)
    )
    legend = (
        '<div class="linked-results-pie-mobile-legend" role="list" '
        'aria-label="Percentuali delle risposte">' + items + "</div>"
        if with_percentages else ""
    )
    return "".join((
        "<style>", CSS, "</style>",
        '<main style="width:min(100%,400px)">', wrapper,
        '<div class="widget-canvas-item page-widget rehearsal-widget" data-widget-kind="results-button">',
        '<section class="linked-results result-view-pie" style="width:100%;height:560px;font:18px Arial">',
        '<svg class="linked-results-pie linked-results-pie-chart" viewBox="0 0 500 320" data-mobile-percent-labels="',
        "true" if with_percentages else "false",
        '" role="img" aria-label="',
        ("Distribuzione percentuale delle risposte. Legenda accessibile con conteggi e percentuali."
         if with_percentages else "Distribuzione delle risposte."),
        '"><g class="linked-results-pie-callout"><text x="380" y="100">25%</text></g></svg>',
        legend,
        '<div class="linked-results-items"><div class="linked-results-row" id="row-marker">',
        '<span class="linked-result-pair">Risultato <output>10</output></span></div></div>',
        "</section></div>", closing, "</main>",
    ))


async def run() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=os.getenv("QUORIVIO_CHROMIUM_PATH", "/usr/bin/chromium"),
            headless=True,
            args=["--no-sandbox"],
        )
        scenarios = [
            ("desktop", 1100, "", False),
            ("phone-390", 390, "", True),
            ("phone-360", 360, "", True),
            ("editor-phone", 1100, '<div class="editor-ux-v2"><div class="canvas-editor-group" data-canvas-device="phone">', True),
            ("audience-phone", 1100, '<div class="audience-widget-layout stage-phone">', True),
        ]
        for name, width, wrapper, expected_visible in scenarios:
            page = await browser.new_page(viewport={"width": width, "height": 850})
            await page.set_content(page_html(wrapper))
            legend = page.get_by_role("list", name="Percentuali delle risposte")
            assert await legend.count() == 1, name
            entries = legend.get_by_role("listitem")
            assert await entries.count() == 3, name
            names = [await entries.nth(i).get_attribute("aria-label") for i in range(3)]
            assert names == [
                "Risposta 1: 1 risposta, 1.5%",
                "Risposta 2: 2 risposte, 2.5%",
                "Risposta 3: 3 risposte, 3.5%",
            ], (name, names)
            state = await page.evaluate("""() => {
              const el=document.querySelector('.linked-results-pie-mobile-legend');
              const css=getComputedStyle(el);
              const rect=el.getBoundingClientRect();
              return {display:css.display,clip:css.clipPath,width:rect.width,
                overflow:el.scrollWidth>el.clientWidth+1};
            }""")
            assert state["display"] == "grid", (name, state)
            if expected_visible:
                assert state["clip"] == "none" and state["width"] > 30, (name, state)
                assert not state["overflow"], (name, state)
            else:
                assert state["clip"] != "none" and state["width"] <= 2, (name, state)
                before = await page.locator("#row-marker").bounding_box()
                await legend.evaluate("(el) => el.remove()")
                after = await page.locator("#row-marker").bounding_box()
                assert before is not None and after is not None
                for key in ("x", "y", "width", "height"):
                    assert abs(before[key] - after[key]) < 0.5, (name, key, before, after)
            print("RC297 accessibility PASS", name, state)
            await page.close()

        # The "show percentages" switch must not leave an empty or misleading
        # accessible percentage list when it is disabled.
        page = await browser.new_page(viewport={"width": 1100, "height": 800})
        await page.set_content(page_html(with_percentages=False))
        assert await page.get_by_role("list", name="Percentuali delle risposte").count() == 0
        assert await page.get_by_role("img", name="Distribuzione delle risposte.").count() == 1
        print("RC297 accessibility PASS: percentages disabled")
        await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
