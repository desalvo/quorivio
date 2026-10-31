"""Regressions for primary widget-first authoring navigation."""
from pathlib import Path

WEB = Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx'

def test_single_primary_creation_flow():
    source = WEB.read_text()
    assert '✎ Modifica le pagine' in source
    assert 'live-stats-tools' in source
    for legacy in ("onClick={()=>createInteractivePage('poll')}",
                   "onClick={()=>createInteractivePage('quiz')}",
                   "onClick={()=>createInteractivePage('timed_quiz')}",
                   'legacy-page-admin', 'Modifica dati legacy'):
        assert legacy not in source
    assert 'onClick={addActivity}' not in source
    assert 'Modifica dati legacy' not in source
    assert 'editor-widget-rail' in source

def test_legacy_endpoint_and_editor_remain_available():
    source = WEB.read_text()
    assert 'async function addActivity()' in source
    assert 'async function saveActivityEdit()' in source
    assert 'beginPageDesign(page)' in source
