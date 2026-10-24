#!/usr/bin/env python3
"""Real PostgreSQL-backed API smoke for portable media, collision handling and profile uploads.

Run only against a disposable CI instance with a disposable bootstrap administrator.
No runtime credentials or media are printed to logs. Requires Python stdlib only.
"""
from __future__ import annotations
import base64
import http.cookiejar
import json
import os
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = os.environ.get('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
EMAIL = os.environ['QUORIVIO_CI_ADMIN_EMAIL']
PASSWORD = os.environ['QUORIVIO_CI_ADMIN_PASSWORD']
NEW_PASSWORD = os.environ['QUORIVIO_CI_NEW_PASSWORD']
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6X7e8AAAAASUVORK5CYII=')
OPENER = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))


def api(method: str, url: str, data=None, mime='application/json', expected=200):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, separators=(',', ':')).encode()
    headers = {'Content-Type': mime} if data is not None else {}
    req = Request(BASE + url, data=data, headers=headers, method=method)
    try:
        with OPENER.open(req, timeout=15) as response:
            status, body = response.status, response.read()
    except HTTPError as err:
        status, body = err.code, err.read()
    assert status == expected, f'{method} {url}: status {status} (expected {expected}), body {body[:300]!r}'
    if not body:
        return None
    return json.loads(body) if body[:1] in (b'{', b'[') else body


def asset_id(snapshot):
    page = snapshot['activities'][0]['page_design']
    return page['widgets'][0]['assetId']


def run():
    signin = api('POST', '/api/auth/login', {'email': EMAIL, 'password': PASSWORD})
    assert signin['must_change_password'] is True, 'CI expects a fresh disposable admin'
    api('POST', '/api/auth/change-password', {'current_password': PASSWORD, 'new_password': NEW_PASSWORD})
    api('POST', '/api/auth/login', {'email': EMAIL, 'password': NEW_PASSWORD})

    before = api('GET', '/api/admin/settings')
    api('PATCH', '/api/admin/settings', {'closed_session_retention_days': 40, 'max_upload_mb': 0}, expected=400)
    assert api('GET', '/api/admin/settings') == before, 'partial admin settings update was persisted'

    photo = api('POST', '/api/auth/profile/photo', PNG, 'image/png', 201)
    assert api('GET', photo['profile_photo_url']) == PNG
    api('DELETE', '/api/auth/profile/photo')
    api('GET', photo['profile_photo_url'], expected=404)

    session = api('POST', '/api/sessions', {'title': 'CI portable media integration'}, expected=201)
    sid = session['id']
    act = api('POST', f'/api/sessions/{sid}/activities', {
        'title': 'Image and responses', 'type': 'poll',
        'options': [{'id': 'yes', 'label': 'Yes'}, {'id': 'no', 'label': 'No'}]
    }, expected=201)
    image = api('POST', f'/api/sessions/{sid}/assets', PNG, 'image/png', 201)
    src = image['id']
    api('PATCH', f'/api/sessions/{sid}/activities/{act["id"]}/design', {
        'page_design': {'widgets': [{'id': 'pic1', 'kind': 'image', 'assetId': src,
                                    'position': {'x': 5, 'y': 5, 'width': 40, 'height': 40}}]},
        'result_design': {'backgroundAssetId': src}
    })
    original = api('GET', f'/api/sessions/{sid}')
    assert asset_id(original) == src
    assert original['activities'][0]['result_design']['backgroundAssetId'] == src

    archive = api('GET', f'/api/sessions/{sid}/export.quorivio')
    assert archive[:4] == b'PK\x03\x04'
    ids = []
    for _ in range(2):
        imported = api('POST', '/api/sessions/import.quorivio', archive,
                       'application/vnd.quorivio.session+zip', 201)
        view = api('GET', f'/api/sessions/{imported["id"]}')
        iid = asset_id(view)
        assert iid != src and iid not in ids, 'asset primary key reused'
        assert iid == view['activities'][0]['result_design']['backgroundAssetId'], 'shared reference broken'
        assert api('GET', f'/api/sessions/{imported["id"]}/assets/{iid}') == PNG
        ids.append(iid)

    duplicated = api('POST', f'/api/sessions/{sid}/duplicate', {}, expected=201)
    copy = api('GET', f'/api/sessions/{duplicated["id"]}')
    cid = asset_id(copy)
    assert cid not in ids and cid != src
    assert copy['activities'][0]['result_design']['backgroundAssetId'] == cid
    assert api('GET', f'/api/sessions/{duplicated["id"]}/assets/{cid}') == PNG
    api('DELETE', f'/api/sessions/{duplicated["id"]}', expected=204)
    assert api('GET', f'/api/sessions/{sid}/assets/{src}') == PNG

    malformed = bytearray(archive)
    malformed[-1] ^= 0x10
    api('POST', '/api/sessions/import.quorivio', bytes(malformed),
        'application/vnd.quorivio.session+zip', expected=400)
    print('PASS PostgreSQL-backed HTTP: admin atomicity, private photo lifecycle, PNG bundle import twice, collision-free duplication, invalid ZIP rejection')


if __name__ == '__main__':
    run()
