# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.k4.key4hep_stack import Key4hepPackage


class Actstracking(CMakePackage, Key4hepPackage):
    """Marlin package for track reconstructions using the ACTS library"""

    homepage = "https://github.com/MuonColliderSoft/ACTSTracking"
    git      = "https://github.com/MuonColliderSoft/ACTSTracking.git"
    url      = "https://github.com/MuonColliderSoft/ACTSTracking/archive/refs/tags/v1.1.0.tar.gz"

    maintainers = ['gianelle', 'kkrizka']

    version("porting_v32", branch="porting_v32")
    version("1.1.1", branch="KITP_10TeV")
    version(
        '1.1.0', sha256='d565e70a2fec97d0d2e81ada69ed54ef8dacc44b0f608b4cf3dffa561091afeb')
    version(
        '1.0.0', sha256='0e98f2185920358d9c220883a48df42f3b5282beb32a91a19f9f3f5c1adc103b')

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
        spack_env.prepend_path(
            'MARLIN_DLL', self.prefix.lib + "/libACTSTracking.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
