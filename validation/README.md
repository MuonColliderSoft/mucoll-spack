# Physics validation workflows

Muon Collider image validation has two distinct scales:

| Workflow | Purpose | Default sample | Layout |
|---|---|---:|---|
| `physics-fast.yaml` | Fast integration check for a proposed image | 10 pion events | SIM, DIGI, RECO, and metrics in one job |
| `physics-validation-template.yaml` | Release or scheduled performance study | Configurable, normally high statistics | Separate SIM, DIGI, RECO, and plotting/metrics jobs |

The fast workflow pulls the container once, runs the appropriate EDM4hep
studies, and uploads logs, production provenance, the per-study JSON fragments,
and their aggregate `metrics.json`. Its metrics are report-only: the job checks
that the requested event count was processed, but it does not yet compare
physics values with reference tolerances.

The workflow uses immutable particle-gun inputs from the `phys-val-inputs`
release. The studies write sidecars and
`mucoll-benchmarks/analysis/benchmarks/aggregate_metrics.py` combines them with
the stack, container, input, geometry, source, and GitHub run provenance. The
`benchmarks-ref` input can select a branch or commit while changes are being
reviewed.

The split full-validation workflow creates `submission.json` in the SIM job and
carries it with the stage artifacts through DIGI and RECO. Its final plot job
uploads a `metrics-<particle>` artifact containing the aggregate report, the
per-study fragments, and that production record. The fast and full workflows
share `validation/write_provenance.py` so they record the same metadata schema.

The active `physics-validation.yaml` manual workflow launches either mode. The
image-build workflow also calls the fast validation against freshly built images for
same-repository pull requests. Those pull requests, pushes to `main`, and manual
image builds also run the split, high-statistics workflow. Both PR validation
paths reuse the image produced by the same build. Fork pull requests skip
physics execution because they cannot publish an image for a downstream job to
pull.

## When each validation runs

| Event | Validation |
|---|---|
| Pull request from this repository | Fast validation plus full four-particle validation, both using the same newly built image |
| Push to `main` | Full validation: the default event count for each of muon, electron, pion, and photon |
| Manual run of `build.yaml` | Full validation against the newly built image |
| Manual run of `physics-validation.yaml` | The selected `fast` or `full` mode for one particle and event count |
| Pull request from a fork | No physics validation, because its image cannot be published for a downstream job |

No validation is currently triggered by a pull-request label.
