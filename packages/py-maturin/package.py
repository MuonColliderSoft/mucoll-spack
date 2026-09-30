# Overlay of the builtin py-maturin package, fixing maturin-based builds on macOS.
#
# See packages/rust: with MACOSX_DEPLOYMENT_TARGET above 11.0, rustc cannot load
# the proc-macro crates it builds ("can't find crate for `zerofrom_derive`").
# The rust overlay pins the deployment target to 11.0 for packages that depend
# on rust directly, but packages that only depend on py-maturin (e.g.
# py-uv-build) still compile Rust code through it and never see rust's
# dependent build environment. Pass the same setting on to them here.
#
# Drop this overlay together with the rust one.

from spack_repo.builtin.packages.py_maturin.package import PyMaturin as BuiltinPyMaturin

from spack.package import *


class PyMaturin(BuiltinPyMaturin):
    __doc__ = BuiltinPyMaturin.__doc__

    def setup_dependent_build_environment(
        self, env: EnvironmentModifications, dependent_spec: Spec
    ) -> None:
        super().setup_dependent_build_environment(env, dependent_spec)
        if dependent_spec.satisfies("platform=darwin"):
            env.set("MACOSX_DEPLOYMENT_TARGET", "11.0")
