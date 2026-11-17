#!/usr/bin/env fish

# Purge all buildcache versions belonging to a given package base name.
#
# Usage: purge_pkg_from_cache.fish [--dryRun] <package-base-name>
#   e.g. purge_pkg_from_cache.fish mucoll-stack
#        purge_pkg_from_cache.fish --dryRun k4actstracking-material
#
# Tags in the buildcache look like <base-name>-<version>-<hash>.spack, so a
# version matches when one of its tags starts with "<base-name>-".

set SCRIPT_NAME (status basename)
set ORG "MuonColliderSoft"
set PACKAGE "mucoll-buildcache"

set DRY_RUN 0
set BASE_NAME ""

for arg in $argv
    switch $arg
        case --dryRun --dry-run
            set DRY_RUN 1
        case '-*'
            echo "Unknown option: $arg" >&2
            echo "Usage: $SCRIPT_NAME [--dryRun] <package-base-name>" >&2
            exit 1
        case '*'
            if test -n "$BASE_NAME"
                echo "Only one package base name may be given (got '$BASE_NAME' and '$arg')" >&2
                exit 1
            end
            set BASE_NAME $arg
    end
end

if test -z "$BASE_NAME"
    echo "Usage: $SCRIPT_NAME [--dryRun] <package-base-name>" >&2
    echo "  e.g. $SCRIPT_NAME mucoll-stack" >&2
    exit 1
end

echo "=== Searching $ORG/$PACKAGE for versions of '$BASE_NAME' ==="
if test $DRY_RUN -eq 1
    echo "(dry run: nothing will be deleted)"
end

# --- Pass 1: collect every matching version (delete only afterwards, so that
# --- removing versions does not shift the pagination under our feet) ---
set ids
set descriptions
set page 1
while true
    set versions (gh api \
        -H "Accept: application/vnd.github+json" \
        "/orgs/$ORG/packages/container/$PACKAGE/versions?per_page=100&page=$page")

    set count (echo $versions | jq 'length')
    if test $count -eq 0
        break
    end

    set matches (echo $versions | jq -r \
        --arg name $BASE_NAME \
        '.[] | select(
            any(.metadata.container.tags[]?;
                . == $name or startswith($name + "-"))
        ) | "\(.id)\t\(.metadata.container.tags | join(","))\t\(.updated_at)"' \
        | string split "\n" | string match -v "")

    for match in $matches
        set fields (string split \t -- $match)
        set -a ids $fields[1]
        set -a descriptions "$fields[1] (tags: $fields[2], updated: $fields[3])"
    end

    set page (math $page + 1)
end

if test (count $ids) -eq 0
    echo "No versions found for '$BASE_NAME'."
    exit 0
end

echo "=== Found "(count $ids)" version(s) ==="
for description in $descriptions
    echo "  $description"
end

if test $DRY_RUN -eq 1
    echo "Dry run: skipping deletion of "(count $ids)" version(s)."
    exit 0
end

# --- Pass 2: delete them ---
echo "=== Deleting ==="
set failed 0
for i in (seq (count $ids))
    echo "Deleting version $descriptions[$i]"
    if not gh api --method DELETE \
        "/orgs/$ORG/packages/container/$PACKAGE/versions/$ids[$i]"
        echo "  ! failed to delete $ids[$i]" >&2
        set failed (math $failed + 1)
    end
end

if test $failed -gt 0
    echo "Done, with $failed failure(s)."
    exit 1
end

echo "Done."
