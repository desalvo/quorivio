#!/usr/bin/env python3
"""Mandatory RC341 real Chromium/LibreOffice export in the built converter image.

No external URLs, account credentials, user sessions or persistent documents.
The stub serves the REAL compiled React bundle taken from the built app image.
The converter runs with production-like read-only isolation and private HTTP.
"""
from __future__ import annotations
import contextlib
import http.server
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MAX_DOC = 50 * 1024 * 1024

def cmd(*args, timeout=90):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)

def fixture():
    session_id = str(uuid4())
    presenter_id, audience_id, second_id = (str(uuid4()) for _ in range(3))
    activities = [
        {"portable_id": presenter_id, "title": "Visual gate presenter",
         "type": "slide", "position": 1, "page_design": {
             "audiencePageId": audience_id,
             "backgroundColor": "#f8fafc",
             "widgets": [{"id": "ci-head", "kind": "text", "label": "Real visual export CI",
                          "position": {"x": 12, "y": 15, "width": 75, "height": 20}}]}},
        {"portable_id": audience_id, "title": "Participant mapped page",
         "type": "slide", "position": 2, "page_design": {
             "presenterHidden": True, "backgroundColor": "#f0fdf4",
             "widgets": [{"id": "ci-part", "kind": "text", "label": "Participant view",
                          "position": {"x": 16, "y": 15, "width": 75, "height": 20}}]}},
        {"portable_id": second_id, "title": "Visual gate second presenter",
         "type": "slide", "position": 3,
         "page_design": {"backgroundColor": "#eff6ff", "widgets": []}},
    ]
    deck = {"format": "quorivio-session", "version": 1, "capture_session_id": session_id,
            "session": {"title": "CI synthetic visual export", "theme": {"master": {"widgets": []}}},
            "activities": activities}
    pages = [{**a, "id": a["portable_id"], "status": "open", "duration_seconds": None}
             for a in activities]
    snapshot = {
        "session": {"id": session_id, "title": "CI synthetic visual export",
                    "status": "draft", "theme": {"master": {"widgets": []}},
                    "join_code": "", "join_url": "", "current_activity_id": None,
                    "presenter_activity_id": None},
        "activities": pages, "results": [], "totals": [],
        "connected_participants": 0, "responded_connected_participants": 0,
        "capture_profiles": [], "capture_widget_results": {"widgets": [], "ratings": [], "reactions": []},
    }
    return deck, snapshot

