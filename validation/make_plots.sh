#!/bin/bash
###############################################################################
# Produce the performance plots for one particle from the reconstruction output.
#
# Usage: make_plots.sh <particle-label>
#
# Input : reco.edm4hep.root in the current directory.
# Output: public/<particle>/ with the plots + an index.html.
#
# This is the ONLY per-study step: the gen/sim/digi/reco chain (run_chain.sh) is
# identical for every particle, and the analysis/plotting that differs lives here.
# It can either analyse reco.edm4hep.root directly, or first run an extra k4run
# step to produce histograms and feed them to plot_tracking_perf.py.
#
# NOTE: the tracking-performance plotting is not implemented yet, because the
# Gaudi TrackPerfHistAlg it relies on is not available in the image. For now a
# placeholder page is written so the pipeline stays green.
###############################################################################
set -euo pipefail

PARTICLE="${1:?usage: make_plots.sh <particle-label>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="public/${PARTICLE}"
mkdir -p "${OUT}"

# Source the stack (not written for strict mode).
set +euo pipefail
# shellcheck disable=SC1091
source /opt/setup_mucoll.sh
set -euo pipefail

if [ ! -f reco.edm4hep.root ]; then
  echo "ERROR: reco.edm4hep.root not found in $(pwd)" >&2
  exit 1
fi

# TODO: implement the tracking-performance analysis here, e.g.
#   - run an extra k4run step that produces histograms, then
#       python "${HERE}/plot_tracking_perf.py" reco_histograms.root "${OUT}" --particle "${PARTICLE}"
#   - or analyse reco.edm4hep.root directly with podio/ROOT.
echo "Plotting not implemented yet (TrackPerfHistAlg unavailable); writing placeholder for ${PARTICLE}."
{
  echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
  echo "<title>${PARTICLE} — performance</title></head><body>"
  echo "<h1>${PARTICLE}: performance plots (placeholder)</h1>"
  echo '<p>gen → sim → digi → reco ran successfully and produced'
  echo '<code>reco.edm4hep.root</code>. Plotting is not implemented yet'
  echo '(it needs <code>TrackPerfHistAlg</code>, which is not available in the image).</p>'
  echo '</body></html>'
} > "${OUT}/index.html"
