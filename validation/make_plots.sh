#!/bin/bash
###############################################################################
# Produce the tracking-performance plots for one particle from the reco output.
#
# Usage: make_plots.sh <particle-label>
#
# Reads reco_histograms.root in the current directory and writes PNGs + an
# index.html into public/<particle>/. If reco_histograms.root is absent (e.g.
# --doTrackPerf was disabled because TrackPerfHistAlg is not yet in the image),
# a placeholder page is written instead so the pipeline stays green.
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

if [ -f reco_histograms.root ]; then
  python "${HERE}/plot_tracking_perf.py" \
    reco_histograms.root "${OUT}" --particle "${PARTICLE}"
else
  echo "reco_histograms.root not produced (--doTrackPerf disabled: TrackPerfHistAlg unavailable). Writing placeholder."
  {
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
    echo "<title>${PARTICLE} — tracking performance</title></head><body>"
    echo "<h1>${PARTICLE}: tracking performance (currently disabled)</h1>"
    echo '<p>gen → sim → digi → reco ran successfully, but no plots were produced:'
    echo '<code>reco_histograms.root</code> requires <code>TrackPerfHistAlg</code>,'
    echo 'which is not yet available in the image (<code>--doTrackPerf</code> is off).</p>'
    echo '</body></html>'
  } > "${OUT}/index.html"
fi
