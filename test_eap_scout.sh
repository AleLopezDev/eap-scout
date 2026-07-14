#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

for cmd in xxd text2pcap tshark; do
  command -v "${cmd}" >/dev/null || { echo "missing test dependency: ${cmd}" >&2; exit 1; }
done

printf '%s' '020000000001020000000002888e0200000a0201000a01616c696365' \
  | xxd -r -p | xxd -g1 | text2pcap -q -l 1 - "${TMPDIR}/identity.pcap" >/dev/null

out="$(bash "${ROOT}/eap-scout" "${TMPDIR}/identity.pcap")"
[[ "${out}" == *"Client: 02:00:00:00:00:02"* ]]
[[ "${out}" == *"alice (real/possibly real)"* ]]

printf 'not a capture\n' > "${TMPDIR}/invalid.cap"
! bash "${ROOT}/eap-scout" "${TMPDIR}/invalid.cap" >/dev/null 2>&1
! python3 "${ROOT}/tools/crack-eap-md5.py" 1 0011 zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz /dev/null >/dev/null 2>&1

echo "ok"
