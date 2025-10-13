# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Overlay(CMakePackage, MCIlcsoftpackage):
    """The package Overlay provides code for event overlay with Marlin."""

    homepage = "https://github.com/MuonColliderSoft/Overlay"
    git      = "https://github.com/MuonColliderSoft/Overlay.git"
    url      = "https://github.com/MuonColliderSoft/Overlay/archive/refs/tags/v00-24-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master',  branch='master')
    version('evo', commit="8b8a68d3cd9d74f134a17934a9865831fe0aac4e", preferred=True)
    version('0.26',    sha256='6451adfc5b2e3cbc98c0842442e455866a18138dd55ee9384f243b18c12514e9')
    version('0.25',    sha256='32a840a14b4d74b3689c83ae05ffb63cfa5996c8ab3beb8d83e2d098f2cda18d')
    version('0.24',    sha256='83ddebb4c3e36b9b5bda2acfb658e5fd0fd2b31f5e5a38c54f72601379949c04')
    version('0.23',    sha256='b885bed6c386676e74db21dafde6bc08bcac2a16df89892759415fb8bbb331ed')
    version('0.22.2',  sha256='9d4ed2d218897f0cbec233d5c588db41bd002dcd5ce809f5b3bad7767408de58')

    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('clhep')
    depends_on('raida')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libOverlay.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
