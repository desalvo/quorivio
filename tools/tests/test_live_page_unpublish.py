"""Regression guard for live page unpublish and participant visibility."""
from pathlib import Path

SRC = (Path(__file__).resolve().parents[2] / 'apps/api/src/server.ts').read_text()

def test_close_page_clears_published_pointer():
    close = SRC.split("app.post('/api/sessions/:id/activities/:aid/close'")[1].split("app.get('/api/sessions/:id/qr'")[0]
    assert 'FOR UPDATE' in close
    assert 'current_activity_id=NULL' in close
    assert "current_activity_id=$2" in close
    assert "await cx.query('COMMIT')" in close
    assert 'await broadcast(req.params.id)' in close

def test_audience_only_sees_active_open_page():
    block = SRC.split('function participantSnapshot(data:any)')[1].split('const webRoot=')[0]
    assert "data.session.status==='active'" in block
    assert "a.status==='open'" in block
    assert 'activities:published?[publicActivity(published)]:[]' in block
    assert 'results:published&&data.session.show_results' in block

def test_public_join_requires_active_session():
    assert "AND status=$2 AND expires_at>now()" in SRC
