#!/bin/bash
###############################################################################
# Produce the performance plots for one particle from the reconstruction output.
#
# Usage: make_plots.sh <particle-label>
#
# Input : reco.edm4hep.root in the current directory.
# Output: public/<particle>/<settings-tag>/ with the PNGs and an index.html,
#         plus the histogram ROOT files under plot_work/<particle>/<tag>/.
#
# This is the ONLY per-study step: the gen/sim/digi/reco chain (run_chain.sh) is
# identical for every particle, and the analysis/plotting lives here.
#
# The analysis is dispatched by particle type; every study is a python script in
# mucoll-benchmarks under analysis/python/edm4hep/:
#   - photon             -> study_photons.py (neutral; no tracks):
#                           efficiency + energy-resolution plots
#   - muon/electron/pion -> the tracking studies listed in PLOT_STUDIES
#                           (default: study_tracks.py, study_seeds.py,
#                           study_hits.py)
#
# These RDataFrame studies replace the legacy TrackingPlots submodule
# (RunAnalysis.C -> PlotAll.C), which no longer exists in mucoll-benchmarks.
# Each study fuses what used to be two steps -- ntuple writing and plotting --
# into a single event loop, so there is no intermediate ntuple stage any more.
#
# Controls are read from validation/plot_settings.sh by default; every setting
# there can also be overridden from the environment. Additional overrides:
#   PLOT_CONF=/path/to/plot_settings.sh
#   PLOT_TAG=<settings-label>
#   PLOT_RUN_DIR=/path/to/histogram/output/dir
#   PLOT_OUT_DIR=/path/to/public/plots/dir
#   PLOT_SUFFIX=png|pdf|...
#   PLOT_LABEL=<provenance label stamped on every plot>
###############################################################################
set -euo pipefail

PARTICLE="${1:?usage: make_plots.sh <particle-label>}"

: "${BM:?BM (mucoll-benchmarks dir) must be set}"

GEOM="${GEOM:-MAIA_v0}"
NEV="${NEV:-100}"
PDG="${PDG:--13}"

HERE="$(cd "$(dirname "$0")" && pwd)"
CONF="${PLOT_CONF:-${HERE}/plot_settings.sh}"
PLOT_SUFFIX="${PLOT_SUFFIX:-png}"
STUDY_DIR="${BM}/analysis/python/edm4hep"

resolve_dir() {
  (cd "$1" && pwd)
}

sanitize_tag() {
  printf '%s' "$1" | tr -c 'A-Za-z0-9._=-' '_' | sed 's/__*/_/g; s/^_//; s/_$//'
}

settings_tag() {
  sanitize_tag \
    "geom-${GEOM}_nev-${NEV}_pdg-${PDG}_evtEta-${EVT_ABS_ETA_MIN}-${EVT_ABS_ETA_MAX}_trkPt-${TRK_PT_MIN}_chi2-${TRK_CHI2_MAX}_hits-${TRK_N_HITS_MIN}"
}

