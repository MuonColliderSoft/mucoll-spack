from spack.package import *
from spack.pkg.k4.key4hep_stack import Key4hepPackage


class K4actstracking(CMakePackage, Key4hepPackage):
    """Acts tracking components for the key4hep project"""

    homepage = "https://github.com/MuonColliderSoft/k4ActsTracking.git"
    # todo
    # url = "https://github.com/MuonColliderSoft/k4ActsTracking"
    git = "https://github.com/MuonColliderSoft/k4ActsTracking.git"

    maintainers("vvolkl")

    version("main", branch="main")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("acts")
    depends_on("dd4hep")
    depends_on("k4fwcore")

    depends_on("opendatadetector", type="test")

    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4actstracking"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4actstracking"].prefix.lib64)
        env.prepend_path("PYTHONPATH", self.prefix.python)

    def cmake_args(self):
        return []