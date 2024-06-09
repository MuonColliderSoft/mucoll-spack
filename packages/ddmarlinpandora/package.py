# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Ddmarlinpandora(CMakePackage, MCIlcsoftpackage):
    """Interface between Marlin and PandoraPFA."""

    homepage = "https://github.com/tmadlener/DDMarlinPandora/"
    git = "https://github.com/tmadlener/DDMarlinPandora.git"
    url = "https://github.com/tmadlener/DDMarlinPandora/archive/refs/tags/v00-14-MC.tar.gz"

    maintainers = ['tmadlener']

    version('ECALcorr', branch='ecal-energy-corrections')

    depends_on('ilcutil')
    depends_on('marlinutil')
    depends_on('marlin')
    depends_on('pandorasdk')
    depends_on("pandorapfa")
    depends_on("lccontent")
    depends_on("larcontent")
    depends_on('dd4hep')
    depends_on('marlintrk')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path(
            'MARLIN_DLL', self.prefix.lib + "/libDDMarlinPandora.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
