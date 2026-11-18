#!/bin/bash
###############################################################################
# Print the mucoll-stack version that a git ref must build.
#
# Usage: resolve_stack_version.sh <tag-or-branch-name>
#
#   v3.2, v3.2-rc1, release/v3.2  ->  3.2
#   any other ref                 ->  nothing (nightly build, dated version)
#
# Fails if a release ref names a version that the mucoll-stack recipe does not
# define, because spack would otherwise accept the undefined bundle version.
###############################################################################
set -euo pipefail

REF="${1:?usage: resolve_stack_version.sh <tag-or-branch-name>}"
RECIPE="$(cd "$(dirname "$0")/.." && pwd)/packages/mucoll-stack/package.py"

if [[ ! "${REF}" =~ ^(release/)?v([0-9]+\.[0-9]+(\.[0-9]+)*)(-rc[0-9]+)?$ ]]; then
  exit 0
fi
VERSION="${BASH_REMATCH[2]}"

if ! grep -qF "version(\"${VERSION}\")" "${RECIPE}"; then
  echo "ERROR: ${REF} needs version(\"${VERSION}\") in ${RECIPE}" >&2
  exit 1
fi
echo "${VERSION}"
