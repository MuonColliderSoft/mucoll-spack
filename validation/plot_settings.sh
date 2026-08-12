# shellcheck shell=bash
# ============================================================
# plot_settings.sh
#
# Controls for the physics-validation plotting step (make_plots.sh).
#
# This replaces the old RunAnalysis.conf (TEnv format), which configured the
# retired RunAnalysis.C -> PlotAll.C macro chain. The plots are now produced by
# the python studies in mucoll-benchmarks (analysis/python/edm4hep/study_*.py),
# which are configured through command-line options, so the controls live here
# as plain shell variables and make_plots.sh maps them onto those options.
#
# Every variable is assigned with ":=", so anything already set in the
# environment wins. That is how the CI overrides individual cuts:
#   docker exec -e TRK_PT_MIN=1.0 ... make_plots.sh muon
#
# Point make_plots.sh at a different file with PLOT_CONF=/path/to/settings.sh.
# ============================================================

# -------------------------
# Collections
# -------------------------
# SiTracks is a podio *subset* collection: it only carries indices into
# AllTracks, which physically stores the TrackData/TrackStates.
: "${TRACK_COLL:=SiTracks}"
: "${TRACK_STORE:=AllTracks}"
: "${REL_COLL:=SiTrackRelations}"
: "${SEED_COLL:=SeedTracks}"
: "${MC_COLL:=MCParticles}"

# -------------------------
# Detector / binning
# -------------------------
# Solenoid field [T], used for pt = |0.3*B/omega/1000| and for the truth helix.
: "${BFIELD:=5.0}"
# Log-spaced pt binning of the efficiency / fake-rate plots. Defaults follow the
# gun range used by run_chain.sh (PTMIN/PTMAX), so the plots cover the sample.
: "${PLOT_PT_MIN:=${PTMIN:-1}}"
: "${PLOT_PT_MAX:=${PTMAX:-100}}"
: "${PLOT_N_PT_BINS:=12}"

# -------------------------
# Event-level selection
# -------------------------
# Keep the event if at least one accepted primary MC particle passes all cuts.
# Use the theta OR the absEta window for the angular selection, not both.
: "${EVT_PT_MIN:=0.0}"
: "${EVT_PT_MAX:=3.4028235e+38}"
: "${EVT_THETA_MIN:=0.0}"
: "${EVT_THETA_MAX:=3.141592653589793}"
: "${EVT_ABS_ETA_MIN:=0.0}"
: "${EVT_ABS_ETA_MAX:=3.4028235e+38}"

# -------------------------
# Track-level selection
# -------------------------
# A track must pass every cut to enter any histogram (and to count towards the
# efficiency numerator). Use the theta OR the absEta window, not both.
: "${TRK_PT_MIN:=0.5}"
: "${TRK_PT_MAX:=3.4028235e+38}"
: "${TRK_THETA_MIN:=0.0}"
: "${TRK_THETA_MAX:=3.141592653589793}"
: "${TRK_ABS_ETA_MIN:=0.0}"
: "${TRK_ABS_ETA_MAX:=3.4028235e+38}"
: "${TRK_PHI_MIN:=-3.141592653589793}"
: "${TRK_PHI_MAX:=3.141592653589793}"
: "${TRK_D0_MIN:=-3.4028235e+38}"
: "${TRK_D0_MAX:=3.4028235e+38}"
: "${TRK_Z0_MIN:=-3.4028235e+38}"
: "${TRK_Z0_MAX:=3.4028235e+38}"
: "${TRK_CHI2_MIN:=0.0}"
: "${TRK_CHI2_MAX:=3.0}"
: "${TRK_N_HITS_MIN:=4}"
: "${TRK_N_HOLES_MAX:=2147483647}"

# -------------------------
# Studies to run for charged particles
# -------------------------
# Space-separated list; each name maps to analysis/python/edm4hep/study_<name>.py.
# "tracks seeds hits" reproduces what the retired RunAnalysis.C -> PlotAll.C
# chain covered. "notracks" is a standalone diagnostic for events that ended up
# with an empty track collection -- add it when debugging a drop in efficiency.
: "${PLOT_STUDIES:=tracks seeds hits}"
