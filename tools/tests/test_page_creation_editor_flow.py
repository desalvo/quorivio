"""Prevent regressions in the create-page -> widget editor handoff."""
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx'


def test_created_activity_is_selected_from_refreshed_snapshot():
    source = SOURCE.read_text()
    assert 'const created=await request<Activity>(`/sessions/${selected}/activities`' in source
    assert 'const updated=await request<Snapshot>(`/sessions/${selected}`)' in source
    assert 'updated.activities.find(a=>a.id===created.id)' in source
    assert 'if(newPage){beginPageDesign(newPage)' in source


def test_page_creator_explains_widget_editor_handoff():
    source = SOURCE.read_text()
    assert 'Crea contenuti con i widget' in source
    assert 'La pagina si apre direttamente nell’editor' in source
    assert "setSessionTab('pages')" in source
