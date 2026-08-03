# Overlay of the builtin acts package.
#
# Upstream ACTS builds the Examples/Scripts/Python helper scripts (material
# recording/mapping, propagation, ...) but never installs them: that directory
# has no CMakeLists.txt, so `+examples` only ever gives you the libraries and
# the python bindings. The material mapping workflow documented in
# k4ActsTracking/doc/material_mapping.md drives everything from those scripts,
# so copy them into the prefix and point PYTHONPATH at the bindings.

from spack_repo.builtin.packages.acts.package import Acts as BuiltinActs

from spack.package import *


class Acts(BuiltinActs):
    __doc__ = BuiltinActs.__doc__

    @property
    def examples_scripts_dir(self):
        return join_path(self.prefix.share.acts, "Examples", "Scripts", "Python")

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
