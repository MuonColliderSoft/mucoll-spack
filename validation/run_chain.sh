#!/bin/bash
###############################################################################
# Single-stage runner for the physics-validation production chain.
#
# Runs one stage of the generic gen -> sim -> digi -> reco chain. This chain is
# the same for every particle gun; only the downstream performance analysis and
# plotting (see validation/make_plots.sh) differ per study.
#
# Usage: run_chain.sh <gen|sim|digi|reco>
#
# Each stage is run independently (one GitHub job each) so every stage gets a
# fresh runner time budget and failures localise to a stage. Outputs are
# forwarded between jobs as artifacts:
#   gen  -> gen.edm4hep.root
#   sim  -> sim.edm4hep.root   (needs gen.edm4hep.root)
#   digi -> digi.edm4hep.root  (needs sim.edm4hep.root)
#   reco -> reco.edm4hep.root  (needs digi.edm4hep.root)
#
# The chain is identical for every particle; performance analysis / plotting is
# handled separately (see make_plots.sh), operating on reco.edm4hep.root.
#
# Environment + geometry config come from the benchmarks' setup_config.sh, which
# maps the geometry name to its config package (MAIA_v0 -> MAIAConfig,
# MuColl_* -> MuCollConfig, MuSIC_* -> MuSICConfig), exports the geometry env
# vars (MUCOLL_GEO / MUCOLL_TGEO / MUCOLL_MATMAP / ...) and puts the config and
# common dirs on PYTHONPATH. The geometry-specific digi/reco steering then lives
# under $MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/; gen/sim are geometry-agnostic and
# live at the top of the mucoll-benchmarks checkout pointed to by $BM.
#
# Configuration is taken from the environment (set by the workflow):
#   BM     mucoll-benchmarks checkout dir  (required)
#   GEOM   detector geometry name          (default MAIA_v0)
#   NEV    number of events                (default 100)
#   PPE    particles per event             (default 1)
#   PDG    PDG id of the gun particle      (default -13, mu)
#   PTMIN  min transverse momentum [GeV]   (default 1)
#   PTMAX  max transverse momentum [GeV]   (default 100)
#   THMIN  min polar angle [deg]           (default 10)
#   THMAX  max polar angle [deg]           (default 170)
###############################################################################
set -euo pipefail

STAGE="${1:?usage: run_chain.sh <gen|sim|digi|reco>}"

: "${BM:?BM (mucoll-benchmarks dir) must be set}"
GEOM="${GEOM:-MAIA_v0}"
NEV="${NEV:-100}"
PPE="${PPE:-1}"
PDG="${PDG:--13}"
PTMIN="${PTMIN:-1}"
PTMAX="${PTMAX:-100}"
THMIN="${THMIN:-10}"
THMAX="${THMAX:-170}"

# --- Stack runtime + geometry/config selection -------------------------------
# Source the release stack, then the benchmarks' setup_config.sh, which selects
# the config package from the geometry name and exports the geometry env vars,
# MUCOLL_CONFIG / MUCOLL_CONFIG_NAME and PYTHONPATH. Neither script is written
# for strict mode (setup_mucoll.sh references unset vars; setup_config.sh uses
# `return` on error), so source them with strict mode off, then restore it and
# assert the config was resolved.
set +euo pipefail
# shellcheck disable=SC1091
source /opt/setup_mucoll.sh
# shellcheck disable=SC1091
source "${BM}/setup_config.sh" "${BM}" "${GEOM}"
set -euo pipefail

: "${MUCOLL_CONFIG:?setup_config.sh did not set MUCOLL_CONFIG (unknown geometry '${GEOM}'?)}"
# Geometry-specific digi/reco steering + PandoraSettings live here.
CONFIG_DIR="${MUCOLL_CONFIG}/${MUCOLL_CONFIG_NAME}"

echo "=== stage=${STAGE} BM=${BM} GEOM=${GEOM} CONFIG=${MUCOLL_CONFIG_NAME} NEV=${NEV} PPE=${PPE} PDG=${PDG} pt=[${PTMIN},${PTMAX}] theta=[${THMIN},${THMAX}] ==="
echo "    MUCOLL_GEO=${MUCOLL_GEO:-<unset>}"
echo "    CONFIG_DIR=${CONFIG_DIR}"

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
    # --num-events overrides the steering's default EvtMax so digi processes the
    # same number of events as the simulation. --IOSvc.Input/Output override the
    # steering's hardcoded sim_output/digi_output names to our artifact names.
    k4run --num-events "${NEV}" "${CONFIG_DIR}/digi_steer.py" \
      --DD4hepXMLFile "${MUCOLL_GEO}" \
      --IOSvc.Input sim.edm4hep.root \
      --IOSvc.Output digi.edm4hep.root
    ;;

  reco)
    # PandoraSettings are resolved relative to the working directory by the PFA.
    cp -r "${CONFIG_DIR}/PandoraSettings" ./
    # --num-events overrides the steering's default EvtMax so reco processes the
    # same number of events as the simulation.
    k4run --num-events "${NEV}" "${CONFIG_DIR}/reco_steer.py" \
      --DD4hepXMLFile "${MUCOLL_GEO}" \
      --IOSvc.Input digi.edm4hep.root \
      --IOSvc.Output reco.edm4hep.root
    ;;

  *)
    echo "Unknown stage: ${STAGE} (expected gen|sim|digi|reco)" >&2
    exit 2
    ;;
esac

echo "=== stage=${STAGE} done ==="
ls -lh ./*.edm4hep.root 2>/dev/null || true
