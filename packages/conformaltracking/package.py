# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Conformaltracking(CMakePackage, MCIlcsoftpackage):
    """Package for running pattern recognition based on conformal mapping
       and cellular automaton. This is not tied to a given geometry, but
       has been developed for the CLIC detector model 2015."""

    homepage = "https://github.com/MuonColliderSoft/ConformalTracking"
    git      = "https://github.com/MuonColliderSoft/ConformalTracking.git"
    url      = "https://github.com/MuonColliderSoft/ConformalTracking/archive/refs/tags/v01-12-MC.tar.gz"


    maintainers = ['gianelle', 'pandreetto']

    version('master', branch='master')
    version('1.12.1', sha256='2fca66be42850afbea910dd8eabc5761d7cb4c517ff7e936503b10bc83218950', preferred=True)
    version('1.12',   sha256='676d20c3f6b6c03910377d0cb241120567cd6c6bd4fbdd0df708965302872e53')
    version('1.11',   sha256='ea5a8e600546f4a67b555c89bb4f60bd95e6fab2259fe72af78ca865cc76819a')
    version('1.10',   sha256='fa3d8c12e92dc0748bb427fe3a388b8d500acb5c0e171736068fffe2135b4b7d')

    depends_on('ilcutil')
    depends_on('root')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('marlintrk')
    depends_on('raida')
    depends_on('boost')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libConformalTracking.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
