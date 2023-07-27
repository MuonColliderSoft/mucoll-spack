# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *

from spack.pkg.k4.key4hep_stack import Key4hepPackage


class K4edm4hep2lcioconv(CMakePackage, Key4hepPackage):
    """Converter library between EDM4hep and LCIO"""

    homepage = "https://github.com/tmadlener/k4EDM4hep2LcioConv"
    git = "https://github.com/tmadlener/k4EDM4hep2LcioConv.git"
    url = "https://github.com/tmadlener/k4EDM4hep2LcioConv/archive/v00-01.zip"

    maintainers = ["tmadlener"]

    version("mucoll-conv-production", branch="mucoll-conv-production")

    depends_on("lcio")
    depends_on("lcio@2.20:", when="@00-05:")
    depends_on("podio")
    depends_on("edm4hep@0.5:", when="@00-03")
    depends_on("edm4hep@0.8:", when="@00-04:")
    depends_on("edm4hep@0.10:", when="@00-05:")

    def cmake_args(self):
        args = [
            self.define("BUILD_TESTING", self.run_tests),
            self.define("FORCE_COLORED_OUTPUT", False),
        ]
        args.append(
            "-DCMAKE_CXX_STANDARD=%s" % self.spec["root"].variants["cxxstd"].value
        )
        return args

    def setup_run_environment(self, env):
        env.set("K4EDM4HEP2LCIOCONV", self.prefix.share.k4EDM4hep2LcioConv)
