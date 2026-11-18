#!/usr/bin/env python3
"""Stage validation histograms for publication with their provenance.

Each histogram file is copied with a ``provenance`` TNamed whose title is a JSON
record of how it was produced. A ``provenance_<particle>.json`` file lists the
SHA-256 of every published file alongside the same production record.
"""

import argparse
import hashlib
import json
import pathlib
import shutil

SCHEMA_VERSION = 1
PROVENANCE_KEY = "provenance"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SystemExit("could not read {}: {}".format(path, error))


def check_consistency(submission, submission_hash, metrics, benchmarks_revision):
    """Reject outputs that do not all come from the same production."""
    recorded = submission.get("revisions", {}).get("mucoll_benchmarks")
    if recorded != benchmarks_revision:
        raise SystemExit(
            "mucoll-benchmarks revision mismatch: production used {}, plotting "
            "used {}".format(recorded, benchmarks_revision)
        )
    provenance = metrics.get("provenance", {})
    production = provenance.get("production") or {}
    if production.get("sha256") != submission_hash:
        raise SystemExit("metrics report does not reference this submission record")
    repository = provenance.get("benchmark_repository") or {}
    revision = repository.get("revision")
    if revision is not None and revision != benchmarks_revision:
        raise SystemExit(
            "metrics report used mucoll-benchmarks {}, expected {}".format(
                revision, benchmarks_revision
            )
        )


def stamp(path, record):
    """Add the provenance record to a ROOT file and verify it reads back."""
    import ROOT

    payload = json.dumps(record, allow_nan=False, sort_keys=True)
    output = ROOT.TFile.Open(str(path), "UPDATE")
    if not output or output.IsZombie():
        raise SystemExit("could not open {}".format(path))
    if output.GetListOfKeys().FindObject(PROVENANCE_KEY):
        output.Close()
        raise SystemExit("{} already has a provenance record".format(path))
    output.cd()
    ROOT.TNamed(PROVENANCE_KEY, payload).Write()
    output.Close()

    check = ROOT.TFile.Open(str(path), "READ")
    if not check or check.IsZombie():
        raise SystemExit("could not reopen {}".format(path))
    stored = check.Get(PROVENANCE_KEY)
    title = str(stored.GetTitle()) if stored else None
    check.Close()
    if title != payload:
        raise SystemExit("provenance record did not read back from {}".format(path))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--particle", required=True)
    parser.add_argument("--histograms-dir", required=True, type=pathlib.Path)
    parser.add_argument("--submission", required=True, type=pathlib.Path)
    parser.add_argument("--metrics", required=True, type=pathlib.Path)
    parser.add_argument("--benchmarks-revision", required=True)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    sources = sorted(args.histograms_dir.glob("*/histos_*.root"))
    if not sources:
        raise SystemExit("no histos_*.root files under {}".format(args.histograms_dir))
    names = [source.name for source in sources]
    if len(set(names)) != len(names):
        raise SystemExit("several settings tags produced the same histogram file")

    submission = load_json(args.submission)
    submission_hash = sha256(args.submission)
    metrics = load_json(args.metrics)
    check_consistency(submission, submission_hash, metrics, args.benchmarks_revision)

    production = {
        "schema_version": SCHEMA_VERSION,
        "particle": args.particle,
        "software": metrics.get("software"),
        "submission": submission,
        "submission_sha256": submission_hash,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    histograms = []
    for source in sources:
        study = source.stem[len("histos_") :]
        settings_tag = source.parent.name
        target = args.output_dir / "histos_{}_{}.root".format(study, args.particle)
        shutil.copyfile(source, target)
        stamp(target, dict(production, study=study, settings_tag=settings_tag))
        histograms.append(
            {
                "name": target.name,
                "study": study,
                "settings_tag": settings_tag,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )

    metrics_target = args.output_dir / "metrics_{}.json".format(args.particle)
    shutil.copyfile(args.metrics, metrics_target)
    manifest = dict(
        production,
        histograms=histograms,
        metrics={"name": metrics_target.name, "sha256": sha256(metrics_target)},
    )
    manifest_path = args.output_dir / "provenance_{}.json".format(args.particle)
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
