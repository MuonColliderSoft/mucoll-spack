from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class MarlinACTS(CMakePackage, MCIlcsoftpackage):
    """Marlin package for track reconstructions using the ACTS library"""

    homepage = "https://github.com/MuonColliderSoft/MarlinACTS"
    git      = "https://github.com/MuonColliderSoft/MarlinACTS.git"
    url      = "https://github.com/MuonColliderSoft/MarlinACTS/archive/refs/tags/v1.0.3.tar.gz"

    maintainers = ['pandreetto']

    version('main', branch='main')
    version("1.0.3", sha256='52f86c08847537a76eab3f90ca9fe3ceda5a048734743f9ce36c75cdeaf3be1b', preferred=True)

    # Ensuring correct ACTS version due to its evolving API
    depends_on('acts@42.0.0 +dd4hep+tgeo+identification+json+fatras')

    depends_on('dd4hep')
    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('root')
    depends_on('tbb')

    # Building in parallel may fail
    parallel = False

    
    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libMarlinACTS.so")
        spack_env.set('MarlinACTS_DATA', self.prefix.share.MarlinACTS.data)
        spack_env.set("ACTS_TGeoFile", self.prefix.share.MarlinACTS.data + "/MuSIC_v2.root")
        spack_env.set("ACTS_MatFile", self.prefix.share.MarlinACTS.data + "/material-maps.json")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
