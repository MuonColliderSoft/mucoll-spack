# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.pkg.mucoll.mucoll_stack import Key4hepPackage
    

class Muoncvxddigitiser(CMakePackage, Key4hepPackage):
    """Realistic digitiser of pixelated sensors for Muon Collider"""

    homepage = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser"
    git      = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser.git"
    url      = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser/archive/refs/tags/v0.2.0.tar.gz"

    version("master", branch="gaudification")
    
    depends_on('edm4hep')
    depends_on('gaudi')
    depends_on('dd4hep')
    depends_on('k4fwcore')
    depends_on('gsl')

    def cmake_args(self):
        args = [
            self.define(
                "CMAKE_CXX_STANDARD", self.spec["root"].variants["cxxstd"].value
            ),
        ]
        return args

    def setup_run_environment(self, env):
        env.prepend_path("PYTHONPATH", self.prefix.python)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["muoncvxddigitiser"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["muoncvxddigitiser"].prefix.lib64)
