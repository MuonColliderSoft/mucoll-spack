# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Ddmarlinpandora(CMakePackage, MCIlcsoftpackage):
    """Interface between Marlin and PandoraPFA."""

    homepage = "https://github.com/MuonColliderSoft/DDMarlinPandora"
    git      = "https://github.com/MuonColliderSoft/DDMarlinPandora.git"
    url      = "https://github.com/MuonColliderSoft/DDMarlinPandora/archive/refs/tags/v00-14-MC.tar.gz"

    maintainers = ['gianelle', 'pandreetto']

    version('master', branch='master')
    version('evo', commit="4949f8652917df382d26bb191d5a8f8141695872", preferred=True)
    version('0.14',  sha256='b22f1fb589d59b9878d746632ad74ca76a03153b16c8901023eecc7469f6dbdb')
    version('0.13',  sha256='1e14a89cd408f597f27b2743af7684068457d6f0b0e1737f03e8093d9deb23d3')
    version('0.12',  sha256='39b0d22b9b4527bce11f3a741f102660d7986dadb4eca085de91f0d256855ddc')

    depends_on('ilcutil')
    depends_on('marlinutil')
    depends_on('marlin')
    depends_on('pandorasdk')
    depends_on("pandorapfa")
    depends_on("lccontent")
    depends_on("larcontent")
    depends_on('dd4hep')
    depends_on('marlintrk')
    depends_on("pandoramonitoring", when="+monitoring")

    variant("monitoring", default=False, description="Enable Pandora Monitoring")

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libDDMarlinPandora.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value,
            self.define_from_variant("PANDORA_MONITORING", "monitoring"),
        ]
