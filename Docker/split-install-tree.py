#!/usr/bin/env python3
"""Spread newly installed spack prefixes over N staging folders of similar size.

The layered Dockerfiles install a whole spack stack in one RUN step, which
would make one huge image layer. Instead, the build stage runs this script
after the install, and the final stage copies each staging folder with its
own COPY instruction, so the stack is split into N layers of similar size.

Only prefixes that are new in this build are staged: prefixes that already
existed in the parent image (listed in --before) are left alone, so they are
not stored twice. The spack database goes into its own folder (meta), which
the Dockerfile copies last.

The prefixes are moved (not copied) into the staging folders, so the build
stage's install tree is no longer usable after this runs.

Layout of --out after a run:
    chunk00/<absolute prefix path>   ...   chunkNN/<absolute prefix path>
    meta/<install root>/.spack-db
"""

import argparse
import os
import shutil
import sys


def read_list(path):
    if not path:
        return set()
    with open(path, encoding="utf-8") as handle:
        return {line.strip().rstrip("/") for line in handle if line.strip()}


def tree_size(path):
    """Disk usage of a directory tree in bytes, counting hard links once."""
    seen = set()
    total = 0
    for directory, dirs, files in os.walk(path):
        for name in dirs + files:
            st = os.lstat(os.path.join(directory, name))
            if st.st_nlink > 1:
                if (st.st_dev, st.st_ino) in seen:
                    continue
                seen.add((st.st_dev, st.st_ino))
            total += st.st_blocks * 512
    return total


def assign_chunks(sizes, n_chunks):
    """Greedy balancing: biggest prefix first, into the lightest chunk."""
    chunks = [[] for _ in range(n_chunks)]
    loads = [0] * n_chunks
    for path, size in sorted(sizes.items(), key=lambda item: (-item[1], item[0])):
        index = loads.index(min(loads))
        chunks[index].append(path)
        loads[index] += size
    return chunks, loads


def move_into(src, staging_root):
    """Move src to staging_root/src, giving new parent folders src's parents' modes."""
    dest = os.path.join(staging_root, src.lstrip("/"))
    parent = os.path.dirname(dest)
    if not os.path.isdir(parent):
        os.makedirs(parent)
        # COPY applies these folders' metadata to the existing ones in the
        # image (e.g. /opt), so give them the same modes and owners.
        orig = os.path.dirname(src)
        made = parent
        while made != staging_root and orig != "/":
            st = os.stat(orig)
            os.chmod(made, st.st_mode & 0o7777)
            if os.geteuid() == 0:
                os.chown(made, st.st_uid, st.st_gid)
            made, orig = os.path.dirname(made), os.path.dirname(orig)
    shutil.move(src, dest)


def human(size):
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return "%.1f %s" % (size, unit)
        size /= 1024.0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, help="spack install tree root")
    parser.add_argument("--installed", required=True,
                        help="file listing every installed prefix (one per line)")
    parser.add_argument("--before", default=None,
                        help="file listing prefixes that the parent image already has")
    parser.add_argument("--chunks", type=int, required=True,
                        help="number of staging folders (must match the Dockerfile COPY lines)")
    parser.add_argument("--out", required=True, help="staging folder to create")
    args = parser.parse_args()

    root = os.path.normpath(args.root)
    before = read_list(args.before)

    sizes = {}
    for prefix in sorted(read_list(args.installed) - before):
        # Externals (e.g. /usr) live outside the install tree: skip them.
        if not prefix.startswith(root + "/") or not os.path.isdir(prefix):
            continue
        sizes[prefix] = tree_size(prefix)

    os.makedirs(args.out)
    for i in range(args.chunks):
        os.makedirs(os.path.join(args.out, "chunk%02d" % i))
    os.makedirs(os.path.join(args.out, "meta"))

    chunks, loads = assign_chunks(sizes, args.chunks)
    for i, (paths, load) in enumerate(zip(chunks, loads)):
        for path in paths:
            move_into(path, os.path.join(args.out, "chunk%02d" % i))
        names = ", ".join(sorted(os.path.basename(p).rsplit("-", 1)[0] for p in paths))
        print("chunk%02d: %10s  %3d prefixes  %s" % (i, human(load), len(paths), names))

    database = os.path.join(root, ".spack-db")
    if not os.path.isdir(database):
        sys.exit("error: no spack database at %s" % database)
    move_into(database, os.path.join(args.out, "meta"))

    print("total:   %10s  %3d prefixes in %d chunks"
          % (human(sum(loads)), len(sizes), args.chunks))


if __name__ == "__main__":
    main()
