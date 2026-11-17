#!/usr/bin/env bash

# Purge all buildcache versions belonging to a given package base name.
# Bash port of purge_pkg_from_cache.fish.
#
# Usage: purge_pkg_from_cache.sh [--dryRun] <package-base-name>
#   e.g. purge_pkg_from_cache.sh mucoll-stack
#        purge_pkg_from_cache.sh --dryRun k4actstracking-material
#
# Tags in the buildcache look like <base-name>-<version>-<hash>.spack, so a
# version matches when one of its tags starts with "<base-name>-".

set -uo pipefail

SCRIPT_NAME=$(basename "$0")
ORG="MuonColliderSoft"
PACKAGE="mucoll-buildcache"

DRY_RUN=0
BASE_NAME=""

usage() {
    echo "Usage: $SCRIPT_NAME [--dryRun] <package-base-name>" >&2
}

for arg in "$@"; do
    case "$arg" in
        --dryRun | --dry-run)
            DRY_RUN=1
            ;;
        -*)
            echo "Unknown option: $arg" >&2
            usage
            exit 1
            ;;
        *)
            if [[ -n "$BASE_NAME" ]]; then
                echo "Only one package base name may be given (got '$BASE_NAME' and '$arg')" >&2
                exit 1
            fi
            BASE_NAME=$arg
            ;;
    esac
done

if [[ -z "$BASE_NAME" ]]; then
    usage
    echo "  e.g. $SCRIPT_NAME mucoll-stack" >&2
    exit 1
fi

echo "=== Searching $ORG/$PACKAGE for versions of '$BASE_NAME' ==="
if [[ $DRY_RUN -eq 1 ]]; then
    echo "(dry run: nothing will be deleted)"
fi

# --- Pass 1: collect every matching version (delete only afterwards, so that
# --- removing versions does not shift the pagination under our feet) ---
ids=()
descriptions=()
page=1
while true; do
    if ! versions=$(gh api \
        -H "Accept: application/vnd.github+json" \
        "/orgs/$ORG/packages/container/$PACKAGE/versions?per_page=100&page=$page"); then
        echo "Failed to list versions (page $page)" >&2
        exit 1
    fi

    count=$(jq 'length' <<<"$versions")
    if [[ $count -eq 0 ]]; then
        break
    fi

    while IFS=$'\t' read -r id tags updated; do
        [[ -z "$id" ]] && continue
        ids+=("$id")
        descriptions+=("$id (tags: $tags, updated: $updated)")
    done < <(jq -r --arg name "$BASE_NAME" \
        '.[] | select(
            any(.metadata.container.tags[]?;
                . == $name or startswith($name + "-"))
        ) | "\(.id)\t\(.metadata.container.tags | join(","))\t\(.updated_at)"' \
        <<<"$versions")

    page=$((page + 1))
done

if [[ ${#ids[@]} -eq 0 ]]; then
    echo "No versions found for '$BASE_NAME'."
    exit 0
fi

echo "=== Found ${#ids[@]} version(s) ==="
for description in "${descriptions[@]}"; do
    echo "  $description"
done

if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run: skipping deletion of ${#ids[@]} version(s)."
    exit 0
fi

# --- Pass 2: delete them ---
echo "=== Deleting ==="
failed=0
for i in "${!ids[@]}"; do
    echo "Deleting version ${descriptions[$i]}"
    if ! gh api --method DELETE \
        "/orgs/$ORG/packages/container/$PACKAGE/versions/${ids[$i]}"; then
        echo "  ! failed to delete ${ids[$i]}" >&2
        failed=$((failed + 1))
    fi
done

if [[ $failed -gt 0 ]]; then
    echo "Done, with $failed failure(s)."
    exit 1
fi

echo "Done."
