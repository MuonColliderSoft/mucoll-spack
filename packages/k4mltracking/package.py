#!/usr/bin/env python3

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.pkg.k4.key4hep_stack import Key4hepPackage

from spack.package import *


class K4mltracking(CMakePackage, Key4hepPackage):
    """Package for GNN based tracking with Acts in Key4hep for the MuonCollider"""

    homepage = "https://github.com/tmadlener/MLTracking.git"
    git = "https://github.com/tmadlener/MLTracking.git"

    maintainers("tmadlener")

    version("main", branch="main")

    depends_on("cxx")

    depends_on("k4fwcore@1.3:")
    depends_on("edm4hep@0.99:")
    depends_on("k4actstracking")
    depends_on("dd4hep")
    depends_on("acts +gnn")
    depends_on("py-torch")
    depends_on("py-onnxruntime")

    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4mltracking"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4mltracking"].prefix.lib64)
        env.prepend_path("PYTHONPATH", self.spec["k4mltracking"].prefix.python)
