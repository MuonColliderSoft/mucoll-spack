#!/bin/bash
###############################################################################
# Produce the tracking plots for one particle from the reconstruction output.
#
# Usage: make_plots.sh <particle-label>
#
# Input : reco.edm4hep.root in the current directory.
# Output: public/<particle>/ with the ROOT plot files, PNGs, and an index.html.
#
# This is the ONLY per-study step: the gen/sim/digi/reco chain (run_chain.sh) is
# identical for every particle, and the analysis/plotting that differs lives here.
#
# The plotting implementation lives in mucoll-benchmarks:
#   plotting/TrackingPlots/PlottingScripts/RunAnalysis.C
#   plotting/TrackingPlots/PlottingScripts/PlotAll.C
#
# Controls are read from validation/RunAnalysis.conf by default. The wrapper
# writes a run-local config with io.inputFilePrefix and io.outputDir set for the
# current reco artifact and settings-tagged work directory. Override with:
#   PLOT_CONF=/path/to/RunAnalysis.conf
#   PLOT_TAG=<settings-label>
#   PLOT_RUN_DIR=/path/to/ntuple/work/dir
#   PLOT_OUT_DIR=/path/to/public/plots/dir
###############################################################################
set -euo pipefail

PARTICLE="${1:?usage: make_plots.sh <particle-label>}"

: "${BM:?BM (mucoll-benchmarks dir) must be set}"

GEOM="${GEOM:-MAIA_v0}"
NEV="${NEV:-100}"
PPE="${PPE:-1}"
PDG="${PDG:--13}"
PTMIN="${PTMIN:-1}"
PTMAX="${PTMAX:-100}"
THMIN="${THMIN:-10}"
THMAX="${THMAX:-170}"

HERE="$(cd "$(dirname "$0")" && pwd)"
CONF="${PLOT_CONF:-${HERE}/RunAnalysis.conf}"
PLOT_SUFFIX="${PLOT_SUFFIX:-png}"
PLOT_SCRIPTS="${BM}/plotting/TrackingPlots/PlottingScripts"
RECO_PREFIX="$(pwd)/reco.edm4hep"

resolve_dir() {
  (cd "$1" && pwd)
}

conf_value() {
  local key="$1"
  local default="$2"
  local value
  value="$(awk -v key="${key}" '
    BEGIN { FS = ":" }
    $1 ~ "^[[:space:]]*" key "[[:space:]]*$" {
      sub(/^[^:]*:/, "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      print
      found = 1
      exit
    }
    END {
      if (!found) exit 1
    }
  ' "${CONF}")" || value="${default}"
  printf '%s' "${value:-${default}}"
}

sanitize_tag() {
  printf '%s' "$1" | tr -c 'A-Za-z0-9._=-' '_' | sed 's/__*/_/g; s/^_//; s/_$//'
}

settings_tag() {
  local event_eta_min event_eta_max track_pt_min track_chi2_max track_hits_min
  event_eta_min="$(conf_value event.absEtaMin 0.0)"
  event_eta_max="$(conf_value event.absEtaMax max)"
  track_pt_min="$(conf_value track.ptMin 0.0)"
  track_chi2_max="$(conf_value track.chi2Max max)"
  track_hits_min="$(conf_value track.nHitsMin 0)"

  sanitize_tag \
    "geom-${GEOM}_nev-${NEV}_ppe-${PPE}_pdg-${PDG}_pt-${PTMIN}-${PTMAX}_theta-${THMIN}-${THMAX}_evtEta-${event_eta_min}-${event_eta_max}_trkPt-${track_pt_min}_chi2-${track_chi2_max}_hits-${track_hits_min}"
}

write_analysis_config() {
  local template="$1"
  local output="$2"
  local input_prefix="$3"
  local output_dir="$4"

  awk -v input_prefix="${input_prefix}" -v output_dir="${output_dir}" '
    /^[[:space:]]*io[.]inputFilePrefix[[:space:]]*:/ {
      print "io.inputFilePrefix: " input_prefix
      saw_input = 1
      next
    }
    /^[[:space:]]*io[.]outputDir[[:space:]]*:/ {
      print "io.outputDir: " output_dir
      saw_output = 1
      next
    }
    { print }
    END {
      if (!saw_input) print "io.inputFilePrefix: " input_prefix
      if (!saw_output) print "io.outputDir: " output_dir
    }
  ' "${template}" > "${output}"
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
    echo "ERROR: PlotAll.C did not write any .${suffix} files to ${out}" >&2
    exit 1
  fi

  {
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">'
    echo "<title>${particle} tracking plots</title>"
    echo '<style>'
    echo 'body{font-family:system-ui,sans-serif;margin:1.5rem;background:#fafafa;color:#222}'
    echo 'h1{font-size:1.4rem;margin:0 0 1rem}'
    echo '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:1rem}'
    echo 'figure{margin:0;background:#fff;border:1px solid #ddd;border-radius:6px;padding:.5rem}'
    echo 'img{display:block;width:100%;height:auto}'
    echo 'figcaption{font-size:.8rem;color:#444;word-break:break-all;margin-top:.35rem}'
    echo '</style></head><body>'
    echo "<h1>${particle} tracking plots</h1>"
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
  echo "ERROR: RunAnalysis config not found: ${CONF}" >&2
  exit 1
fi

if [ ! -f "${PLOT_SCRIPTS}/RunAnalysis.C" ] || [ ! -f "${PLOT_SCRIPTS}/PlotAll.C" ]; then
  echo "ERROR: plotting scripts not found under ${PLOT_SCRIPTS}" >&2
  exit 1
fi

if ! command -v root >/dev/null 2>&1; then
  echo "ERROR: root command not found after sourcing /opt/setup_mucoll.sh" >&2
  exit 1
fi

RUN_TAG="${PLOT_TAG:-$(settings_tag)}"
RUN_DIR="${PLOT_RUN_DIR:-plot_work/${PARTICLE}/${RUN_TAG}}"
OUT="${PLOT_OUT_DIR:-public/${PARTICLE}/${RUN_TAG}}"
mkdir -p "${RUN_DIR}" "${OUT}"
RUN_DIR="$(resolve_dir "${RUN_DIR}")"
OUT="$(resolve_dir "${OUT}")"
RUN_CONF="${RUN_DIR}/RunAnalysis.conf"

write_analysis_config "${CONF}" "${RUN_CONF}" "${RECO_PREFIX}" "${RUN_DIR}/"

echo "=== plotting ${PARTICLE} ==="
echo "    BM           : ${BM}"
echo "    source config: ${CONF}"
echo "    run config   : ${RUN_CONF}"
echo "    plot scripts : ${PLOT_SCRIPTS}"
echo "    settings tag : ${RUN_TAG}"
echo "    ntuple dir   : ${RUN_DIR}"
echo "    output dir   : ${OUT}"

root -l -q "${PLOT_SCRIPTS}/RunAnalysis.C(\"${RUN_CONF}\")"

for ntuple in tracks_ntuple.root seeds_ntuple.root hits_ntuple.root; do
  if [ ! -f "${RUN_DIR}/${ntuple}" ]; then
    echo "ERROR: RunAnalysis.C did not write ${RUN_DIR}/${ntuple}" >&2
    exit 1
  fi
done

root -l -q "${PLOT_SCRIPTS}/PlotAll.C(\"${RUN_DIR}/\", \"${OUT}/\", \"${PLOT_SUFFIX}\")"

write_index "${OUT}" "${PARTICLE}" "${PLOT_SUFFIX}"

echo "=== plotting ${PARTICLE} done ==="
ls -lh "${OUT}" || true
