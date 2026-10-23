"""Regression coverage of widget answer key resolution and scoring."""
from pathlib import Path

SRC = (Path(__file__).resolve().parents[2] / 'apps/api/src/server.ts').read_text()


def test_single_answer_falls_back_to_legacy_when_array_empty():
    resolver = SRC.split('function widgetCorrectOptionIds(widget:any):string[]{', 1)[1].split('\n}', 1)[0]
    assert "if(multi)return Array.isArray(widget.correctOptionIds)?widget.correctOptionIds:[]" in resolver
    assert "widget.correctOptionId==='string'" in resolver
    assert 'widget.correctOptionIds.length===1' in resolver


def test_validation_and_scoring_use_same_key_resolution():
    handler = SRC.split("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'", 1)[1].split("app.get('/api/sessions/:id/widget-answers'", 1)[0]
    assert handler.count('widgetCorrectOptionIds(widget)') == 2
    assert 'new Set(correctIds).size!==correctIds.length' in handler
    assert 'answer.optionIds.length===correctIds.length' in handler
