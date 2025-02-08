# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Forwardtracking(CMakePackage, MCIlcsoftpackage):
    """Track Reconstruction for the Forward Direction (for the FTD)"""

    homepage = "https://github.com/MuonColliderSoft/ForwardTracking"
    git      = "https://github.com/MuonColliderSoft/ForwardTracking.git"
    url      = "https://github.com/MuonColliderSoft/ForwardTracking/archive/refs/tags/v01-14-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master', branch='master')
    version('1.14.2', sha256='e07cf6e71e2198253c53a1ea017d827d432de7c541c84642c89edf99184785b4', preferred=True)
    version('1.14',   sha256='00e4fd4fc4be2c0c6febf6927fd5b37856ecb80a82d62836086ce4b53c1fb107')

    patch('testing.patch', when="@:1.15")

    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('marlintrk')
    depends_on('kitrack')
    depends_on('kitrackmarlin')
    depends_on('gsl')
    depends_on('root')
    depends_on('clhep')
    depends_on('raida')


    def cmake_args(self):
        args = []
        args.append(self.define('BUILD_TESTING', self.run_tests))
        args.append(self.define('CMAKE_CXX_STANDARD',
                                self.spec['root'].variants['cxxstd'].value))
        return args

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libForwardTracking.so")
