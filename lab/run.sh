#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-cve-2026-129496}"
export PYTHONUNBUFFERED=1

LABEL="CVE-2026-129496"

down() {
  docker compose -p "${COMPOSE_PROJECT_NAME}" down --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  printf 'FAIL %s rce=no\nreason=%s\nFAIL\n' "${LABEL}" "${reason}" | tee poc-last-run.txt
  down
  exit 1
}

trap down EXIT

echo "== docker compose down =="
down

for img in php:8.4.27-apache php:8.4.28-apache; do
  if ! docker image inspect "${img}" >/dev/null 2>&1; then
    echo "== docker pull ${img} =="
    docker pull "${img}" || fail_setup "image-pull-failed:${img}"
  fi
done

echo "== docker compose up --build =="
up_ok=0
for attempt in $(seq 1 5); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up --build -d; then
    up_ok=1
    break
  fi
  echo "compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait for HTTP 127.0.0.1:18224 and 18225 =="
ok=0
for i in $(seq 1 90); do
  if python3 - <<'PY' >/dev/null 2>&1
import urllib.error
import urllib.request
for port in (18224, 18225):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/index.php", timeout=2) as resp:
            body = resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        raise SystemExit(1)
    if "CVE-2026-129496-ALIVE" not in body or "apache2handler" not in body:
        raise SystemExit(1)
PY
  then
    ok=1
    echo "http-ready attempt=${i}"
    break
  fi
  echo "http-wait attempt=${i}"
  sleep 2
done
if [[ "${ok}" != 1 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 || true
  fail_setup "http-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py
rc=$?
set -e
if ! head -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
  printf 'FAIL %s rce=no\npoc-exit=%s\nFAIL\n' "${LABEL}" "${rc}" | tee poc-last-run.txt
  exit 1
fi
exit "${rc}"
