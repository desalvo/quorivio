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
from ci_http_isolation import ci_load_headers

BASE = os.environ.get('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
EMAIL = os.environ['QUORIVIO_CI_ADMIN_EMAIL']
PASSWORD = os.environ['QUORIVIO_CI_ADMIN_PASSWORD']
NEW_PASSWORD = os.environ['QUORIVIO_CI_NEW_PASSWORD']
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6X7e8AAAAASUVORK5CYII=')
OPENER = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))


def api(method: str, url: str, data=None, mime='application/json', expected=200, opener=None):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, separators=(',', ':')).encode()
    headers = {'Content-Type': mime} if data is not None else {}
    headers.update(ci_load_headers(BASE))
    req = Request(BASE + url, data=data, headers=headers, method=method)
    try:
        with (opener or OPENER).open(req, timeout=15) as response:
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
    ci_load_headers(BASE)  # fail before login if the CI environment is unsafe
    signin = api('POST', '/api/auth/login', {'email': EMAIL, 'password': PASSWORD})
    assert signin['must_change_password'] is True, 'CI expects a fresh disposable admin'
    api('POST', '/api/auth/change-password', {'current_password': PASSWORD, 'new_password': NEW_PASSWORD})
    api('POST', '/api/auth/login', {'email': EMAIL, 'password': NEW_PASSWORD})

    admin_id = api('GET', '/api/auth/me')['id']
    # Atomic user administration: role, approval and nickname must not partially persist.
    first = api('POST', '/api/admin/users', {
        'email': 'ci-profile-first@example.invalid',
        'temporary_password': 'ci-temporary-password-123', 'role': 'user'
    }, expected=201)
    second = api('POST', '/api/admin/users', {
        'email': 'ci-profile-second@example.invalid',
        'temporary_password': 'ci-temporary-password-123', 'role': 'user'
    }, expected=201)
    changed = api('PATCH', f'/api/admin/users/{first["id"]}', {
        'nickname': 'ci_first', 'role': 'presenter', 'approved': False
    })
    assert changed['nickname'] == 'ci_first' and changed['role'] == 'presenter' and not changed['approved']
    # A conflicting nickname must roll back the whole admin update.
    api('PATCH', f'/api/admin/users/{second["id"]}', {
        'nickname': 'ci_first', 'role': 'moderator', 'approved': False
    }, expected=409)
    users = api('GET', '/api/admin/users')
    current = next(u for u in users if u['id'] == second['id'])
    assert current['nickname'] is None and current['role'] == 'user' and current['approved']
    api('PATCH', f'/api/admin/users/{second["id"]}', {
        'nickname': 'invalid space', 'role': 'moderator', 'approved': False
    }, expected=400)
    api('PATCH', f'/api/admin/users/{first["id"]}', {
        'nickname': 'ci_first', 'role': 'presenter', 'approved': True
    })
    # The immutable primary admin cannot be demoted or renamed via the unified route.
    api('PATCH', f'/api/admin/users/{admin_id}', {
        'nickname': 'other', 'role': 'platform_admin', 'approved': True
    }, expected=409)
    before = api('GET', '/api/admin/settings')
    api('PATCH', '/api/admin/settings', {'closed_session_retention_days': 40, 'max_upload_mb': 0}, expected=400)
    assert api('GET', '/api/admin/settings') == before, 'partial admin settings update was persisted'
    # Platform retention is the DEFAULT for new sessions; each session may override it.
    api('PATCH', '/api/admin/settings', {'closed_session_retention_days': 7})
    retention_session = api('POST', '/api/sessions', {'title': 'CI retention policy'}, expected=201)
    assert retention_session['retention_days'] == 7, 'new session ignored admin retention default'
    api('PATCH', f'/api/sessions/{retention_session["id"]}/retention', {'retention_days': 3})
    assert api('GET', f'/api/sessions/{retention_session["id"]}')['session']['retention_days'] == 3
    api('PATCH', '/api/admin/settings', {'closed_session_retention_days': int(before['closed_session_retention_days'])})
    assert api('GET', f'/api/sessions/{retention_session["id"]}')['session']['retention_days'] == 3, 'admin change must not overwrite session-specific policy'


    # The same authenticated profile API works for every approved account role.
    profile = api('GET', '/api/auth/profile')
    assert profile['email'] == EMAIL and profile['profile_photo_url'] is None
    api('PATCH', '/api/auth/profile', {'display_name': 'CI Presenter Profile'})
    assert api('GET', '/api/auth/profile')['display_name'] == 'CI Presenter Profile'
    # Metadata validation must reject spoofed and decompression-bomb images.
    malformed = bytearray(PNG)
    malformed[16:20] = (4097).to_bytes(4, 'big')
    api('POST', '/api/auth/profile/photo', bytes(malformed), 'image/png', expected=415)
    assert api('GET', '/api/auth/profile')['profile_photo_url'] is None
    photo = api('POST', '/api/auth/profile/photo', PNG, 'image/png', 201)
    assert api('GET', photo['profile_photo_url']) == PNG
    assert api('GET', '/api/auth/profile')['profile_photo_url'] == photo['profile_photo_url']
    # An anonymous participant sees only a scoped public URL for an active session.
    session_for_photo = api('POST', '/api/sessions', {'title': 'CI public presenter profile'}, expected=201)
    sid_photo = session_for_photo['id']
    code_photo = session_for_photo['join_code']
    api('POST', f'/api/sessions/{sid_photo}/status', {'status': 'active'})
    anonymous = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    profiles = api('GET', f'/api/join/{code_photo}/presenter-profiles', opener=anonymous)
    assert len(profiles) == 1 and profiles[0]['name'] == 'CI Presenter Profile'
    assert 'email' not in profiles[0] and 'profile_photo_url' not in profiles[0]
    assert profiles[0]['photo_url'].startswith(f'/api/join/{code_photo}/presenters/')
    assert api('GET', profiles[0]['photo_url'], opener=anonymous) == PNG
    api('GET', photo['profile_photo_url'], expected=401, opener=anonymous)
    # Replacement revokes old media, and the public URL follows the current photo.
    replacement = api('POST', '/api/auth/profile/photo', PNG, 'image/png', 201)
    assert replacement['profile_photo_url'] != photo['profile_photo_url']
    api('GET', photo['profile_photo_url'], expected=404)
    assert api('GET', profiles[0]['photo_url'], opener=anonymous) == PNG
    api('DELETE', '/api/auth/profile/photo')
    api('GET', replacement['profile_photo_url'], expected=404)
    api('GET', profiles[0]['photo_url'], expected=404, opener=anonymous)
    assert api('GET', f'/api/join/{code_photo}/presenter-profiles', opener=anonymous)[0]['photo_url'] is None
    api('POST', f'/api/sessions/{sid_photo}/status', {'status': 'closed'})
    api('GET', f'/api/join/{code_photo}/presenter-profiles', expected=404, opener=anonymous)

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

    # PostgreSQL DATE must be serialized as YYYY-MM-DD, never as a JS Date timestamp.
    exported_json = api('GET', f'/api/sessions/{sid}/export.json')
    assert exported_json['session']['reference_date'] == session['reference_date'][:10], 'portable reference date changed during export'
    assert len(exported_json['session']['reference_date']) == 10, 'portable reference date must use YYYY-MM-DD'
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

    # A closed source is explicitly duplicable by its owner/collaborator;
    # the new object is a fresh draft with independent access credentials.
    api('POST', f'/api/sessions/{sid}/status', {'status': 'closed'})
    source_closed = api('GET', f'/api/sessions/{sid}')
    assert source_closed['session']['status'] == 'closed'
    duplicated = api('POST', f'/api/sessions/{sid}/duplicate', {}, expected=201)
    assert duplicated['status']=='draft' and duplicated['data_copied'] is False and duplicated['source_status']=='closed'
    copy = api('GET', f'/api/sessions/{duplicated["id"]}')
    assert copy['session']['status']=='draft' and copy['session']['join_code'] != source_closed['session']['join_code']
    assert copy['session']['id'] != source_closed['session']['id']
    assert copy['activities'][0]['id'] != source_closed['activities'][0]['id']
    assert copy['session'].get('current_activity_id') is None

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
    print('PASS PostgreSQL HTTP: atomic profile, photo dimensions, anonymous session avatars, revocation, bundle import/duplication, invalid ZIP')


if __name__ == '__main__':
    run()
