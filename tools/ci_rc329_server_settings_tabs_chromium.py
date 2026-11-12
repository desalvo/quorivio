#!/usr/bin/env python3
"""RC329: actual Chromium CSS visibility/contrast for seven server-setting tabs.

Uses shipped Quorivio CSS and an HTML fixture matching the authenticated
administrator's tablist. No session, credentials, or network requests involved.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "apps/web/src/style.css"
LABELS = ("Generale", "Autenticazione", "Posta elettronica", "Spazio disco",
          "Convertitore", "Backup", "Audit")
HTML = """<!doctype html><html lang="it"><head><meta charset="UTF-8"></head>
<body><div class="app"><main class="dashboard"><aside class="aside"></aside>
<section class="workspace"><div class="server-settings-tabs" role="tablist"
aria-label="Schede delle impostazioni del server">BUTTONS</div></section>
</main></div></body></html>"""


def brightness(rgb_css: str) -> float:
    numbers = [int(n) for n in re.findall(r"\d+", rgb_css)[:3]]
    assert len(numbers) == 3, f"Expected RGB CSS color, got {rgb_css!r}"
    values = [x / 255 for x in numbers]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
              for x in values]
    return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    a, b = brightness(foreground), brightness(background)
    return (max(a, b) + .05) / (min(a, b) + .05)


def main() -> None:
    buttons = "".join(
        '<button type="button" class="server-settings-tab%s" role="tab" '
        'aria-selected="%s" tabindex="%s">%s</button>'
        % (" active" if i == 0 else "", "true" if i == 0 else "false",
           "0" if i == 0 else "-1", label)
        for i, label in enumerate(LABELS)
    )
    with sync_playwright() as pw:
        launch = {"headless": True}
        if os.getenv("QUORIVIO_CHROMIUM_PATH"):
            launch["executable_path"] = os.environ["QUORIVIO_CHROMIUM_PATH"]
        browser = pw.chromium.launch(**launch)
        try:
            for width in (390, 1280):
                page = browser.new_page(viewport={"width": width, "height": 800})
                page.set_content(HTML.replace("BUTTONS", buttons))
                page.add_style_tag(content=CSS.read_text(encoding="utf-8"))
                tabs = page.locator(".server-settings-tabs > button.server-settings-tab")
                assert tabs.count() == 7
                metrics = tabs.evaluate_all("""elements => elements.map(el => {
                    const style = getComputedStyle(el), box = el.getBoundingClientRect();
                    return {text:el.textContent, fg:style.color, bg:style.backgroundColor,
                      visibility:style.visibility, opacity:Number(style.opacity),
                      display:style.display, width:box.width, height:box.height,
                      selected:el.getAttribute('aria-selected')};
                })""")
                for i, metric in enumerate(metrics):
                    assert metric["text"] == LABELS[i], metric
                    assert metric["visibility"] == "visible", metric
                    assert metric["opacity"] >= .99, metric
                    assert metric["display"] != "none", metric
                    assert metric["width"] >= 58 and metric["height"] >= 40, metric
                    assert metric["selected"] == ("true" if i == 0 else "false"), metric
                    assert contrast(metric["fg"], metric["bg"]) >= 4.5, metric
                # A hover must remain legible, and mobile must scroll to Audit.
                tabs.nth(1).hover()
                hovered = tabs.nth(1).evaluate("""el => {
                    const s=getComputedStyle(el);return [s.color,s.backgroundColor] }""")
                assert contrast(*hovered) >= 4.5, hovered
                if width == 390:
                    rail = page.locator(".server-settings-tabs")
                    sizes = rail.evaluate("""el=>[el.clientWidth,el.scrollWidth,
                        getComputedStyle(el).overflowX]""")
                    assert sizes[1] > sizes[0] and sizes[2] == "auto", sizes
                    tabs.last.scroll_into_view_if_needed()
                    visible = tabs.last.evaluate("""el=>{
                       const t=el.getBoundingClientRect();
                       const p=el.parentElement.getBoundingClientRect();
                       return t.left>=p.left-2 && t.right<=p.right+2
                    }""")
                    assert visible, "Audit tab cannot be reached on mobile"
                print(f"RC329 tabs: {width}px, all 7 visible, WCAG-AA contrast PASS", flush=True)
                page.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
