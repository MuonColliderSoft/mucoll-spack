#!/usr/bin/env python3
"""Write reproducible production metadata for a physics-validation chain."""

import argparse
import datetime
import hashlib
import json
import os
import pathlib


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def github_metadata(environment=None):
    environment = os.environ if environment is None else environment
    mapping = {
        "repository": "GITHUB_REPOSITORY",
        "workflow": "GITHUB_WORKFLOW",
        "job": "GITHUB_JOB",
        "event": "GITHUB_EVENT_NAME",
        "run_id": "GITHUB_RUN_ID",
        "run_attempt": "GITHUB_RUN_ATTEMPT",
        "sha": "GITHUB_SHA",
        "ref": "GITHUB_REF",
    }
    return {
        key: environment[source]
        for key, source in mapping.items()
        if environment.get(source)
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--input-source", required=True)
    parser.add_argument("--events", required=True, type=int)
    parser.add_argument("--particle", required=True)
    parser.add_argument("--pdg", required=True, type=int)
    parser.add_argument("--geometry", required=True)
    parser.add_argument("--image-reference", required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--image-platform", required=True)
    parser.add_argument("--benchmarks-revision", required=True)
    parser.add_argument("--spack-revision", required=True)
    parser.add_argument("--output", default="submission.json", type=pathlib.Path)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not args.input.is_file():
        raise SystemExit("input file not found: {}".format(args.input))
    if args.events < 0:
        raise SystemExit("--events must be non-negative")
    metadata = {
        "schema_version": 1,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input": {
            "path": args.input.name,
            "source": args.input_source,
            "bytes": args.input.stat().st_size,
            "sha256": sha256(args.input),
        },
        "events": args.events,
        "particle": args.particle,
        "pdg": args.pdg,
        "geometry": args.geometry,
        "container": {
            "reference": args.image_reference,
            "image_id": args.image_id,
            "platform": args.image_platform,
        },
        "revisions": {
            "mucoll_benchmarks": args.benchmarks_revision,
            "mucoll_spack": args.spack_revision,
        },
        "github": github_metadata(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(metadata, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
