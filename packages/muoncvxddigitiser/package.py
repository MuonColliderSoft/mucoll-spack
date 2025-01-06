# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage


class Muoncvxddigitiser(CMakePackage, MCIlcsoftpackage):
    """Realistic digitiser of pixelated sensors for Muon Collider"""

    homepage = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser"
    git      = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser.git"
    url      = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser/archive/refs/tags/v0.2.0.tar.gz"

    version("master", branch="master")
    version("0.2.0", sha256="6d22f0fe712a9165725fe23ac123f5c90e6e26e4eb11aeb5601eecb40ef1a85c", preferred=True)
    version("0.1", sha256="b4fe817025aeda01e0d503a91a5988b4c1d906dfcb02d2a505f013f8de90efc0")
    
    depends_on('ilcutil')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('dd4hep')
    depends_on('lcio')
    depends_on('clhep')

    # Defining patches
    patch("cmake_v0.1.patch", when='@=0.1')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libMuonCVXDDigitiser.so")

    def cmake_args(self):
        # C++ Standard
        return [
            '-DCMAKE_CXX_STANDARD=%s' % self.spec['root'].variants['cxxstd'].value
        ]
