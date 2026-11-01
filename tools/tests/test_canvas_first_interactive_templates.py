from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()

def test_page_templates_create_backed_activities():
    assert "async function createInteractivePage(template:'poll'|'quiz'|'timed_quiz')" in SOURCE
    assert "`/sessions/${selected}/activities`,'POST'" in SOURCE
    assert "duration_seconds:template==='timed_quiz'?30:null" in SOURCE

def test_templates_open_editor_and_keep_existing_form():
    assert 'if(page){beginPageDesign(page);setNotice(' in SOURCE
    assert "createInteractivePage('poll')" in SOURCE
    assert "createInteractivePage('quiz')" in SOURCE
    assert "createInteractivePage('timed_quiz')" in SOURCE
    assert 'async function addActivity()' in SOURCE
