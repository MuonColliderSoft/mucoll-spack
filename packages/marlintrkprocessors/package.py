# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Marlintrkprocessors(CMakePackage, MCIlcsoftpackage):
    """A collection of Tracking Relelated Processors Based on MarlinTrk"""

    homepage = "https://github.com/madbaron/MarlinTrkProcessors"
    git      = "https://github.com/madbaron/MarlinTrkProcessors.git"
    url      = "https://github.com/madbaron/MarlinTrkProcessors/archive/refs/tags/v02-14-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master', branch='master')
    version("2.15",   sha256="439c2d01bd36c165a2a9e19caeceb807466691a5f240984a2654e2b6d3d0bcbf")
    version('2.14',   sha256='3fda69fbbd23e8e3e7f3c47d898dcd301693286f0a17854e919cfbe68bf3918f')
    version('2.13',   sha256='a44fe66a62d252f5226ca710a913fca6337812af1b7937bfb050d8f2d34df011')
    version('2.12',   sha256='458b3e428aece3b7749bb292695320a1126d246ee40da8eede2a13714b204615')
    version('2.11',   sha256='ee1f5958e4b7a44b4ba2d231465c6d0e8d031d8091383393ca5de24381f1e883')

    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('dd4hep')
    depends_on('marlintrk')
    depends_on('kitrack')
    depends_on('kitrackmarlin')
    depends_on('gsl')
    depends_on('ddkaltest')
    depends_on('raida')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libMarlinTrkProcessors.so")

    def cmake_args(self):
        return [
            self.define('CMAKE_CXX_STANDARD',
                        self.spec['root'].variants['cxxstd'].value)
        ]
