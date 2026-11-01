"""Regression: widget submissions are bound to a live active page within the transaction."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/api/src/server.ts').read_text()

def test_widget_response_rechecks_session_under_lock():
    endpoint = SOURCE.split("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'", 1)[1].split("app.get('/api/sessions/:id/widget-answers'", 1)[0]
    assert "await cx.query('BEGIN')" in endpoint
    assert "status='active' AND current_activity_id=$2" in endpoint
    assert 'allow_anonymous=true FOR SHARE' in endpoint
    assert "status='open' FOR SHARE" in endpoint
    assert "if(!a.rowCount)" in endpoint
    assert endpoint.index('const live=') < endpoint.index('const a=') < endpoint.index('INSERT INTO widget_answers')
