#!/usr/bin/env bash
# Optional *real* rootless-Podman acceptance. No image publication or host port.
# Run as the non-root CI account, against disposable PostgreSQL 18.
set -Eeuo pipefail
if [[ $# -ne 1 || ! "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,180}$ ]]; then
  echo 'usage: ci_rootless_podman_smoke.sh <local-image>' >&2
  exit 2
fi
image="$1"
command -v podman >/dev/null || { echo 'rootless Podman binary missing' >&2; exit 3; }
command -v openssl >/dev/null || { echo 'openssl missing' >&2; exit 3; }
command -v sha256sum >/dev/null || { echo 'sha256sum missing' >&2; exit 3; }
# Do not silently accept a rootful process or socket, including via CONTAINER_HOST.
if [[ "$(id -u)" == 0 || "$(podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)" != true ]]; then
  echo 'rootless Podman is required (not rootful Podman or Docker)' >&2
  exit 4
fi
# Podman can honor remote URLs, so ensure the test uses the CI user's local engine.
if [[ -n "${CONTAINER_HOST:-}" || -n "${DOCKER_HOST:-}" || -n "${PODMAN_HOST:-}" ]]; then
  echo 'remote container engine environment is not allowed for local rootless acceptance' >&2
  exit 4
fi
# Never print disposable secrets, image environment, or database/container logs.
pg_password="$(openssl rand -hex 18)"
auth_secret="$(openssl rand -hex 32)"
admin_password="$(openssl rand -hex 20)"
suffix="$(printf '%s' "$image-$$" | sha256sum | cut -c1-12)"
network="quorivio-podman-$suffix"
postgres="quorivio-podman-db-$suffix"
service="quorivio-podman-app-$suffix"
cleanup() {
  podman rm -f "$service" "$postgres" >/dev/null 2>&1 || true
  podman network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT
podman image exists "$image" || { echo 'rootless image is missing' >&2; exit 5; }
# Network is internal to the test; DNS stays local to the disposable containers.
podman network create --internal "$network" >/dev/null
podman run -d --name "$postgres" --network "$network" --network-alias "$postgres" \
  -e POSTGRES_DB=quorivio_ci -e POSTGRES_USER=quorivio_ci \
  -e POSTGRES_PASSWORD="$pg_password" \
  docker.io/library/postgres:18-alpine >/dev/null
pg_ready=0
for i in $(seq 1 75); do
  if podman exec "$postgres" pg_isready -q -U quorivio_ci -d quorivio_ci >/dev/null 2>&1; then
    pg_ready=1; break
  fi
  if [[ "$(podman inspect --format '{{.State.Running}}' "$postgres" 2>/dev/null || true)" != true ]]; then
    echo 'rootless PostgreSQL container exited unexpectedly' >&2; exit 6
  fi
  sleep 1
done
[[ "$pg_ready" == 1 ]] || { echo 'rootless PostgreSQL did not become ready' >&2; exit 6; }

# Do not confuse the OCI architecture with Node's process.arch (amd64 -> x64).
# The container must execute the actual Node runtime with the image's default user.
podman run --rm --entrypoint node "$image" -e '
const fs = require("fs");
if(process.arch!=="x64" && process.arch!=="arm64") process.exit(41);
if(!process.getuid || process.getuid()===0) {console.error("root process");process.exit(42)}
for(const p of ["/app/apps/api/dist/server.js","/app/apps/web/dist/index.html"]){
  if(!fs.existsSync(p)||!fs.statSync(p).isFile()) {console.error("missing compiled application");process.exit(43)}
}
if(fs.existsSync("/usr/local/bin/npm")){console.error("npm unexpectedly installed");process.exit(44)}
' >/dev/null

# Podman rejects Docker-specific tmpfs uid=/gid= options (Ubuntu 24.04).
# Podman's supported U=true sets tmpfs ownership for the image's configured
# non-root USER. Preserve mode 0700 and bound the disposable mount to 256MiB.
asset_mount='type=tmpfs,destination=/app/assets,tmpfs-size=268435456,tmpfs-mode=0700,U=true'
# Fail before boot if the unprivileged image cannot actually write this mount.
# This probes the same mount options as production without elevating privileges.
podman run --rm --mount "$asset_mount" --entrypoint node "$image" -e '
const fs = require("fs"), p = "/app/assets/.ci-probe-" + process.pid;
if(!process.getuid || process.getuid()===0) process.exit(42);
try { fs.writeFileSync(p, "ok", {flag:"wx",mode:0o600});
  if(fs.readFileSync(p,"utf8")!=="ok") process.exit(45);
  fs.unlinkSync(p);
} catch(e) { console.error("unprivileged assets tmpfs is not writable"); process.exit(46); }
' >/dev/null

podman run -d --name "$service" --network "$network" \
  --mount "$asset_mount" \
  -e NODE_ENV=production -e PORT=8080 \
  -e DATABASE_URL="postgres://quorivio_ci:$pg_password@$postgres:5432/quorivio_ci" \
  -e AUTH_SECRET="$auth_secret" \
  -e ADMIN_EMAIL=admin@example.invalid -e ADMIN_PASSWORD="$admin_password" \
  -e PUBLIC_BASE_URL=http://127.0.0.1:8080 \
  "$image" >/dev/null
ready=0
for i in $(seq 1 90); do
  [[ "$(podman inspect --format '{{.State.Running}}' "$service" 2>/dev/null || true)" == true ]] || {
    echo 'rootless application exited before readiness' >&2; exit 7;
  }
  if podman exec "$service" node -e '
(async()=>{
 for(const path of ["/api/health/ready","/api/health/live","/"]){
  const r=await fetch("http://127.0.0.1:8080"+path,{signal:AbortSignal.timeout(2000)});
  if(!r.ok || (path==="/" && !/<html/i.test(await r.text()))) process.exit(1);
 }
})().catch(()=>process.exit(2));' >/dev/null 2>&1; then
    ready=1;break
  fi
  sleep 2
done
[[ "$ready" == 1 ]] || { echo 'rootless application failed PostgreSQL and HTTP readiness' >&2; exit 7; }
echo 'PASS isolated rootless Podman PostgreSQL 18 + compiled non-root runtime + live/ready/HTML (CI only)'
