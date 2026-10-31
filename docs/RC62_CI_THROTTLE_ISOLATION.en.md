# Quorivio 0.1.0-dev — RC62 — standard CI run 41186895267 remediation

**Date:** 31 October 2026. **Last maintainer-confirmed commit:** `5a088fc300037b5a6a98a533de36ac6700b3b765`, failing standard CI [run 41186895267, job 124495541784](https://github.com/desalvo/quorivio/actions/runs/41186895267/job/124495541784). RC62 is an **uncommitted** change following that maintainer commit.

## Proven failure

The `validate` job passed reproducible installation, **546/546 API** and **99/99 frontend** Node unit tests, the API/frontend builds, PostgreSQL bootstrap, both federated identity acceptance fixtures and portable/profile acceptance. It then failed in `tools/ci_background_library_postgres.py` on a collaborator `GET /api/sessions/<id>/backgrounds`: **429 instead of 200**.

The API-wide PostgreSQL fixed-window limiter counts all requests from the same loopback address, capped at 100 per minute. Integration fixtures share that address. The workflow already generates a 32-byte random ephemeral load token and the server accepts it only outside `NODE_ENV=production`, with a constant-time comparison. However, the portable and background suites did not forward the token. Thus the background test eventually exceeded the shared IP budget: this was a 429 from middleware, **not** an application authorization failure.

## Patch

- New `tools/ci_http_isolation.py` requires a 32–256 character printable ephemeral token, allows only disposable HTTP loopback hosts and a port, and blocks external/userinfo/path/query/fragment URLs before any request.
- Both `tools/ci_portable_http.py` and `tools/ci_background_library_postgres.py` attach `X-Quorivio-Load-Token` to all HTTP methods; missing token fails before network access. Expected negative 401/403/404/409 checks are untouched.
- `.github/workflows/ci.yml` passes the existing ephemeral secret to both tests, not to production. No changes to the server's real limiter, user auth, DB, or deployment.
- Python regression tests cover every method, absent/invalid tokens, external-origin prevention, workflow wiring and production limiter behavior.

## Release qualification

Local Python tests can validate headers without PostgreSQL; only a new GitHub run can confirm the full integration chain. No evidence from the failed run was credited as a completed RC gate. **Verified score stays 81.75% (38 accepted, 17 partial of 55).** Strict RC and publication remain disabled. Physical RWX, network/browser acceptance and independent reviews remain outstanding. No assistant commit, push, tag or release.
