# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class K4geo(CMakePackage):
    """DD4hep geometry models for future colliders.

    MuColl overlay of the upstream key4hep/k4geo recipe. It points at the
    madbaron fork and adds a ``geant4`` variant wired to the new
    ``K4GEO_USE_GEANT4`` CMake option, so the Geant4-dependent k4geoG4 plugin
    (the only part of k4geo that links DD4hep::DDG4 and Geant4) can be skipped.
    Disabling it lets the reconstruction layer build k4geo with no Geant4 at all.
    """

    homepage = "https://github.com/key4hep/k4geo"
    git = "https://github.com/madbaron/k4geo.git"
    url = "https://github.com/key4hep/k4geo/archive/v00-16-07.tar.gz"

    generator = "Ninja"

    maintainers("jmcarcell", "madbaron")

    # Test branch carrying the optional-Geant4-plugin change (madbaron fork).
    version("optional-geant4-plugin", branch="optional-geant4-plugin")
    version("main", branch="main")

    variant("compact", default=True, description="Install compact files")
    variant(
        "geant4",
        default=True,
        description="Build the Geant4-dependent k4geoG4 plugin (requires DD4hep DDG4 and Geant4)",
    )
    variant(
        "beampipe_stl",
        default=True,
        description="Download and install the FCC-ee MDI beampipe CAD (STL) files",
    )

    depends_on("cxx", type="build")

    depends_on("lcio")
    depends_on("dd4hep@1.31:")
    # The DDG4 component (and Geant4) are only needed for the k4geoG4 plugin.
    depends_on("dd4hep+ddg4", when="+geant4")
    depends_on("geant4", when="+geant4")
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
        args.append(self.define_from_variant("K4GEO_USE_GEANT4", "geant4"))
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
