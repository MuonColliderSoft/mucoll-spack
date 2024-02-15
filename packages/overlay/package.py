# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Overlay(CMakePackage, MCIlcsoftpackage):
    """The package Overlay provides code for event overlay with Marlin."""

    homepage = "https://github.com/MuonColliderSoft/Overlay"
    git      = "https://github.com/MuonColliderSoft/Overlay.git"
    url      = "https://github.com/MuonColliderSoft/Overlay/archive/refs/tags/v00-24-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master',  branch='master')
    version('0.25.0.1', sha256='ca293cd96ec4be115d73321df41cbce96b49ec995a54b025c6dc344367265266')
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