write_index() {
  local out="$1"
  local particle="$2"
  local suffix="$3"
  local plots=()

  shopt -s nullglob
  plots=("${out}"/*."${suffix}")
  shopt -u nullglob

  if [ "${#plots[@]}" -eq 0 ]; then
    echo "ERROR: the studies did not write any .${suffix} files to ${out}" >&2
    exit 1
  fi

  {
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">'
    echo "<title>${particle} performance plots</title>"
    echo '<style>'
    echo 'body{font-family:system-ui,sans-serif;margin:1.5rem;background:#fafafa;color:#222}'
    echo 'h1{font-size:1.4rem;margin:0 0 1rem}'
    echo '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:1rem}'
    echo 'figure{margin:0;background:#fff;border:1px solid #ddd;border-radius:6px;padding:.5rem}'
    echo 'img{display:block;width:100%;height:auto}'
    echo 'figcaption{font-size:.8rem;color:#444;word-break:break-all;margin-top:.35rem}'
    echo '</style></head><body>'
    echo "<h1>${particle} performance plots</h1>"
    echo "<p>${#plots[@]} plots generated from <code>reco.edm4hep.root</code>.</p>"
    echo '<div class="grid">'
    local plot name
    for plot in "${plots[@]}"; do
      name="$(basename "${plot}")"
      printf '<figure><a href="%s"><img src="%s" alt="%s" loading="lazy"></a><figcaption>%s</figcaption></figure>\n' \
        "${name}" "${name}" "${name}" "${name}"
    done
    echo '</div></body></html>'
  } > "${out}/index.html"
}

# Source the stack (not written for strict mode).
set +euo pipefail
# shellcheck disable=SC1091
source /opt/setup_mucoll.sh
set -euo pipefail

if [ ! -f reco.edm4hep.root ]; then
  echo "ERROR: reco.edm4hep.root not found in $(pwd)" >&2
  exit 1
fi

if [ ! -f "${CONF}" ]; then
  echo "ERROR: plot settings not found: ${CONF}" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "${CONF}"

if [ ! -d "${STUDY_DIR}" ]; then
  echo "ERROR: study scripts not found under ${STUDY_DIR}" >&2
  exit 1
fi

RUN_TAG="${PLOT_TAG:-$(settings_tag)}"
RUN_DIR="${PLOT_RUN_DIR:-plot_work/${PARTICLE}/${RUN_TAG}}"
OUT="${PLOT_OUT_DIR:-public/${PARTICLE}/${RUN_TAG}}"
mkdir -p "${RUN_DIR}" "${OUT}"
RUN_DIR="$(resolve_dir "${RUN_DIR}")"
OUT="$(resolve_dir "${OUT}")"

# Provenance stamp drawn on every plot by the studies.
LABEL="${PLOT_LABEL:-${GEOM}, ${PARTICLE}, ${NEV} events}"

echo "=== plotting ${PARTICLE} ==="
echo "    BM           : ${BM}"
echo "    settings     : ${CONF}"
echo "    studies dir  : ${STUDY_DIR}"
echo "    settings tag : ${RUN_TAG}"
echo "    histogram dir: ${RUN_DIR}"
echo "    output dir   : ${OUT}"
echo "    label        : ${LABEL}"

run_study() {
  local name="$1"
  shift
  local script="${STUDY_DIR}/study_${name}.py"

  if [ ! -f "${script}" ]; then
    echo "ERROR: study script not found: ${script}" >&2
    exit 1
  fi

  echo "--- study_${name}.py ---"
  python "${script}" \
    -i reco.edm4hep.root \
    -o "${RUN_DIR}/histos_${name}.root" \
    -d "${OUT}" \
    --label "${LABEL}" \
    --suffix "${PLOT_SUFFIX}" \
    "$@"

  if [ ! -f "${RUN_DIR}/histos_${name}.root" ]; then
    echo "ERROR: study_${name}.py did not write ${RUN_DIR}/histos_${name}.root" >&2
    exit 1
  fi
}

# Event-level selection, shared by the studies that support it.
evt_sel_opts=(
  --evtPtMin "${EVT_PT_MIN}" --evtPtMax "${EVT_PT_MAX}"
  --evtThetaMin "${EVT_THETA_MIN}" --evtThetaMax "${EVT_THETA_MAX}"
  --evtAbsEtaMin "${EVT_ABS_ETA_MIN}" --evtAbsEtaMax "${EVT_ABS_ETA_MAX}"
)

# Track-level selection (study_tracks.py only).
trk_sel_opts=(
  --trkPtMin "${TRK_PT_MIN}" --trkPtMax "${TRK_PT_MAX}"
  --trkThetaMin "${TRK_THETA_MIN}" --trkThetaMax "${TRK_THETA_MAX}"
  --trkAbsEtaMin "${TRK_ABS_ETA_MIN}" --trkAbsEtaMax "${TRK_ABS_ETA_MAX}"
  --trkPhiMin "${TRK_PHI_MIN}" --trkPhiMax "${TRK_PHI_MAX}"
  --trkD0Min "${TRK_D0_MIN}" --trkD0Max "${TRK_D0_MAX}"
  --trkZ0Min "${TRK_Z0_MIN}" --trkZ0Max "${TRK_Z0_MAX}"
  --trkChi2Min "${TRK_CHI2_MIN}" --trkChi2Max "${TRK_CHI2_MAX}"
  --trkNHitsMin "${TRK_N_HITS_MIN}" --trkNHolesMax "${TRK_N_HOLES_MAX}"
)

# -------------------------------------------------------------------------
# Photons are neutral: produce only the photon performance study.
# study_photons.py takes neither the selection options nor --label/--suffix.
# -------------------------------------------------------------------------
if [ "${PARTICLE}" = "photon" ]; then
  PHOTON_SCRIPT="${STUDY_DIR}/study_photons.py"
  if [ ! -f "${PHOTON_SCRIPT}" ]; then
    echo "ERROR: photon study not found: ${PHOTON_SCRIPT}" >&2
    exit 1
  fi
  echo "--- study_photons.py ---"
  python "${PHOTON_SCRIPT}" -i reco.edm4hep.root -o "${RUN_DIR}/histos_photons.root" -d "${OUT}"
  write_index "${OUT}" "${PARTICLE}" "${PLOT_SUFFIX}"
  echo "=== plotting ${PARTICLE} done ==="
  ls -lh "${OUT}" || true
  exit 0
fi

# -------------------------------------------------------------------------
# Charged particles (muon, electron, pion, ...): the tracking studies.
# Each study takes the subset of the controls it understands.
# -------------------------------------------------------------------------
# shellcheck disable=SC2086  # PLOT_STUDIES is a space-separated list
for study in ${PLOT_STUDIES}; do
  case "${study}" in
    tracks)
      run_study tracks \
        --trackColl "${TRACK_COLL}" --trackStore "${TRACK_STORE}" \
        --relColl "${REL_COLL}" --mcColl "${MC_COLL}" \
        --Bfield "${BFIELD}" \
        --ptMin "${PLOT_PT_MIN}" --ptMax "${PLOT_PT_MAX}" \
        --nPtBins "${PLOT_N_PT_BINS}" \
        "${evt_sel_opts[@]}" "${trk_sel_opts[@]}"
      ;;
    seeds)
      run_study seeds \
        --seedColl "${SEED_COLL}" --mcColl "${MC_COLL}" \
        --Bfield "${BFIELD}" \
        "${evt_sel_opts[@]}"
      ;;
    hits)
      run_study hits \
        --mcColl "${MC_COLL}" \
        "${evt_sel_opts[@]}"
      ;;
    notracks)
      # Standalone diagnostic: no event or track selection options.
      run_study notracks \
        --trackColl "${TRACK_COLL}" --trackStore "${TRACK_STORE}" \
        --seedColl "${SEED_COLL}" --mcColl "${MC_COLL}"
      ;;
    *)
      echo "ERROR: unknown study '${study}' in PLOT_STUDIES" >&2
      exit 2
      ;;
  esac
done

write_index "${OUT}" "${PARTICLE}" "${PLOT_SUFFIX}"

echo "=== plotting ${PARTICLE} done ==="
ls -lh "${OUT}" || true
