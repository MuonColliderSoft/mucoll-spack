# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Actstracking(CMakePackage, MCIlcsoftpackage):
    """Marlin package for track reconstructions using the ACTS library"""

    homepage = "https://github.com/MuonColliderSoft/ACTSTracking"
    git      = "https://github.com/MuonColliderSoft/ACTSTracking.git"
    url      = "https://github.com/MuonColliderSoft/ACTSTracking/archive/refs/tags/v1.1.0.tar.gz"

    maintainers = ['gianelle', 'kkrizka']

    version('main', branch='main')
    version('1.3.1', sha256='ff9014f17931fa8d883e4d944a5d745a91d03afae7c4fb8d05a95fd7cb54c917', preferred=True)
    version('1.3.0', sha256='d013a7700ce453054848572603bcfc6fdf4f5a4d')
    version('1.2.2', sha256='be08b87037167892a9b1a7ad601511beaf99423e836841436c6318fef5fa93de')
    version('1.2.1', sha256='747c15a4c937ab09d79afcc956bb1f1f82ce345febfb4bd18462b71e70ae0b29')
    version('1.2', sha256='7390d03ab848f7ad9e67c5aabda8122942a885256775174db30964fb9fe028e1')
    version('1.1.0', sha256='d565e70a2fec97d0d2e81ada69ed54ef8dacc44b0f608b4cf3dffa561091afeb')
    version('1.0.0', sha256='0e98f2185920358d9c220883a48df42f3b5282beb32a91a19f9f3f5c1adc103b')

    # Ensuring correct ACTS version due to its evolving API
    depends_on('acts +dd4hep+tgeo+identification+json+fatras')
    depends_on('acts@13 +dd4hep+tgeo+identification+json+fatras', when="@:1.1.0")

    depends_on('dd4hep')
    depends_on('ilcutil')
    depends_on('marlin@1.0:')
    depends_on('root')

    # Building in parallel may fail
    parallel = False

    
    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libACTSTracking.so")
        spack_env.set("ACTS_TGeoFile", self.prefix.share.ACTSTracking.data + "/MuColl_v1.root")
        spack_env.set("ACTS_MatFile", self.prefix.share.ACTSTracking.data + "/material-maps.json")
        spack_env.set("ACTS_TGeoFile_MuSIC", self.prefix.share.ACTSTracking.data + "/MuSIC_v2.root")
        spack_env.set("ACTS_MatFile_MuSIC", self.prefix.share.ACTSTracking.data + "/material-maps.json")
        spack_env.set("ACTS_TGeoFile_MAIA", self.prefix.share.ACTSTracking.data + "/MAIA_v0.root")
        spack_env.set("ACTS_MatFile_MAIA", self.prefix.share.ACTSTracking.data + "/MAIA_v0_material.json")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
