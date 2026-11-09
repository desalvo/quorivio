#!/usr/bin/env python3
"""Real browser screenshot evidence: strict provenance, exact image hashes.

CI-generated screenshot bytes are never silently labelled as real unless the
capture manifest proves a live loopback Chromium + PostgreSQL session.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / 'docs/assets/manual-screenshots'
CAPTURE_FILE = SCREENSHOTS / 'capture.json'
# Figures are included only for roles where they explain an actual workflow.
CATALOG = {
 'login-desktop': ('user','presenter','admin'),
 'workspace-desktop': ('presenter','admin'),
 'admin-server-settings': ('admin',),
 'admin-backups': ('admin',),
 'admin-audit': ('admin',),
 'admin-users': ('admin',),
 'editor-canvas': ('presenter',),
 'editor-widget-properties': ('presenter',),
 'rehearsal-presenter': ('presenter',),
 'rehearsal-smartphone': ('presenter','user'),
 'participant-entry-smartphone': ('user',),
 'participant-question-smartphone': ('user',),
 'participant-feedback-smartphone': ('user',),
 'presenter-live': ('presenter',),
}
CAPTIONS = {
 'login-desktop': ('Accesso alla vera interfaccia; credenziali di prova non mostrate.', 'Actual sign-in interface; test credentials are not displayed.'),
 'workspace-desktop': ('Workspace presentatore su istanza temporanea con dati di esempio.', 'Presenter workspace on a disposable instance with sample data.'),
 'admin-server-settings': ('Impostazioni del server: panoramica della configurazione.', 'Server settings: configuration overview.'),
 'admin-backups': ('Pannello reale di backup completo e storico delle esecuzioni.', 'Actual full-instance backup configuration and run history.'),
 'admin-audit': ('Ricerca e retention dell’audit amministrativo.', 'Administrative audit search and retention.'),
 'admin-users': ('Gestione degli utenti e delle approvazioni.', 'User administration and approval workflow.'),
 'editor-canvas': ('Editor grafico con widget e canvas di esempio.', 'Graphical editor with sample widgets and canvas.'),
 'editor-widget-properties': ('Controlli di proprietà dei widget disponibili nell’editor.', 'Widget-property controls available in the editor.'),
 'rehearsal-presenter': ('Anteprima del presentatore senza inviare risposte reali.', 'Presenter rehearsal preview without real submissions.'),
 'rehearsal-smartphone': ('Anteprima smartphone sullo stesso progetto.', 'Smartphone rehearsal preview of the same project.'),
 'participant-entry-smartphone': ('Accesso da smartphone a una sessione temporanea.', 'Joining a disposable session from a smartphone.'),
 'participant-question-smartphone': ('Risposta a una domanda sullo smartphone.', 'Answering a question on a phone.'),
 'participant-feedback-smartphone': ('Conferma di invio visualizzata dal partecipante.', 'Submission confirmation visible to the participant.'),
 'presenter-live': ('Schermo reale di proiezione del presentatore.', 'Actual presenter projection screen.'),
}


def validate_capture_environment(base: str | None = None) -> str:
    """Refuse remote and production targets, including URL userinfo tricks."""
    value = base or os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
    try:
        target = urlsplit(value)
        port = target.port
    except ValueError as exc:
        raise ValueError('Malformed disposable origin') from exc
    if (target.scheme != 'http' or target.hostname not in ('localhost','127.0.0.1')
            or port is None or not (1 <= port <= 65535) or target.username
            or target.password or target.path not in ('','/') or target.query or target.fragment):
        raise ValueError('Only disposable loopback HTTP can be captured')
    if not (os.environ.get('QUORIVIO_CI_ADMIN_EMAIL','').endswith('@example.com')
            and os.environ.get('QUORIVIO_CI_NEW_PASSWORD')
            and os.environ.get('QUORIVIO_CI_LOAD_TOKEN')):
        raise RuntimeError('A synthetic CI admin and a disposable load token are required')
    sha = os.environ.get('GITHUB_SHA','')
    if sha and not re.fullmatch('[0-9a-f]{40}',sha):
        raise ValueError('Invalid Git SHA')
    return f'http://{target.hostname}:{port}'

def evidence(path: Path = SCREENSHOTS, *, expected_commit: str | None = None, minimum: int = 1) -> dict:
    manifest = path / 'capture.json'
    if not manifest.is_file():
        if minimum == 0: return {'shots': {}, 'source': 'absent'}
        raise ValueError('Real screenshot capture manifest missing; run disposable Chromium capture')
    data = json.loads(manifest.read_text(encoding='utf8'))
    if data.get('source') != 'disposable-postgresql-chromium-live-app' or data.get('fixture') != 'synthetic-only':
        raise ValueError('Screenshot provenance is not a real disposable app run')
    commit = data.get('commit','')
    if expected_commit and commit != expected_commit:
        raise ValueError('Outdated screenshots: commit mismatch')
    if commit and not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('Invalid screenshot commit')
    shots = data.get('shots')
    if not isinstance(shots, dict) or len(shots) < minimum:
        raise ValueError('Insufficient captured screenshots')
    for stem, item in shots.items():
        if stem not in CATALOG or not isinstance(item, dict):
            raise ValueError('Unknown screenshot evidence')
        filename = stem + '.png'
        file = path / filename
        if not file.is_file() or not file.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Missing or invalid real screenshot: ' + filename)
        if hashlib.sha256(file.read_bytes()).hexdigest() != item.get('sha256'):
            raise ValueError('Screenshot checksum mismatch: ' + filename)
        if item.get('width',0) < 300 or item.get('height',0) < 200:
            raise ValueError('Screenshot too small: ' + filename)
    return data


def gallery(role: str, lang: str, path: Path = SCREENSHOTS, *, require: bool = False, commit: str | None = None) -> str:
    if require and not commit:
        raise ValueError('A full source Git commit is mandatory when publishing authentic screenshots')
    data = evidence(path, expected_commit=commit if require else None, minimum=9 if require else 0)
    images=[]
    for stem in CATALOG:
        if role not in CATALOG[stem] or stem not in data['shots']:continue
        caption=CAPTIONS[stem][0 if lang=='it' else 1]
        label=('SCHERMATA REALE' if lang=='it' else 'REAL APP SCREENSHOT')
        images.append(f'<figure><img src="../assets/manual-screenshots/{stem}.png" alt="{caption}"/><figcaption>{label} · {caption} · Build {data.get("commit", "")[:12] or "local disposable"}.</figcaption></figure>')
    if require and len(images)<3:
        raise ValueError(f'Too few screenshot examples for {role}')
    return '\n'.join(images)
