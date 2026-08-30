#!/usr/bin/env spack-python
"""Print the packages a concretized root spec contributes to a finished image.

Runs under `spack python` (it needs Spack's own interpreter and modules):

    spack python concretized_packages.py 'mucoll-stack+sim'

Only the link/run closure is printed: the images run `spack gc` after the
install, so build-only dependencies (autoconf, rust, py-hatchling, ...) never
reach the baselines that check.py compares against.
"""

import sys

import spack.environment


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: spack python %s <spec>" % sys.argv[0])
    spec = sys.argv[1]

    environment = spack.environment.active_environment()
    if environment is None:
        sys.exit("no active Spack environment")

    roots = [
        concrete
        for _, concrete in environment.concretized_specs()
        if concrete.satisfies(spec)
    ]
    if len(roots) != 1:
        sys.exit(
            "%d concretized roots match '%s', expected exactly one"
            % (len(roots), spec)
        )

    names = {
        dependency.name for dependency in roots[0].traverse(deptype=("link", "run"))
    }
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
