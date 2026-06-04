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
# The steering files live in the mucoll-benchmarks checkout pointed to by $BM.
# Geometry / tracking files come from the environment variables exported by
# k4MuCPlayground/setup_digireco.sh (MUCOLL_GEO, MUCOLL_MATMAP, ...).
#
# Sample configuration is taken from the environment (set by the workflow):
#   NEV    number of events                (default 100)
#   PPE    particles per event             (default 1)
#   PDG    PDG id of the gun particle      (default -13, mu+)
#   PTMIN  min transverse momentum [GeV]   (default 1)
#   PTMAX  max transverse momentum [GeV]   (default 100)
#   THMIN  min polar angle [deg]           (default 10)
#   THMAX  max polar angle [deg]           (default 170)
###############################################################################
set -euo pipefail

STAGE="${1:?usage: run_tracking_chain.sh <gen|sim|digi|reco>}"

: "${BM:?BM (mucoll-benchmarks dir) must be set}"
NEV="${NEV:-100}"
PPE="${PPE:-1}"
PDG="${PDG:--13}"
PTMIN="${PTMIN:-1}"
PTMAX="${PTMAX:-100}"
THMIN="${THMIN:-10}"
THMAX="${THMAX:-170}"

echo "=== stage=${STAGE} BM=${BM} NEV=${NEV} PPE=${PPE} PDG=${PDG} pt=[${PTMIN},${PTMAX}] theta=[${THMIN},${THMAX}] ==="
echo "    MUCOLL_GEO=${MUCOLL_GEO:-<unset>}"

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
    k4run "${BM}/reconstruction/reco_steer.py" \
      --IOSvc.Input digi.edm4hep.root \
      --IOSvc.Output reco.edm4hep.root \
      --doTrackPerf
    ;;

  *)
    echo "Unknown stage: ${STAGE} (expected gen|sim|digi|reco)" >&2
    exit 2
    ;;
esac

echo "=== stage=${STAGE} done ==="
ls -lh ./*.edm4hep.root ./reco_histograms.root 2>/dev/null || true
