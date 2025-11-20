# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.k4.key4hep_stack import Ilcsoftpackage
from spack.package import *

class Marlinmuonid(CMakePackage, Ilcsoftpackage):
    """Marlin-based processor for muon identification"""

    homepage = "https://github.com/MuonColliderSoft/MarlinMuonID"
    git      = "https://github.com/MuonColliderSoft/MarlinMuonID.git"
    url      = "https://github.com/MuonColliderSoft/MarlinMuonID/archive/refs/tags/v00-00-02.tar.gz"

    maintainers = ['casarsa', 'pandreetto']

    version('main', branch='main')
    version("0.0.2", sha256="b65ed78295bfa47492e586788ebe3d154e1a771e510d271c7da0aa4aaccacb3a", preferred=True)    
    version("0.0.1", sha256="6a578764d6c2146b91992758f5d16fc85700db62e66a7757d52c5a49cdbee8d3")    

    depends_on('marlin')
    depends_on('dd4hep')
    depends_on('root')
    depends_on('gsl')
    depends_on('pandorasdk')
    depends_on('raida')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libMarlinMuonID.so")

    def cmake_args(self):
        return [
            self.define('CMAKE_CXX_STANDARD',
                        self.spec['root'].variants['cxxstd'].value)
        ]
