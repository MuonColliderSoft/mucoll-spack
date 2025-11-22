# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Marlintrkprocessors(CMakePackage, MCIlcsoftpackage):
    """A collection of Tracking Relelated Processors Based on MarlinTrk"""

    homepage = "https://github.com/MuonColliderSoft/MarlinTrkProcessors"
    git      = "https://github.com/MuonColliderSoft/MarlinTrkProcessors.git"
    url      = "https://github.com/MuonColliderSoft/MarlinTrkProcessors/archive/refs/tags/v02-14-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master', branch='master')
    version("2.18.2", sha256="1509997dcd3de25225cf08039297ca15eafcd279faa96a288c26b98af4d1fdb2", preferred=True)    
    version("2.18.1", sha256="d9271330e39a02547f0dc6d83e35364e08336d8ba12464ddf7bfeef6f29b411d")    
    version("2.18",   sha256="82fe72309a63c24661b2d66d127b6f2c5ffb69c4a001354c50806a751879e8c0")    
    version("2.17.1", sha256="e16971067006826a98b3fe9d6973f58c559bd1f8a8741deb626e58b5a220379a")
    version('2.17',   sha256='9730086392b8b60abe45ce9b69c06823fa006e89752ba2e72c7b5373199b6992')
    version('2.16',   sha256='cb37cb149e7d12e8a8b9e481183b661bacc24d13c94ef048c3ad6a94c94de8d2')
    version('2.15.2', sha256='346c8ddd35271a2ca7c09eede101cceb7356a6c1d6f8532cd047a60dc5d067df')
    version('2.15.1', sha256='c8e8ff7bdea755fa1b5f65341a50009cbc05e59ab206c8046d43e169939b5418')
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
