#!/usr/bin/env python3
"""Render every histogram in a TrackPerf output ROOT file to PNG.

The reconstruction stage (reco_steer.py --doTrackPerf) writes the
TrackPerfHistAlg / TrackTruthAlg histograms (efficiency, pT & impact-parameter
resolution, hits-on-track, track multiplicity, truth distributions, ...) to a
ROOT file via THistSvc. This script is intentionally generic: it walks the file,
draws every TH1/TH2/TProfile it finds, and emits a small index.html so the
result browses as a gallery on GitHub Pages. No histogram names are hard-coded,
so it keeps working as the upstream TrackPerf package evolves.

Usage:
    plot_tracking_perf.py INPUT.root OUTPUT_DIR [--particle NAME]
"""
import argparse
import os
import sys

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(111110)


def iter_histograms(directory, prefix=""):
    """Recursively yield (path, object) for every histogram/profile in a TDirectory."""
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        path = f"{prefix}/{key.GetName()}" if prefix else key.GetName()
        if isinstance(obj, ROOT.TDirectory):
            yield from iter_histograms(obj, path)
        elif isinstance(obj, (ROOT.TH1, ROOT.TProfile)):
            # TH2/TH3 are subclasses of TH1, handled below by dimension
            yield path, obj


def safe_name(path):
    """Turn a histogram path into a filesystem-safe PNG stem."""
    return path.replace("/", "__").replace(" ", "_")


def draw(obj, out_png):
    canvas = ROOT.TCanvas("c", "c", 800, 600)
    if isinstance(obj, ROOT.TH2):
        obj.Draw("COLZ")
    elif isinstance(obj, ROOT.TProfile):
        obj.Draw("E")
    else:
        obj.Draw("HIST E")
    canvas.SetGrid()
    canvas.SaveAs(out_png)
    canvas.Close()


def write_index(out_dir, particle, pngs):
    title = f"Tracking performance — {particle}" if particle else "Tracking performance"
    rows = "\n".join(
        f'  <figure><img src="{png}" alt="{name}" loading="lazy">'
        f"<figcaption>{name}</figcaption></figure>"
        for name, png in pngs
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 1.5rem; background: #fafafa; }}
  h1 {{ font-size: 1.4rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 1rem; }}
  figure {{ margin: 0; background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: .5rem; }}
  img {{ width: 100%; height: auto; }}
  figcaption {{ font-size: .8rem; color: #444; word-break: break-all; margin-top: .25rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p>{len(pngs)} histograms.</p>
<div class="grid">
{rows}
</div>
</body>
</html>
"""
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="Input ROOT file (reco_histograms.root)")
    ap.add_argument("output_dir", help="Directory to write PNGs + index.html into")
    ap.add_argument("--particle", default="", help="Particle label for the page title")
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    f = ROOT.TFile.Open(args.input)
    if not f or f.IsZombie():
        print(f"ERROR: could not open {args.input}", file=sys.stderr)
        return 1

    pngs = []
    for path, obj in iter_histograms(f):
        if obj.GetEntries() == 0:
            print(f"  skipping empty histogram: {path}")
            continue
        stem = safe_name(path) + ".png"
        draw(obj, os.path.join(args.output_dir, stem))
        pngs.append((path, stem))
        print(f"  wrote {stem}")

    f.Close()

    if not pngs:
        print("WARNING: no non-empty histograms found", file=sys.stderr)

    pngs.sort()
    write_index(args.output_dir, args.particle, pngs)
    print(f"=== {len(pngs)} plots written to {args.output_dir} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
