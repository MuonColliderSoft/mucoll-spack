# Release Notes

Release notes for the [Muon Collider Spack package repository](https://github.com/MuonColliderSoft/mucoll-spack).

Each release corresponds to a git tag and a set of container images published by the CI.
The release version is also recorded in `packages/mucoll-stack/package.py` and the per-package
versions in `environments/mucoll-common/packages.yaml`.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

No changes yet on `main` on top of `v3.1`.

---

## [v3.1] — 2026-08-13

Second release of the **3.x series** (`mucoll-stack@3.1`). It consolidates the layered build to two
images, removes the Marlin/ILCSoft/LCIO reconstruction chain in favour of the native key4hep path,
brings back the GNN tracking pipeline, and pins the stack to tagged key4hep/MuColl releases instead
of tracking `main`.

### Added
- **Event generators in the `sim` image.** New `+gen` variant pulling in `whizard +openloops`,
  `madgraph5amc`, and `pythia8`. The published `sim` layer is now built as `+sim+gen` — both the
  `mucoll-layered` environment and the CI (`amd64`/`arm64`).
- **`k4gaudipandora` in the `+sim` layer**, providing the Gaudi ↔ PandoraPFA interface that replaces
  the dropped `pandorapfa`/`marlin` path. It is required as `@0.3.0 ~ddkaltest`: `~ddkaltest` takes
  the track states already present on the input tracks instead of recomputing them at the
  calorimeter, which avoids the `k4reco +conformal_tracking` dependency (and with it LCIO).
- **ACTS overlay recipe** (`packages/acts`) so the material-mapping workflow of
  `k4ActsTracking/doc/material_mapping.md` actually works against `acts@main`: it passes the renamed
  `ACTS_BUILD_PYTHON_BINDINGS` / `ACTS_BUILD_EXAMPLES_ROOT` cmake options (the builtin package's
  names are silent no-ops on `main`), installs the `Examples/Scripts/Python` helper scripts, and
  exports `PYTHONPATH` / `ACTS_EXAMPLES_SCRIPTS`. ACTS is now required as
  `+dd4hep+json+edm4hep+examples+geant4+hepmc3+python cxxstd=20`.
- **GNN tracking pipeline back in the default build.** The stack requires
  `k4actstracking@00-05 +gnn`, which pulls `acts +gnn+onnx+torch` together with `py-torch` and
  `py-onnxruntime`. The pipeline is now selected by a variant on a tagged release rather than by
  a branch pin, and needs no ACORN (GNN4ITk) dependency.
- **Concretization CI now exercises the real image bootstrap.** `concretize-template.yaml` builds
  `Docker/Dockerfile.base --target concretize` instead of running inside the key4hep externals
  image, so it uses exactly the same pinned spack / spack-packages commits, key4hep-spack and local
  `.cherry-pick`, LLVM-20/rust externals and buildcache mirror that the published images use.
  Nothing is installed, so the check stays cheap while failing on exactly the concretization
  problems a real build would hit; the concretized spec is uploaded as `spec-<target>.log`.
- **Geant4 `examples` variant via cherry-pick.** `.cherry-pick` now cherry-picks the key4hep-spack
  commit that adds the `examples` variant to `geant4`, so the build can turn the examples off
  without vendoring a full local `geant4` recipe.

### Changed
- **Simplified the layered build from three images to two.** Collapsed the
  `analysis ⊂ sim ⊂ ml` chain into `analysis ⊂ sim`: the machine-learning tools (`+ml`) are now
  folded into the base analysis layer instead of shipping as a separate `mucoll-ml` image, and both
  the `analysis` and `sim` roots carry `+ml`. Removed the dedicated `+analysis` variant — the
  edm4hep/podio analysis stack is now the always-installed base of every layer. Moved `hepmc3`
  into the `+sim` layer. The roots are now `mucoll-stack~devtools+pytools+ml~sim` and
  `mucoll-stack~devtools+pytools+ml+sim+gen`.
- **Pinned the stack to tagged releases** rather than tracking upstream `main`: `edm4hep@1.1`,
  `k4fwcore@1.7`, `k4geo@0.26`, `k4gen@0.1pre16`, `k4gaudipandora@0.3.0`, `k4actstracking@00-05`,
  `k4reco@0.3` (new version added to the recipe and made preferred). `k4simgeant4` still tracks
  `@main`.
- **Physics-validation plotting moved to the `mucoll-benchmarks` python studies.** The plot step now
  runs `analysis/python/edm4hep/study_{tracks,seeds,hits}.py` (and `study_photons.py` for photons)
  instead of the retired `TrackingPlots` submodule (`RunAnalysis.C` -> `PlotAll.C`), which no longer
  exists upstream. The studies fuse ntuple writing and plotting into a single RDataFrame event loop,
  so there is no intermediate ntuple stage. `validation/RunAnalysis.conf` is replaced by
  `validation/plot_settings.sh`, whose settings can all be overridden from the environment.
- Pinned `numpy` (`@:2.2`, the numba-compatible ceiling), `py-sympy@1.13.3`, `eigen@3.4`,
  `py-fsspec +http` and `valgrind ~boost` in `packages.yaml` so the `analysis` and `sim` roots stay
  shareable under `unify: when_possible` — each of these otherwise forks the expensive
  `py-torch`/`onnxruntime` subtree across the two roots.
- Disabled Geant4 examples (`geant4 ~examples`) to trim the build, and dropped `+lcio` from the
  `dd4hep` and Whizard specs (now `whizard +openloops`).
- `k4geo` is still required as `~beampipe_stl` — it skips the network download of the FCC-ee MDI
  beampipe CAD, which MuColl does not use and which intermittently breaks the build. The variant
  itself now comes from upstream, so it no longer needs a local overlay to exist.

### Removed
- **Removed Marlin, ILCSoft, and LCIO from the stack.** Dropped the entire Marlin/ILCSoft
  reconstruction chain (`marlin`, `marlinreco`, `marlintrk`, `marlinutil`, `marlindd4hep`,
  `marlinfastjet`, `marlinkinfit*`, `pandorapfa`/`pandoraanalysis`, `gear`, `kaltest`/`ddkaltest`,
  `kitrack*`, `clicperformance`, `fcalclusterer`, `generalbrokenlines`, `aidatt`, `raida`, `sio`,
  `ced`/`cedviewer`, `garlic`, `lcfiplus`/`lcfivertex`, …) together with `k4marlinwrapper` and the
  `lcio` pin from the stack's direct dependencies, along with the now-unused `muoncvxddigitiser` and
  `mybibutils` recipes. Reconstruction is now driven entirely by the native key4hep/`k4reco` path
  (`k4geo` still pulls upstream `lcio`. The changes needed to avoid this will land later).
- Dropped the version requirements on `k4simdelphes` and `k4edm4hep2lcioconv`.
- **Dropped the local `k4geo`, `k4actstracking` and `k4gaudipandora` recipes** in favour of the
  upstream Spack packages, which now carry everything the overlays were adding (the `beampipe_stl`,
  `gnn` and `ddkaltest` variants). `packages/` is down to `acorn`, `acts`, `k4reco`, `mucoll-stack`,
  `pelican` and the python/ML helpers.
- Removed the `mucoll-release-debug` environment (and its entry from the concretization matrix).

---

## [v3.0] — 2026-06-20

First release of the **3.x series** (`mucoll-stack@3.0`) — a major restructuring of how the stack
is built and distributed.

### Added
- **Layered build and image chain.** The stack is organised as three nested root specs
  (`analysis ⊂ sim ⊂ ml`) concretized together under `unify: when_possible`, so every shared
  dependency resolves to a single hash and is installed only once. The CI publishes a chain of
  images that build on top of one another:
  - `mucoll-analysis-<os>` — minimal, edm4hep+podio analysis stack
    (`mucoll-stack+devtools+pytools+analysis`).
  - `mucoll-sim-<os>` — adds the simulation and reconstruction tools (`+sim`, pulls in
    `dd4hep+ddg4`, `geant4+data`).
  - `mucoll-ml-<os>` — adds the machine-learning stack (`+ml`).
- **Machine-learning layer.** New `+ml` variant pulling in a PyTorch-based stack: `py-torch`
  (+ `torch-scatter`, `py-torch-cluster`, `py-torch-sparse`, `py-torch-spline-conv`),
  `py-class-resolver`, `py-trackml`, and related tooling, with a GNN-enabled
  `k4actstracking@gnn` branch.
- **Full ACTS recipe** and ACORN integration for ML-based tracking.
- New/updated `mucoll`-namespaced packages: `acorn`, `k4reco`, `k4geo`, `muoncvxddigitiser`,
  `marlinmuonid`, `mybibutils`, `pelican`, `py-atlasify`.
- **Physics validation** workflow (`validation/`) tracking `mucoll-benchmarks` main, with
  geometry-driven configuration selection, gated on a multi-arch simulation manifest.

### Changed
- **Analysis layer built from a plain Ubuntu base** rather than the full key4hep image, trimming
  the footprint of the analysis-only image.
- Docker build consolidated to a small set of Dockerfiles (`Dockerfile.base`, `Dockerfile.layer`).
- Migrated to `cxxstd=20` and `build_type=RelWithDebInfo` as the default variants.
- Switched several components to upstream `main`/`master` branches: `k4fwcore`, `k4gen`,
  `k4marlinwrapper` handling, ACTS.
- Builds target both `x86_64` and `aarch64` (multi-arch images).
- Re-added `k4marlinwrapper` and `k4simgeant4` to the `+sim` layer (the latter provides the
  `GeoSvc` that the MAIA/MuColl reconstruction workflow loads at runtime).
- Added `ccache` as a build dependency.

### Removed
- Dropped `k4simdelphes`, the separate `lcgeo` package (replaced by `k4geo`), and `pytools`
  cherry-picks no longer needed.

### Fixed
- ML stack concretization on `aarch64`: pin `llvm@20` with stable `numba`/`llvmlite`, install
  `libzstd-dev`/`zlib1g-dev` so `py-llvmlite` links against the system LLVM, and work around
  LLVM OOM-kills by limiting build jobs.
- ACTS `fillGrid` `atPosition`→`at` patch (later resolved upstream).
- CI hardening: check out the PR head SHA for PR builds, avoid leaking GitHub tokens into final
  images, fix repository-name casing.

---

## [v2.11] — 2025-11-20

### Added
- `mybibutils` and `marlinmuonid` packages.
- Auto-setup of the stack environment on container start.

### Changed
- Updated `marlintrkprocessors` (multiple bug-fix bumps) and bumped to version 2.18.2.
- Track `k4fwcore@main`.
- Adjusted package types across recipes.

### Fixed
- ROOT C++ modules (`cxxmodules`) configuration.

---

## [v2.10.1] — 2025-10-27

### Fixed
- ROOT `cxxmodules` build issue.

## [v2.10] — 2025-10-13

### Added
- Initial machine-learning build step in the CI (later matured in the 3.x series).
- Target-architecture selection for multi-arch builds.

### Changed
- **Images built on top of the key4hep Docker image** instead of from scratch.
- Cleaned up the stack installation scripts and concretization CI.
- Picked up latest `actstracking` and `marlintrkprocessors`.

### Removed
- Dropped the standalone `lcgeo` package and `openloops`/`pytools` cherry-picks.

### Fixed
- Temporary workaround for the ONNX runtime.
- Hardened the image workflow against leaking GitHub tokens.

---

## [v2.9.8] — 2025-09-06

### Changed
- Build on top of the key4hep Docker image; specify target architectures.
- Picked up latest `actstracking` and `marlintrkprocessors`.

### Fixed
- Checksum fixes; repository-name casing fix; ONNX runtime workaround.

## [v2.9.7] — 2025-06-03

### Changed
- Pick up tagged base image from key4hep-dev-externals.

## [v2.9.6] — 2025-05-28

### Fixed
- Docker build and registry-credentials handling.

## [v2.9.5] — 2025-04-29

### Changed
- Use upstream LCIO; bump `dd4hep`, `cvxddigitiser`, `lcgeo`, and `k4geo` tags.
- Enable Pandora monitoring for debugging.

---

## [v2.9] — 2024-07-16

### Added
- Development instructions in the README.
- Spack environment view generation.

### Changed
- New versions of the ACTS processor and MarlinTrk processors.
- Latest ACTS and MarlinTrk processors in the release.

### Fixed
- `lcgeo` path definition; `dd4hep` `LD_LIBRARY_PATH` setup; ROOT and `lcgeo` library
  configuration in the run environment.

### Removed
- `xrootd`; `man-db` from `mucoll-stack`.

---

## [v2.8] — 2023-06-22

First tagged release of the 2.x series — Spack recipes for the Muon Collider software stack
(namespace `mucoll`) built on top of the key4hep stack.

---

[Unreleased]: https://github.com/MuonColliderSoft/mucoll-spack/compare/v3.1...main
[v3.1]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v3.1
[v3.0]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v3.0
[v2.11]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.11
[v2.10.1]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.10.1
[v2.10]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.10
[v2.9.8]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.9.8
[v2.9.7]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.9.7
[v2.9.6]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.9.6
[v2.9.5]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.9.5
[v2.9]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.9
[v2.8]: https://github.com/MuonColliderSoft/mucoll-spack/releases/tag/v2.8
