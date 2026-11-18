#!/bin/bash
###############################################################################
# Print the full commit SHA of a mucoll-benchmarks branch, tag, or commit.
#
# Usage: resolve_benchmarks_ref.sh <ref>
#
# A validation run resolves its ref once and checks out the resulting commit in
# every job, so a push to mucoll-benchmarks during the run cannot mix revisions.
#
# Configuration is taken from the environment:
#   BENCHMARKS_REPO  repository URL (default: the MuonColliderSoft repository)
###############################################################################
set -euo pipefail

REF="${1:?usage: resolve_benchmarks_ref.sh <ref>}"
REPO="${BENCHMARKS_REPO:-https://github.com/MuonColliderSoft/mucoll-benchmarks.git}"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

git -C "${WORK_DIR}" init --quiet
git -C "${WORK_DIR}" fetch --quiet --depth 1 --filter=tree:0 "${REPO}" "${REF}"
git -C "${WORK_DIR}" rev-parse --verify 'FETCH_HEAD^{commit}'
