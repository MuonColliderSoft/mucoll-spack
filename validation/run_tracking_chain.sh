#!/bin/bash
###############################################################################
# Single-stage runner for the physics-validation tracking chain.
#
# Usage: run_tracking_chain.sh <gen|sim|digi|reco>
#
# Each stage is run independently (one GitHub job each) so every stage gets a
# fresh runner time budget and failures localise to a stage. Outputs are
# forwarded between jobs as artifacts:
#   gen  -> gen.edm4hep.root
#   sim  -> sim.edm4hep.root   (needs gen.edm4hep.root)
#   digi -> digi.edm4hep.root  (needs sim.edm4hep.root)
#   reco -> reco.edm4hep.root + reco_histograms.root  (needs digi.edm4hep.root)
#
# This script also sets up the environment itself, deliberately NOT relying on
# the benchmarks' k4MuCPlayground/setup_digireco.sh. That script only (a) puts
# the benchmarks dirs on PYTHONPATH and (b) exports the geometry env vars, but it
# hardcodes a `linux-x86_64` install glob (breaks on other arches) and is not
# written for strict mode. We replicate both jobs here, arch-independently.
#
# The steering files live in the mucoll-benchmarks checkout pointed to by $BM.
#
# Configuration is taken from the environment (set by the workflow):
#   BM     mucoll-benchmarks checkout dir  (required)
#   GEOM   detector geometry name          (default MAIA_v0)
#   NEV    number of events                (default 100)
#   PPE    particles per event             (default 1)
#   PDG    PDG id of the gun particle      (default -13, mu+)
#   PTMIN  min transverse momentum [GeV]   (default 1)
#   PTMAX  max transverse momentum [GeV]   (default 100)
#   THMIN  min polar angle [deg]           (default 10)
#   THMAX  max polar angle [deg]           (default 170)
#   DO_TRACK_PERF  run TrackPerfHistAlg in reco (0/1, default 0)
#
# NOTE: DO_TRACK_PERF is off by default because the Gaudi TrackPerfHistAlg that
# reco_steer.py --doTrackPerf relies on is not yet available in the image. Set
# DO_TRACK_PERF=1 once that algorithm ships to produce reco_histograms.root.
###############################################################################
set -euo pipefail

STAGE="${1:?usage: run_tracking_chain.sh <gen|sim|digi|reco>}"

: "${BM:?BM (mucoll-benchmarks dir) must be set}"
GEOM="${GEOM:-MAIA_v0}"
NEV="${NEV:-100}"
PPE="${PPE:-1}"
PDG="${PDG:--13}"
PTMIN="${PTMIN:-1}"
PTMAX="${PTMAX:-100}"
THMIN="${THMIN:-10}"
THMAX="${THMAX:-170}"
DO_TRACK_PERF="${DO_TRACK_PERF:-0}"

# --- Stack runtime -----------------------------------------------------------
# setup_mucoll.sh references unset variables (e.g. ACLOCAL_PATH) and is not
# written for strict mode; source it with strict mode off, then restore it.
set +euo pipefail
# shellcheck disable=SC1091
source /opt/setup_mucoll.sh
set -euo pipefail

# --- PYTHONPATH for the benchmarks steering modules --------------------------
# (reco_steer.py does `from reco_components...`, `from muc_mt...`, etc.)
export PYTHONPATH="${BM}/digitization:${BM}/reconstruction:${BM}/common:${PYTHONPATH:-}"

# --- Geometry / tracking files ----------------------------------------------
# Resolved by globbing the spack install tree (arch-independent: linux-*).
resolve_one() { ls -d $1 2>/dev/null | head -n 1; }
K4GEO_SHARE=$(resolve_one "/opt/spack/opt/spack/*/*/*/*/linux-*/k4geo-*/share/k4geo")
K4ATS_DATA=$(resolve_one "/opt/spack/opt/spack/*/*/*/*/linux-*/k4actstracking-*/share/k4ActsTracking/data")

export MUCOLL_GEOM_NAME="${GEOM}"
export MUCOLL_GEO=$(resolve_one "${K4GEO_SHARE}/MuColl/*/compact/${GEOM}/${GEOM}.xml")
# MAIA ships a per-geometry material map; others use a generic one.
if [ -f "${K4ATS_DATA}/${GEOM}_material.json" ]; then
  export MUCOLL_MATMAP="${K4ATS_DATA}/${GEOM}_material.json"
else
  export MUCOLL_MATMAP="${K4ATS_DATA}/material-maps.json"
fi
export MUCOLL_TGEO="${K4ATS_DATA}/${GEOM}.root"
export MUCOLL_TGEO_DESC="${K4ATS_DATA}/${GEOM}.json"

echo "=== stage=${STAGE} BM=${BM} GEOM=${GEOM} NEV=${NEV} PPE=${PPE} PDG=${PDG} pt=[${PTMIN},${PTMAX}] theta=[${THMIN},${THMAX}] ==="
echo "    MUCOLL_GEO=${MUCOLL_GEO:-<unset>}"
echo "    MUCOLL_MATMAP=${MUCOLL_MATMAP:-<unset>}"
echo "    MUCOLL_TGEO=${MUCOLL_TGEO:-<unset>}"
echo "    MUCOLL_TGEO_DESC=${MUCOLL_TGEO_DESC:-<unset>}"

case "${STAGE}" in
  gen)
    python "${BM}/generation/pgun/pgun_edm4hep.py" \
      -e "${NEV}" -p "${PPE}" --pdg "${PDG}" \
      --pt "${PTMIN}" "${PTMAX}" --theta "${THMIN}" "${THMAX}" \
      -- gen.edm4hep.root
    ;;

  sim)
    ddsim --steeringFile "${BM}/simulation/steer_baseline.py" \
      --inputFiles gen.edm4hep.root \
      --outputFile sim.edm4hep.root \
      --numberOfEvents "${NEV}"
    ;;

  digi)
    k4run "${BM}/digitization/digi_steer.py" \
      --IOSvc.Input sim.edm4hep.root \
      --IOSvc.Output digi.edm4hep.root
    ;;

  reco)
    # PandoraSettings are resolved relative to the working directory by reco_steer.py
    cp -r "${BM}/reconstruction/PandoraSettings" ./
    reco_args=(--IOSvc.Input digi.edm4hep.root --IOSvc.Output reco.edm4hep.root)
    case "${DO_TRACK_PERF}" in
      1|true|TRUE|yes|on)
        # Produces reco_histograms.root (requires TrackPerfHistAlg in the image)
        reco_args+=(--doTrackPerf)
        ;;
      *)
        echo "DO_TRACK_PERF=${DO_TRACK_PERF}: skipping --doTrackPerf (TrackPerfHistAlg not available)"
        ;;
    esac
    k4run "${BM}/reconstruction/reco_steer.py" "${reco_args[@]}"
    ;;

  *)
    echo "Unknown stage: ${STAGE} (expected gen|sim|digi|reco)" >&2
    exit 2
    ;;
esac

echo "=== stage=${STAGE} done ==="
ls -lh ./*.edm4hep.root ./reco_histograms.root 2>/dev/null || true
