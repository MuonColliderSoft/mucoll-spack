# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Overlay(CMakePackage, MCIlcsoftpackage):
    """The package Overlay provides code for event overlay with Marlin."""

    homepage = "https://github.com/madbaron/Overlay"
    git = "https://github.com/madbaron/Overlay.git"
    url = "https://github.com/madbaron/Overlay/archive/refs/tags/v00-24-MC.tar.gz"

    maintainers = ['fmeloni']

    version('master',  branch='randomFileOverlay')

    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('clhep')
    depends_on('raida')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path(
            'MARLIN_DLL', self.prefix.lib + "/libOverlay.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
