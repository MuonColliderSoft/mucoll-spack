# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.pkg.k4.key4hep_stack import Key4hepPackage


class Muoncvxddigitiser(CMakePackage, Key4hepPackage):
    """Realistic digitiser of pixelated silicon sensors for the Muon Collider,
    implemented as Gaudi algorithms for the Key4hep framework."""

    homepage = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser"
    url = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser/archive/refs/tags/v0.5.0.tar.gz"
    git = "https://github.com/MuonColliderSoft/MuonCVXDDigitiser.git"

    maintainers("madbaron")

    version("master", branch="master")
    version(
        "0.5.0",
        sha256="9946214181f4fa0a7444ee1462eed7964bb6b101752c9d8e1f291ff50926d8d5",
    )

    depends_on("cxx", type="build")
    depends_on("cmake@3.23:", type="build")

    depends_on("podio")
    depends_on("edm4hep")
    depends_on("dd4hep")
    depends_on("gaudi")
    depends_on("k4fwcore")
    depends_on("root")
    depends_on("clhep")
    depends_on("gsl")

    # The regression tests need the MAIA_v0 geometry and download their input samples
    depends_on("k4geo", type="test")
    depends_on("python", type="test")

    def cmake_args(self):
        args = [
            self.define(
                "CMAKE_CXX_STANDARD", self.spec["root"].variants["cxxstd"].value
            ),
            self.define("BUILD_TESTING", self.run_tests),
            self.define("CMAKE_INSTALL_LIBDIR", "lib"),
        ]
        return args

    def setup_build_environment(self, env):
        if self.run_tests:
            env.set("K4GEO", self.spec["k4geo"].prefix.share.k4geo)

    def setup_run_environment(self, env):
        env.prepend_path("PYTHONPATH", self.prefix.python)
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)
