#!/bin/bash

# Get file to patch
if [ ${#} != 1 ]; then
    echo "usage: ${0} /path/to/repo"
    exit 1
fi

REPO=${1}

# Apply the patches to spack
echo "Applying patches from ${REPO}..."
cd ${SPACK_ROOT}
source ${REPO}/.cherry-pick
