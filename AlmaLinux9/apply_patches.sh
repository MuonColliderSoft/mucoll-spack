#!/bin/bash

function usage() {
    echo "usage: ${0} [-f] /path/to/repo"
    echo ""
    echo "Options"
    echo " -f: Force patch application if ref check fails."
}

# Get steering options
OPTSTRING=":f"

FORCE=0 # Do not force

while getopts ${OPTSTRING} opt; do
    case ${opt} in
        f)
            FORCE=1
            ;;
        ?)
            echo "Invalid option: -${OPTARG}"
            usage
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Get file to patch
if [ ${#} != 1 ]; then
    usage
    exit 1
fi

REPO=$(realpath ${1})

# Determine what commit of spack we have
if [ -z "${SPACK_ROOT+x}" ]; then
    echo "No spack detected."
    exit 1
fi
cd ${SPACK_ROOT}
SPACK_COMMIT=$(git rev-parse HEAD)

# Determine key4hep supported spack commit
SPACK_COMMIT_REPO=$(cat ${REPO}/.latest-commit)

if [ "${SPACK_COMMIT}" != "${SPACK_COMMIT_REPO}" ]; then
    echo "Spack version not officially tested."
    echo " recommended version: ${SPACK_COMMIT_REPO}"
    echo " our version: ${SPACK_COMMIT}"
    if [ ${FORCE} == 0 ]; then
        echo "Ignoring patches..."
        exit 1
    fi
fi

# Apply the patches to spack
echo "Applying patches from ${REPO}..."
cd ${SPACK_ROOT}
source ${REPO}/.cherry-pick
