# Overlay of the builtin rust package, fixing the source build on macOS.
#
# On macOS spack sets MACOSX_DEPLOYMENT_TARGET to the host OS version (27.0).
# With any deployment target above 11.0 (rustc's own aarch64-apple-darwin
# default), the stage0 rustc from rust-bootstrap@1.96 rejects the proc-macro
# dylibs it just built while compiling x.py's bootstrap tool, and the build
# stops with "error[E0463]: can't find crate for `clap_derive`". The same cargo
# build succeeds when MACOSX_DEPLOYMENT_TARGET is unset or 11.0. The installed
# rust has the same problem with crates that use proc macros, e.g. py-maturin
# fails with "can't find crate for `zerofrom_derive`".
#
# Package and dependency setup run after spack's platform setup, so pinning the
# deployment target back to 11.0 here overrides the host default for rust and
# for every package that builds with it.
#
# Drop this overlay once rust builds with the default deployment target.

from spack_repo.builtin.packages.rust.package import Rust as BuiltinRust

from spack.package import *


class Rust(BuiltinRust):
    __doc__ = BuiltinRust.__doc__

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        super().setup_build_environment(env)
        if self.spec.satisfies("platform=darwin"):
            env.set("MACOSX_DEPLOYMENT_TARGET", "11.0")

    def setup_dependent_build_environment(
        self, env: EnvironmentModifications, dependent_spec: Spec
    ) -> None:
        super().setup_dependent_build_environment(env, dependent_spec)
        if dependent_spec.satisfies("platform=darwin"):
            env.set("MACOSX_DEPLOYMENT_TARGET", "11.0")
