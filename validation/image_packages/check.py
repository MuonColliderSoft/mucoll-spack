#!/usr/bin/env python3
"""Compare the image's installed package names with a committed baseline."""

import argparse
import json
import os
import subprocess
import sys


def collect_apt_packages(root="/"):
    """Return the installed package names from dpkg's status file."""
    status_path = os.path.join(root, "var/lib/dpkg/status")
    packages = []
    with open(status_path, encoding="utf-8", errors="replace") as status:
        stanza = {}
        for line in status.read().split("\n"):
            if not line.strip():
                if stanza.get("Status") == "install ok installed":
                    packages.append(stanza["Package"])
                stanza = {}
            elif not line.startswith((" ", "\t")) and ":" in line:
                key, _, value = line.partition(":")
                stanza[key] = value.strip()

        if stanza.get("Status") == "install ok installed":
            packages.append(stanza["Package"])

    return sorted(set(packages))


def find_spack_database(root="/"):
    """Find the installed Spack database below the padded store path."""
    store = os.path.join(root, "opt/spack/opt/spack")
    for directory, subdirectories, files in os.walk(store):
        if os.path.basename(directory) == ".spack-db" and "index.json" in files:
            return os.path.join(directory, "index.json")
        subdirectories[:] = [
            name
            for name in subdirectories
            if name in {"__spack_path_placeholder__", ".spack-db"}
        ]
    raise FileNotFoundError("Spack database not found under %s" % store)


def collect_spack_packages(root="/"):
    """Return installed Spack package names and their DAG hashes."""
    with open(find_spack_database(root), encoding="utf-8") as database:
        installs = json.load(database)["database"]["installs"]

    hashes = {}
    for dag_hash, entry in installs.items():
        if not entry.get("installed"):
            continue
        name = entry["spec"]["name"]
        hashes.setdefault(name, []).append(dag_hash.lstrip("/"))

    hashes = {name: sorted(set(values)) for name, values in sorted(hashes.items())}
    return sorted(hashes), hashes


def collect_concretized_spack_packages(spec):
    """Return package names in a concrete, not-yet-installed Spack DAG."""
    result = subprocess.run(
        [
            "spack",
            "find",
            "--show-concretized",
            "--deps",
            "--format",
            "{name}",
            spec,
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return sorted(set(result.stdout.split()))


def compare(expected, observed, package_types=("apt", "spack")):
    """Return readable package additions and removals."""
    changes = []
    for package_type in package_types:
        expected_packages = set(expected.get(package_type, []))
        observed_packages = set(observed[package_type])
        changes.extend(
            "%s: REMOVED %s" % (package_type, package)
            for package in sorted(expected_packages - observed_packages)
        )
        changes.extend(
            "%s: ADDED %s" % (package_type, package)
            for package in sorted(observed_packages - expected_packages)
        )
    return changes


def write_json(path, value):
    with open(path, "w", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-type", choices=("analysis", "sim"), required=True)
    parser.add_argument("--arch", choices=("amd64", "arm64"), required=True)
    parser.add_argument(
        "--concretized-spec",
        help="check this concrete Spack DAG instead of an installed image",
    )
    parser.add_argument("--observed-out")
    args = parser.parse_args()

    if args.concretized_spec:
        if args.observed_out:
            parser.error("--observed-out is only available for installed images")
        inventory = {"spack": collect_concretized_spack_packages(args.concretized_spec)}
        package_types = ("spack",)
    else:
        spack_packages, spack_hashes = collect_spack_packages()
        inventory = {
            "apt": collect_apt_packages(),
            "spack": spack_packages,
            # Informational only: compare() deliberately ignores hash changes.
            "spack_hashes": spack_hashes,
        }
        package_types = ("apt", "spack")
        if args.observed_out:
            write_json(args.observed_out, inventory)

    baseline_path = os.path.join(
        os.path.dirname(__file__),
        "baselines",
        "%s-%s.json" % (args.image_type, args.arch),
    )
    with open(baseline_path, encoding="utf-8") as baseline_file:
        baseline = json.load(baseline_file)

    changes = compare(baseline, inventory, package_types)
    if changes:
        subject = (
            "Concretized Spack packages"
            if args.concretized_spec
            else "Image package inventory"
        )
        print("%s changed:" % subject)
        print("\n".join("  " + change for change in changes))
        if args.concretized_spec:
            print(
                "\nConfirm the change against the finished image before updating %s."
                % baseline_path
            )
        elif args.observed_out:
            print("\nIf this is intentional, replace %s with %s."
                  % (baseline_path, args.observed_out))
        else:
            print("\nIf this is intentional, rerun with --observed-out and replace %s."
                  % baseline_path)
        return 1

    if args.concretized_spec:
        print("Concretized Spack packages match %s (%d packages)."
              % (baseline_path, len(inventory["spack"])))
    else:
        print(
            "Package inventory matches %s (%d apt, %d Spack)."
            % (baseline_path, len(inventory["apt"]), len(inventory["spack"]))
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
