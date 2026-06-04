#!/bin/bash
###############################################################################
# Single-stage runner for the physics-validation production chain.
#
# Runs one stage of the generic gen -> sim -> digi -> reco chain. This chain is
# the same for every particle gun; only the downstream performance analysis and
# plotting (e.g. plot_tracking_perf.py) differ per study.
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

# --- Geometry ----------------------------------------------------------------
# Only the DD4hep compact description is needed: k4geo exports its location as
# k4geo_DIR (-> <k4geo prefix>/share/k4geo); fall back to globbing if unset.
# MUCOLL_GEOM_NAME selects the reco tracking path; for MAIA_v0 the CKF builds the
# ACTS geometry from the compact, so the prebuilt material/TGeo files
# (MUCOLL_MATMAP / MUCOLL_TGEO / MUCOLL_TGEO_DESC) are NOT required. Non-MAIA
# geometries would need those re-added.
resolve_one() { ls -d $1 2>/dev/null | head -n 1; }
K4GEO_SHARE="${k4geo_DIR:-$(resolve_one "/opt/spack/opt/spack/*/*/*/*/linux-*/k4geo-*/share/k4geo")}"

export MUCOLL_GEOM_NAME="${GEOM}"
export MUCOLL_GEO=$(resolve_one "${K4GEO_SHARE}/MuColl/*/compact/${GEOM}/${GEOM}.xml")

echo "=== stage=${STAGE} BM=${BM} GEOM=${GEOM} NEV=${NEV} PPE=${PPE} PDG=${PDG} pt=[${PTMIN},${PTMAX}] theta=[${THMIN},${THMAX}] ==="
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
      --IOSvc.Output reco.edm4hep.root
    ;;

  *)
    echo "Unknown stage: ${STAGE} (expected gen|sim|digi|reco)" >&2
    exit 2
    ;;
esac

echo "=== stage=${STAGE} done ==="
ls -lh ./*.edm4hep.root 2>/dev/null || true
