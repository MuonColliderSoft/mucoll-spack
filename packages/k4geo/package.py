# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class K4geo(CMakePackage):
    """DD4hep geometry models for future colliders.

    MuColl overlay of the upstream key4hep/k4geo recipe. The only addition is a
    ``beampipe_stl`` variant: upstream ties INSTALL_BEAMPIPE_STL_FILES to the
    ``compact`` variant, which downloads the FCC-ee MDI beampipe CAD over the
    network at configure time (flaky, and unused by MuColl). This variant lets
    the stack opt out (see packages.yaml: k4geo ... ~beampipe_stl).
    """

    homepage = "https://github.com/key4hep/k4geo"
    git = "https://github.com/key4hep/k4geo.git"
    url = "https://github.com/key4hep/k4geo/archive/v00-16-07.tar.gz"

    generator = "Ninja"

    maintainers("jmcarcell", "madbaron")

    version("main", branch="main")
    version(
        "00-24",
        sha256="3eefd973c0e534cc5cbb4d8fc079455508986bba49f859c30e0c23ac3e732f19",
    )
    version(
        "00-23",
        sha256="dd0c6300a6a2190a089012dfea271bd31050e8d4134ce09d896ebd81ef7391c5",
    )
    version(
        "00-22",
        sha256="95712eaf3452d29d35ac8156c37e5b4ea6449eb04073fb330bddc5df686f2cb3",
    )

    variant("compact", default=True, description="Install compact files")
    variant(
        "beampipe_stl",
        default=True,
        description="Download and install the FCC-ee MDI beampipe CAD (STL) files",
    )

    depends_on("cxx", type="build")

    depends_on("lcio")
    depends_on("dd4hep")
    depends_on("dd4hep@1.31:", when="@0.22:")
    depends_on("root")
    depends_on("python", type="build")
    depends_on("ninja", type="build")
    depends_on("podio")

    def cmake_args(self):
        args = []
        args.append(
            f"-DCMAKE_CXX_STANDARD={self.spec['root'].variants['cxxstd'].value}"
        )
        args.append(self.define_from_variant("INSTALL_COMPACT_FILES", "compact"))
        # The beampipe STL files are downloaded from the network at configure
        # time, so this variant lets consumers opt out (the MuColl stack does,
        # via packages.yaml: it doesn't use the FCC-ee MDI beampipe CAD).
        args.append(self.define_from_variant("INSTALL_BEAMPIPE_STL_FILES", "beampipe_stl"))
        args.append(self.define("BUILD_TESTING", self.run_tests))
        return args

    def setup_run_environment(self, env):
        env.set("LCGEO", self.prefix.share.k4geo)
        env.set("K4GEO", self.prefix.share.k4geo)
        env.set("lcgeo_DIR", self.prefix.share.k4geo)
        env.set("k4geo_DIR", self.prefix.share.k4geo)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4geo"].libs.directories[0])

    def setup_build_environment(self, env):
        env.set("LCGEO", self.prefix.share.k4geo)
        env.set("lcgeo_DIR", self.prefix.share.k4geo)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["lcio"].libs.directories[0])
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)

    def setup_dependent_run_environment(self, env, dependent_spec):
        env.set("LCGEO", self.prefix.share.k4geo)
        env.set("lcgeo_DIR", self.prefix.share.k4geo)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4geo"].libs.directories[0])
        env.prepend_path("LD_LIBRARY_PATH", self.spec["lcio"].libs.directories[0])

    def setup_dependent_build_environment(self, env, dependent_spec):
        env.set("LCGEO", self.prefix.share.k4geo)
        env.set("lcgeo_DIR", self.prefix.share.k4geo)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4geo"].libs.directories[0])
        env.prepend_path("LD_LIBRARY_PATH", self.spec["lcio"].libs.directories[0])

    # dd4hep tests need to run after install step:
    # disable the usual check
    def check(self):
        pass

    # instead add custom check step that runs after installation
    @run_after("install")
    def install_check(self):
        print(self)
        with working_dir(self.build_directory):
            if self.run_tests:
                ninja("test")
