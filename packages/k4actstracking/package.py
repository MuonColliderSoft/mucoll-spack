from spack.package import *
from spack.pkg.k4.key4hep_stack import Key4hepPackage


class K4actstracking(CMakePackage, Key4hepPackage):
    """Acts tracking components for the key4hep project"""

    homepage = "https://github.com/MuonColliderSoft/k4ActsTracking.git"
    git = "https://github.com/MuonColliderSoft/k4ActsTracking.git"
    url = "https://github.com/MuonColliderSoft/k4ActsTracking/archive/refs/tags/v00-01.tar.gz"

    maintainers("vvolkl")

    version("main", branch="main")

    version("0.2", sha256="f805d292529409c9460627d533ec787567811340a1dedb6ad64b793e974aeb72", preferred=True)
    version("0.1", sha256="e214a0bff098ba306490f6dbd68fb3b19c1f3c6d7dc32cf3506bf9de104fb012")

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