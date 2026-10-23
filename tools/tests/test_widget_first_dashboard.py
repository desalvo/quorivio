"""Regressions for primary widget-first authoring navigation."""
from pathlib import Path

WEB = Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx'

def test_single_primary_creation_flow():
    source = WEB.read_text()
    assert 'onClick={createCanvasPage}' in source
    assert "onClick={()=>createInteractivePage('poll')}" in source
    assert "onClick={()=>createInteractivePage('quiz')}" in source
    assert "onClick={()=>createInteractivePage('timed_quiz')}" in source
    assert 'onClick={addActivity}' not in source
    assert 'Modifica dati legacy' in source
    assert 'Apri editor widget' in source

def test_legacy_endpoint_and_editor_remain_available():
    source = WEB.read_text()
    assert 'async function addActivity()' in source
    assert 'async function saveActivityEdit()' in source
    assert 'beginPageDesign(page)' in source
