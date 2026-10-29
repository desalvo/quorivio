#!/usr/bin/env bash
# Disposable multi-architecture OCI runtime acceptance. Requires Docker and QEMU
# (for ARM64 on x86_64); never pushes any image or retains test credentials.
set -Eeuo pipefail

if [[ $# -ne 2 ]]; then
  echo 'usage: ci_oci_runtime_smoke.sh <local-image> <amd64|arm64>' >&2
  exit 2
fi
image="$1"; target="$2"
case "$target" in amd64|arm64) ;; *) echo 'invalid target architecture' >&2; exit 2;; esac
[[ "$image" =~ ^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,180}$ ]] || { echo 'invalid image reference' >&2; exit 2; }
command -v docker >/dev/null || { echo 'docker runtime missing' >&2; exit 1; }
command -v openssl >/dev/null || { echo 'openssl missing' >&2; exit 1; }
# Per-run disposable secrets, never committed, printed or persisted.
pg_password="$(openssl rand -hex 18)"
auth_secret="$(openssl rand -hex 32)"
admin_password="$(openssl rand -hex 20)"

# No reusable secrets and no port collision with other GitHub jobs.
suffix="$(printf '%s' "$image-$target-$$" | sha256sum | cut -c1-12)"
network="quorivio-oci-$suffix"
postgres="quorivio-oci-db-$suffix"
service="quorivio-oci-app-$suffix"
cleanup() {
  docker rm -f "$service" "$postgres" >/dev/null 2>&1 || true
  docker network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker image inspect "$image" >/dev/null
docker network create --internal "$network" >/dev/null
# The network is intentionally isolated from the Internet. Secrets only belong
# to ephemeral containers, and are never logged or written into artifacts.
docker run -d --name "$postgres" --network "$network" \
  -e POSTGRES_DB=quorivio_ci -e POSTGRES_USER=quorivio_ci \
  -e POSTGRES_PASSWORD="$pg_password" \
  --health-cmd='pg_isready -U quorivio_ci -d quorivio_ci' \
  --health-interval=2s --health-retries=40 --health-timeout=2s \
  postgres:18-alpine >/dev/null
for i in $(seq 1 60); do
  health="$(docker inspect --format '{{.State.Health.Status}}' "$postgres" 2>/dev/null || true)"
  [[ "$health" == healthy ]] && break
  [[ "$health" != unhealthy ]] || { echo 'PostgreSQL health failed' >&2; exit 1; }
  sleep 1
done
[[ "$(docker inspect --format '{{.State.Health.Status}}' "$postgres")" == healthy ]] || { echo 'PostgreSQL timeout' >&2; exit 1; }

# Distinctly execute the configured CPU architecture, not just a manifest
# inspection. Verify the production image runs as a non-root UID and contains
# both its compiled API and UI assets.
docker run --rm --platform "linux/$target" --entrypoint node "$image" -e '
const fs=require("fs");
if(process.arch!==process.argv[1]||process.getuid()===0)process.exit(42);
for(const p of ["/app/apps/api/dist/server.js","/app/apps/web/dist/index.html"]){if(!fs.statSync(p).isFile())process.exit(43)}
if(fs.existsSync("/usr/local/bin/npm"))process.exit(44);
' "$target"

# Production server must boot against a separate real PostgreSQL 18 container,
# serve readiness and HTML, and stay healthy as a non-root process. The host
# port is dynamically allocated and bound to loopback only.
docker run -d --name "$service" --platform "linux/$target" --network "$network" \
  --tmpfs /app/assets:rw,uid=1000,gid=1000,mode=0700 \
  -e NODE_ENV=production -e PORT=8080 \
  -e DATABASE_URL="postgres://quorivio_ci:$pg_password@$postgres:5432/quorivio_ci" \
  -e AUTH_SECRET="$auth_secret" \
  -e ADMIN_EMAIL=admin@example.invalid \
  -e ADMIN_PASSWORD="$admin_password" \
  -e PUBLIC_BASE_URL=http://127.0.0.1:8080 \
  "$image" >/dev/null

ready=0
for i in $(seq 1 90); do
  [[ "$(docker inspect --format '{{.State.Running}}' "$service" 2>/dev/null || echo false)" == true ]] || { echo 'runtime process exited before readiness' >&2; exit 1; }
  if docker exec "$service" node -e '
(async()=>{
 for(const route of ["/api/health/ready","/api/health/live","/"]){
  const r=await fetch("http://127.0.0.1:8080"+route,{signal:AbortSignal.timeout(2000)});
  if(!r.ok)process.exit(1);
  if(route==="/" && !/<html/i.test(await r.text()))process.exit(2);
 }
})().catch(()=>process.exit(3));' >/dev/null 2>&1; then
    ready=1; break
  fi
  sleep 2
done
[[ "$ready" == 1 ]] || { echo 'image failed real PostgreSQL + HTTP readiness' >&2; exit 1; }
# No production logs or credentials in the output. CI-specific timing is not
# production HA, Kubernetes, Podman or RTO/RPO acceptance.
echo "PASS isolated OCI $target non-root PostgreSQL 18 + live/ready + HTML runtime smoke (CI only)"
