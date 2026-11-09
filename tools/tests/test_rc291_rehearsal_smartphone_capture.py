"""RC291: distinguish preview mode Smartphone from participant-device Smartphone.

The RC290 full CI reached fifteen real screenshots, then Playwright rejected an
ambiguous unscoped locator inside the side-by-side rehearsal dialog. The two
buttons are legitimate and must be exercised separately, preserving both
preview modes and the resulting screenshots.
"""
from __future__ import annotations
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ROOT/'tools/ci_manual_real_screenshots.py'
UI=ROOT/'apps/web/src/main.tsx'
CATALOG=ROOT/'tools/manual_screenshot_catalog.py'
CI=ROOT/'.github/workflows/ci.yml'


def assert_phone_modes_scoped(capture:str, ui:str, catalog:str)->None:
    start=capture.index("await shot('rehearsal-side-by-side',editor)")
    end=capture.index("await dialog.get_by_role('button',name='Chiudi anteprima')",start)
    body=capture[start:end]
    stages=(
        "devices=dialog.get_by_role('group',name='Dispositivo partecipante')",
        "device_phone=devices.get_by_role('button',name='Smartphone',exact=True)",
        "await expect(device_phone).to_have_count(1,timeout=12000)",
        "await expect(device_phone).to_be_enabled(timeout=12000)",
        "await device_phone.click(timeout=12000)",
        "await expect(device_phone).to_have_attribute('aria-pressed','true',timeout=12000)",
        "await expect(dialog.locator('.rehearsal-mode-both .rehearsal-pane-phone')).to_be_visible(timeout=12000)",
        "await shot('rehearsal-side-by-side-smartphone',editor)",
        "modes=dialog.get_by_role('group',name='Modalità anteprima')",
        "phone_mode=modes.get_by_role('button',name='Smartphone',exact=True)",
        "await expect(phone_mode).to_have_count(1,timeout=12000)",
        "await expect(phone_mode).to_be_enabled(timeout=12000)",
        "await phone_mode.click(timeout=12000)",
        "await expect(phone_mode).to_have_attribute('aria-pressed','true',timeout=12000)",
        "await expect(dialog.locator('.rehearsal-mode-mobile')).to_be_visible(timeout=12000)",
        "await shot('rehearsal-smartphone',editor)",
    )
    last=-1
    for stage in stages:
        i=body.find(stage,last+1)
        if i<0:raise AssertionError('missing/out-of-order preview capture verification: '+stage)
        last=i
    # A broad dialog query is invalid: both buttons are real and accessible.
    if "dialog.get_by_role('button',name='Smartphone')" in body or ".get_by_role('button',name='Smartphone').first" in body:
        raise AssertionError('Unscoped Smartphone locator would be ambiguous')
    # Confirm the actual app exposes two different groups, not just fake selectors.
    if 'aria-label="Modalità anteprima"' not in ui or 'aria-label="Dispositivo partecipante"' not in ui:
        raise AssertionError('Preview device and mode controls missing from real editor')
    if "setMode('mobile')" not in ui or "setParticipantDevice('phone')" not in ui:
        raise AssertionError('Preview mode and participant device actions have been removed')
    if "mode==='both'&&participantDevice==='phone'" not in ui or "' rehearsal-pane-phone'" not in ui:
        raise AssertionError('Side-by-side phone rendering missing')
    if "'rehearsal-side-by-side-smartphone': ('presenter','user')" not in catalog:
        raise AssertionError('Side-by-side phone screenshot not listed for presenter and participant manuals')
    if "'rehearsal-side-by-side-smartphone': ('Anteprima affiancata" not in catalog:
        raise AssertionError('Screenshot is missing bilingual caption')


class RC291RehearsalSmartphoneCapture(unittest.TestCase):
    def test_both_real_smartphone_controls_are_scoped_and_captured(self):
        assert_phone_modes_scoped(CAPTURE.read_text(),UI.read_text(),CATALOG.read_text())

    def test_unscoped_selector_would_fail(self):
        source=CAPTURE.read_text();ui=UI.read_text();cat=CATALOG.read_text()
        modifications=(
            ("devices.get_by_role('button',name='Smartphone',exact=True)", "dialog.get_by_role('button',name='Smartphone')"),
            ("modes.get_by_role('button',name='Smartphone',exact=True)", "dialog.get_by_role('button',name='Smartphone')"),
            ("await expect(device_phone).to_have_count(1,timeout=12000)", "await device_phone.click(force=True)"),
            ("await expect(phone_mode).to_have_attribute('aria-pressed','true',timeout=12000)", "await expect(phone_mode).to_be_visible(timeout=12000)"),
            ("await shot('rehearsal-side-by-side-smartphone',editor)", "# no side-by-side device screenshot"),
        )
        for before,after in modifications:
            self.assertIn(before,source)
            with self.subTest(change=before),self.assertRaises(AssertionError):
                assert_phone_modes_scoped(source.replace(before,after),ui,cat)

    def test_mode_device_ui_changes_are_rejected(self):
        src=CAPTURE.read_text();ui=UI.read_text();cat=CATALOG.read_text()
        for before,after in (("setMode('mobile')", "setMode('both')"),("setParticipantDevice('phone')", "setParticipantDevice('desktop')"),('aria-label="Dispositivo partecipante"','aria-label="Dispositivo"')):
            self.assertIn(before,ui)
            with self.subTest(change=before),self.assertRaises(AssertionError):
                assert_phone_modes_scoped(src,ui.replace(before,after),cat)

    def test_ci_runs_preflight_before_costly_browser_capture(self):
        workflow=CI.read_text()
        assert 'python3 -m unittest tools.tests.test_rc291_rehearsal_smartphone_capture -q' in workflow
        assert workflow.index('tools.tests.test_rc291_rehearsal_smartphone_capture') < workflow.index('python3 tools/ci_manual_real_screenshots.py')


if __name__=='__main__':unittest.main()