def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("This isolated image test must run only on a disposable GitHub runner")
    with tempfile.TemporaryDirectory(prefix="quorivio-rc341-") as raw:
        base = Path(raw)
        dist, work = base / "dist", base / "conversions"
        work.mkdir(mode=0o755)
        container = None
        worker_name = "quo-rc341-" + secrets.token_hex(5)
        docker_export = cmd("docker", "create", "quorivio:gate").stdout.strip()
        try:
            cmd("docker", "cp", docker_export + ":/app/apps/web/dist", str(dist))
        finally:
            cmd("docker", "rm", docker_export)
        if not (dist / "index.html").is_file():
            raise RuntimeError("Published app image lacks its compiled React entrypoint")

        deck, snapshot = fixture()
        token = secrets.token_hex(32)
        jobs: dict[str, str] = {}
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(dist), **kwargs)

            def log_message(self, fmt, *args):
                # No request path, capability, payload or token ever enters CI logs.
                return

            def do_GET(self):
                route = urlsplit(self.path).path
                match = re.fullmatch(r"/api/export-render/([0-9a-f]{32})", route)
                if match:
                    job = match.group(1)
                    if jobs.get(job) != self.headers.get("x-quorivio-capture-token"):
                        self.send_error(404)
                        return
                    payload = json.dumps(snapshot, ensure_ascii=False).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return
                if re.fullmatch(r"/export-render/[0-9a-f]{32}", route):
                    content = (dist / "index.html").read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                return super().do_GET()

        web = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=web.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:" + str(web.server_port)
        try:
            # Bind only a disposable directory; host networking stays on the
            # ephemeral GitHub runner and is never part of a deployed image.
            args = [
                "docker", "run", "-d", "--name", worker_name,
                "--network", "host", "--read-only", "--security-opt", "no-new-privileges",
                "--pids-limit", "256", "--memory", "2g", "--cpus", "2",
                "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m",
                "--mount", "type=bind,src=" + str(work) + ",dst=/conversions",
                "-e", "QUORIVIO_WORKER_TOKEN=" + token,
                "-e", "QUORIVIO_CONVERSION_DIR=/conversions",
                "-e", "QUORIVIO_CAPTURE_BASE_URL=" + url,
                "quorivio-converter:gate"
            ]
            container = cmd(*args, timeout=25).stdout.strip()
            for _ in range(60):
                try:
                    with urlopen("http://127.0.0.1:8099/health", timeout=2) as result:
                        if result.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(.5)
            else:
                raise RuntimeError("Real converter health endpoint not ready")

            for view in ("presenter", "participant"):
                for fmt in ("pptx", "pdf"):
                    job = secrets.token_hex(16)
                    workspace = work / job
                    workspace.mkdir(mode=0o777)
                    workspace.chmod(0o777)  # synthetic fixture; worker is unprivileged UID 1000
                    (workspace / "portable.json").write_text(json.dumps(deck))
                    (workspace / "capture-token").write_text(secrets.token_hex(32))
                    (workspace / "export-view").write_text(view)
                    jobs[job] = (workspace / "capture-token").read_text()
                    route = "visual-export-pdf" if fmt == "pdf" else "visual-export"
                    payload = json.dumps({"job": job}).encode()
                    req = Request("http://127.0.0.1:8099/" + route,
                                  data=payload, method="POST",
                                  headers={"Authorization": "Bearer " + token,
                                           "Content-Type": "application/json"})
                    try:
                        with urlopen(req, timeout=180) as response:
                            body = json.loads(response.read(512))
                            if response.status != 200 or body.get("pages") != 2:
                                raise RuntimeError("Unexpected converter response")
                    except HTTPError as error:
                        body = error.read(512).decode("ascii", "replace")
                        # Only error name and an enumerated failure phase may be shown.
                        stage = json.loads(body).get("phase", "unknown") if body.startswith("{") else "unknown"
                        raise RuntimeError("Converter returned HTTP " + str(error.code)
                                           + " during " + str(stage)) from None

                    # Validate generated output as the converter UID because
                    # production exports are chmod 0600, not runner-readable.
                    verify = (
                        "from pathlib import Path\nimport sys,zipfile,re\n"
                        "p=Path('/conversions')/sys.argv[1]/('presentation.'+sys.argv[2])\n"
                        "assert p.is_file() and 8<=p.stat().st_size<=50*1024*1024\n"
                        "if sys.argv[2]=='pdf':\n"
                        " b=p.read_bytes(); assert b.startswith(b'%PDF-') and b'%%EOF' in b[-2048:]\n"
                        "else:\n"
                        " with zipfile.ZipFile(p) as z:\n"
                        "  names=z.namelist(); slides=[n for n in names if re.fullmatch(r'ppt/slides/slide[1-9][0-9]*.xml',n)]\n"
                        "  assert len(slides)==2 and all(b'<p:pic>' in z.read(n) for n in slides)\n"
                        "print('PASS document validated')\n"
                    )
                    cmd("docker", "exec", container, "python3", "-c", verify, job, fmt)
                    print("PASS RC341 real converter:", fmt.upper(), view, "2 slides")
                    cmd("docker", "exec", container, "python3", "-c",
                        "import pathlib,shutil,sys; shutil.rmtree(pathlib.Path('/conversions')/sys.argv[1])", job)
                    jobs.pop(job)

            print("PASS all four visual exports: compiled app + actual Chromium/LibreOffice in read-only converter image")
        except Exception:
            if container:
                logs = cmd("docker", "logs", container).stderr
                for category in ("conversion rejected:", "Error response", "Traceback"):
                    if category in logs:
                        # Whitelist only phase/error class from safe worker logging.
                        matches = re.findall(r"conversion rejected: [A-Za-z]+(?: phase=[a-z_]+)?", logs)
                        if matches:
                            print("Safe converter diagnostic:", matches[-1])
                            break
            raise
        finally:
            if container:
                subprocess.run(["docker", "rm", "-f", container], capture_output=True, timeout=20)
            web.shutdown()
            web.server_close()
            thread.join(timeout=2)
            # Container-owned 0700 generated directories are cleaned with a
            # disposable unprivileged helper rather than weakening file modes.
            if work.exists():
                subprocess.run(["docker", "run", "--rm", "--user", "1000:1000",
                                "--mount", "type=bind,src=" + str(work) + ",dst=/conversions",
                                "quorivio-converter:gate", "python3", "-c",
                                "import pathlib,shutil; [shutil.rmtree(p) for p in pathlib.Path('/conversions').iterdir()]"],
                               capture_output=True, timeout=30)

if __name__ == "__main__":
    main()
