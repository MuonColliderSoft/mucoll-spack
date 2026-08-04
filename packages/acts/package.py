# Overlay of the builtin acts package, needed to run the material mapping
# workflow of k4ActsTracking/doc/material_mapping.md against acts@main.
#
# Two upstream problems are worked around here:
#
# 1. The builtin package's cmake args have drifted from acts@main. It still
#    passes -DACTS_BUILD_EXAMPLES_PYTHON_BINDINGS, but the option that gates
#    `add_subdirectory_if(Python ...)` was renamed to ACTS_BUILD_PYTHON_BINDINGS;
#    the old name now only feeds a set_option_if() clause that turns
#    ACTS_BUILD_EXAMPLES on. The result is a silent no-op ("Ignore subdirectory
#    'Python'" in the build log) and no <prefix>/python at all. The builtin
#    package also never passes ACTS_BUILD_EXAMPLES_ROOT, which defaults to OFF,
#    so ActsExamplesIoRoot -- and with it acts.examples.root.RootMaterialTrackWriter,
#    which every step of the mapping chain writes through -- is not built.
#
# 2. The Examples/Scripts/Python helper scripts (material_recording.py,
#    material_mapping.py, ...) have no CMakeLists.txt and are never installed,
#    so no combination of variants puts them in the prefix.
#
# Drop the cmake_args override once the builtin package catches up with the
# acts@main option names; the install/environment bits are still needed.

from spack_repo.builtin.packages.acts.package import Acts as BuiltinActs

from spack.package import *


class Acts(BuiltinActs):
    __doc__ = BuiltinActs.__doc__

    @property
    def examples_scripts_dir(self):
        return join_path(self.prefix.share.acts, "Examples", "Scripts", "Python")

    def cmake_args(self):
        args = super().cmake_args()
        # Appended last so they win over the stale names above.
        if self.spec.satisfies("+examples"):
            # RootMaterialTrackWriter / RootMaterialTrackReader live here.
            args.append(self.define("ACTS_BUILD_EXAMPLES_ROOT", True))
        if self.spec.satisfies("+python"):
            args.append(self.define("ACTS_BUILD_PYTHON_BINDINGS", True))
        return args

    @run_after("install")
    def install_example_scripts(self):
        if self.spec.satisfies("+examples +python"):
            install_tree(
                join_path(self.stage.source_path, "Examples", "Scripts", "Python"),
                self.examples_scripts_dir,
            )

    def setup_run_environment(self, env):
        super().setup_run_environment(env)
        if self.spec.satisfies("+python"):
            # ACTS installs its bindings under <prefix>/python/acts, which is
            # not a location spack knows about.
            env.prepend_path("PYTHONPATH", self.prefix.python)
        if self.spec.satisfies("+examples +python"):
            env.set("ACTS_EXAMPLES_SCRIPTS", self.examples_scripts_dir)
