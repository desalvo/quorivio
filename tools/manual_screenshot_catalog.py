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
# A verified historic gallery may illustrate local PDFs. Current-commit CI
# builds MUST use SCREENSHOTS and --require-real instead of this fallback.
HISTORIC_SCREENSHOTS = ROOT / 'docs/assets/manual-evidence-rc283'
LATEST_ARCHIVED_SCREENSHOTS = ROOT / 'docs/assets/manual-evidence-rc291'
LATEST_ARCHIVED_COMMIT = '1501e9f4250161d43d8e928142a31406a75b56b8'
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
 'editor-thumbnails-widgets': ('presenter',),
 'editor-widget-context': ('presenter',),
 'editor-widget-format': ('presenter',),
 'editor-widget-format-resized': ('presenter',),
 'editor-widget-format-tabs': ('presenter',),
 'editor-schema': ('presenter',),
 'editor-schema-inspector': ('presenter',),
 'rehearsal-participant': ('presenter','user'),
 'rehearsal-side-by-side': ('presenter','user'),
 'rehearsal-side-by-side-smartphone': ('presenter','user'),
 'participant-widescreen': ('user',),
 'presenter-live-secondary': ('presenter',),
 'session-attachments-collapsed': ('presenter','admin'),
 'session-attachments-expanded': ('presenter','admin'),
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
 'editor-thumbnails-widgets': ('Le miniature riproducono domanda, opzioni, tempo e altri contenuti di esempio.', 'Page thumbnails reproduce the sample question, choices, timer and other authored widgets.'),
 'editor-widget-context': ('Menu contestuale reale con scorrimento indipendente e V/F sintetico.', 'Actual independently scrollable widget context menu with compact true/false choices.'),
 'editor-widget-format': ('Finestra reale di formattazione del widget prima del ridimensionamento.', 'Actual widget-formatting window before resizing.'),
 'editor-widget-format-resized': ('Finestra Formato widget dopo il ridimensionamento esplicito.', 'Widget Formatting after explicitly resizing the outer window.'),
 'editor-widget-format-tabs': ('Formato widget dopo il cambio scheda: dimensioni impostate dall’utente conservate.', 'Widget Formatting after switching to Contents, retaining the user-resized outer dimensions.'),
 'editor-schema': ('Editor degli schemi e barra di formattazione master.', 'Master scheme editor and master formatting ribbon.'),
 'editor-schema-inspector': ('Pannello delle proprietà delle widget nello schema.', 'Widget inspector in the master editor.'),
 'rehearsal-participant': ('Anteprima del partecipante con input simulati.', 'Participant rehearsal with simulated inputs.'),
 'rehearsal-side-by-side': ('Confronto reale delle viste presentatore e partecipante.', 'Real side-by-side presenter and audience preview.'),
 'rehearsal-side-by-side-smartphone': ('Anteprima affiancata con dispositivo partecipante impostato su smartphone.', 'Side-by-side rehearsal with the participant device switched to smartphone.'),
 'participant-widescreen': ('Pagina 16:9 sul telefono del partecipante.', '16:9 session slide on a participant phone.'),
 'presenter-live-secondary': ('Seconda vista di proiezione dal vivo con sessione sintetica.', 'Second real live-projection view using a synthetic session.'),
 'session-attachments-collapsed': ('Pannello allegati chiuso per impostazione predefinita.', 'Session attachment panel collapsed by default.'),
 'session-attachments-expanded': ('Pannello allegati aperto per aggiungere o gestire risorse.', 'Attachment panel expanded to add or manage files.'),
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
    if require and path != SCREENSHOTS:
        raise ValueError('Current-build screenshots must come from the active CI capture directory')
    # Local checked-in manuals keep genuinely photographed examples with their
    # original RC283 commit provenance. This can never satisfy CI --require-real.
    if not require and path == SCREENSHOTS and not (path / 'capture.json').is_file():
        path = LATEST_ARCHIVED_SCREENSHOTS if LATEST_ARCHIVED_SCREENSHOTS.is_dir() else HISTORIC_SCREENSHOTS
    historic = path in (HISTORIC_SCREENSHOTS, LATEST_ARCHIVED_SCREENSHOTS)
    if path == SCREENSHOTS and (path / 'capture.json').is_file() and not commit:
        raise ValueError('Active screenshot evidence requires a matching source Git commit')
    # Archived images keep their original provenance, never the current build.
    source_commit = (LATEST_ARCHIVED_COMMIT if path == LATEST_ARCHIVED_SCREENSHOTS else
                     '0bb89e6ac79ed57493130f06fc5042182a166ed6' if path == HISTORIC_SCREENSHOTS else commit)
    data = evidence(path, expected_commit=source_commit, minimum=9 if require else 0)
    images=[]
    for stem in CATALOG:
        if role not in CATALOG[stem] or stem not in data['shots']:continue
        caption=CAPTIONS[stem][0 if lang=='it' else 1]
        label=('SCHERMATA REALE' if lang=='it' else 'REAL APP SCREENSHOT')
        source_dir = ('manual-evidence-rc291' if path == LATEST_ARCHIVED_SCREENSHOTS else
                      'manual-evidence-rc283' if historic else 'manual-screenshots')
        provenance = (('ARCHIVIO RC291' if lang=='it' else 'RC291 ARCHIVE') if path == LATEST_ARCHIVED_SCREENSHOTS else
                      ('ARCHIVIO RC283' if lang=='it' else 'RC283 ARCHIVE') if historic else
                      ('BUILD CORRENTE' if lang=='it' else 'CURRENT BUILD'))
        images.append(f'<figure><img src="../assets/{source_dir}/{stem}.png" alt="{caption}"/><figcaption>{label} · {provenance} · {caption}</figcaption></figure>')
    if require and len(images)<3:
        raise ValueError(f'Too few screenshot examples for {role}')
    return '\n'.join(images)
