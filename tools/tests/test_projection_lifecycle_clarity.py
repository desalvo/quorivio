"""Guard explicit projection lifecycle states from regressing to a blank display."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx').read_text()


def test_public_projection_distinguishes_pause_from_active_page():
    assert "publicSnap?.session?.status==='paused'" in SOURCE
    assert 'Presentazione in pausa' in SOURCE
    assert "publicSnap?.session?.status!=='active'" in SOURCE


def test_projection_handles_active_without_selected_page():
    assert "publicSnap?.activities?.some(a=>a.id===publicSnap.session.current_activity_id)" in SOURCE
    assert 'In attesa di una pagina' in SOURCE
    assert 'Pagine e contenuti' in SOURCE


def test_dashboard_explains_start_and_pause_semantics():
    assert "snap.session.status==='active'&&!snap.session.current_activity_id" in SOURCE
    assert 'Sessione avviata: pubblica una pagina' in SOURCE
    assert 'Sessione in pausa: i partecipanti' in SOURCE
