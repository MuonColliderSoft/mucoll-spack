from spack.package import *
from spack.pkg.mucoll.mucoll_stack import Key4hepPackage


class K4actstracking(CMakePackage, Key4hepPackage):
    """Acts tracking components for the key4hep project"""

    url = "https://github.com/MuonColliderSoft/k4ActsTracking/archive/v00-11.tar.gz"
    homepage = "https://github.com/MuonColliderSoft/k4ActsTracking"
    git = "https://github.com/MuonColliderSoft/k4ActsTracking.git"

    maintainers("vvolkl")

    version("main", branch="main")

    depends_on("acts+dd4hep+tgeo+json")
    depends_on("gaudi")
    depends_on("root")
    depends_on("edm4hep")
    depends_on("k4fwcore")
    depends_on("acts-dd4hep")

    def cmake_args(self):
        return []
