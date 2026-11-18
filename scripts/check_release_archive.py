#!/usr/bin/env python3
"""Decide whether a GitHub release may be deposited on Zenodo.

``assets`` fails unless the release is final and carries the complete validation
output of its own tag build. ``zenodo`` reports whether the version is already
part of the concept DOI, so that a retry cannot deposit it twice.
"""

import argparse
import json
import os
import pathlib
import re
import urllib.parse
import urllib.request

PARTICLES = ("muon", "electron", "pion", "photon")


def asset_errors(asset, expected_bytes, expected_sha256):
    """Compare one release asset with its provenance entry."""
    errors = []
    if asset["size"] != expected_bytes:
        errors.append(
            "{}: {} bytes, expected {}".format(
                asset["name"], asset["size"], expected_bytes
            )
        )
    digest = asset.get("digest")
    if digest and digest != "sha256:{}".format(expected_sha256):
        errors.append("{}: checksum does not match provenance".format(asset["name"]))
    return errors


def particle_errors(particle, tag, assets, provenance_dir):
    """Return every problem with the published files of one particle."""
    name = "provenance_{}.json".format(particle)
    path = provenance_dir / name
    if name not in assets or not path.is_file():
        return ["{}: missing".format(name)]

    record = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    ref = record["submission"].get("github", {}).get("ref")
    if ref != "refs/tags/{}".format(tag):
        errors.append("{}: produced by {}, not {}".format(name, ref, tag))
    version = (record.get("software") or {}).get("mucoll_stack_version")
    if version != tag[1:]:
        errors.append("{}: stack version is {}".format(name, version))

    metrics = record["metrics"]
    if metrics["name"] not in assets:
        errors.append("{}: missing".format(metrics["name"]))
    elif assets[metrics["name"]].get("digest") not in (
        None,
        "sha256:{}".format(metrics["sha256"]),
    ):
        errors.append("{}: checksum does not match provenance".format(metrics["name"]))

    if not record["histograms"]:
        errors.append("{}: lists no histogram files".format(name))
    for histogram in record["histograms"]:
        if histogram["name"] not in assets:
            errors.append("{}: missing".format(histogram["name"]))
            continue
        errors.extend(
            asset_errors(
                assets[histogram["name"]], histogram["bytes"], histogram["sha256"]
            )
        )
    return errors


def check_assets(args):
    release = json.loads(args.release.read_text(encoding="utf-8"))
    if release.get("isDraft") or release.get("isPrerelease"):
        raise SystemExit("{} is not a published final release".format(args.tag))
    assets = {asset["name"]: asset for asset in release.get("assets", [])}
    errors = []
    for particle in PARTICLES:
        errors.extend(particle_errors(particle, args.tag, assets, args.provenance_dir))
    if errors:
        raise SystemExit(
            "{} is not ready to archive:\n  {}".format(args.tag, "\n  ".join(errors))
        )
    print("{} has the complete validation output".format(args.tag))


def archived_versions(concept_doi):
    """Return the versions published under a Zenodo concept DOI."""
    match = re.fullmatch(r"10\.5281/zenodo\.(\d+)", concept_doi)
    if not match:
        raise SystemExit("invalid Zenodo concept DOI")
    query = urllib.parse.urlencode(
        {"q": 'parent.id:"{}"'.format(match.group(1)), "all_versions": "true"}
    )
    url = "https://zenodo.org/api/records?{}&size=25".format(query)
    versions = set()
    while url:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "mucoll-spack-release-check",
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            page = json.load(response)
        for record in page["hits"]["hits"]:
            versions.add(record["metadata"].get("version"))
        url = page.get("links", {}).get("next")
    if not versions:
        raise SystemExit("no Zenodo records found for the concept DOI")
    return versions


def check_zenodo(args):
    archived = args.tag in archived_versions(args.concept_doi)
    print("{} archived on Zenodo: {}".format(args.tag, archived))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("archived={}\n".format(str(archived).lower()))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    assets = commands.add_parser("assets", help="check the release and its assets")
    assets.add_argument("--tag", required=True)
    assets.add_argument("--release", required=True, type=pathlib.Path)
    assets.add_argument("--provenance-dir", required=True, type=pathlib.Path)
    assets.set_defaults(handler=check_assets)

    zenodo = commands.add_parser("zenodo", help="check for an existing deposit")
    zenodo.add_argument("--tag", required=True)
    zenodo.add_argument("--concept-doi", required=True)
    zenodo.set_defaults(handler=check_zenodo)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    args.handler(args)


if __name__ == "__main__":
    main()
