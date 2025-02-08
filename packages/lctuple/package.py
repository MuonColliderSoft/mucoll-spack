# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Lctuple(CMakePackage, MCIlcsoftpackage):
    """Marlin package that creates a ROOT TTree with a column wise ntuple from LCIO collections."""

    homepage = "https://github.com/MuonColliderSoft/LCTuple"
    git      = "https://github.com/MuonColliderSoft/LCTuple.git"
    url      = "https://github.com/MuonColliderSoft/LCTuple/archive/refs/tags/v01-15-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master',  branch='master')
    version('1.15',    sha256='4db2360a58ec51df44c84acf95560d6723f4130ba61834c0c9b2153ece28d212')
    version('1.14',    sha256='3311c84c21123bf572dda99bfc56327382b7377f0449ed5b4e998dc9ff864390')
    version('1.13',    sha256='704b89051db8409f6d55baf1fa1094e6ec5322b799e1431ed97e9b28a42f610a')
    version('1.12.2',  sha256='52e925398cf997dfe093b8a7085c683244aa8469b19f514239ebc4f08ab1870d')

    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('root')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libLCTuple.so")

    def cmake_args(self):
        args = []
        # C++ Standard
        args.append('-DCMAKE_CXX_STANDARD=%s'
                    % self.spec['root'].variants['cxxstd'].value)
        args.append('-DBUILD_TESTING=%s' % self.run_tests)
        return args
