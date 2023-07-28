# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Dd4hep(CMakePackage):
    """DD4hep is a software framework for providing a complete solution for
    full detector description (geometry, materials, visualization, readout,
    alignment, calibration, etc.) for the full experiment life cycle
    (detector concept development, detector optimization, construction,
    operation). It offers a consistent description through a single source
    of detector information for simulation, reconstruction, analysis, etc.
    It distributed under the LGPLv3 License."""

    homepage = "https://dd4hep.web.cern.ch/dd4hep/"
    url = "https://github.com/madbaron/DD4hep/archive/v01-12-01.tar.gz"
    git = "https://github.com/madbaron/DD4hep.git"

    maintainers("madbaron")

    tags = ["hep"]

    version("1.25.3", branch="rebase1251")

    generator("ninja")

    # variants for subpackages
    variant("ddcad", default=True,
            description="Enable CAD interface based on Assimp")
    variant("ddg4", default=True,
            description="Enable the simulation part based on Geant4")
    variant("ddrec", default=True, description="Build DDRec subpackage.")
    variant("dddetectors", default=True,
            description="Build DDDetectors subpackage.")
    variant("ddcond", default=True, description="Build DDCond subpackage.")
    variant("ddalign", default=True, description="Build DDAlign subpackage.")
    variant("dddigi", default=True, description="Build DDDigi subpackage.")
    variant("ddeve", default=True, description="Build DDEve subpackage.")
    variant("utilityapps", default=True,
            description="Build UtilityApps subpackage.")

    # variants for other build options
    variant("xercesc", default=False,
            description="Enable 'Detector Builders' based on XercesC")
    variant("hepmc3", default=False, description="Enable build with hepmc3")
    variant("lcio", default=False, description="Enable build with lcio")
    variant("edm4hep", default=True, description="Enable build with edm4hep")
    variant("geant4units", default=False,
            description="Use geant4 units throughout")
    variant("tbb", default=False, description="Enable build with tbb")
    variant(
        "debug",
        default=False,
        description="Enable debug build flag - adds extra info in"
        " some places in addtion to the debug build type",
    )

    depends_on("cmake @3.12:", type="build")
    depends_on("boost @1.49:")
    depends_on("boost +iostreams", when="+ddg4")
    depends_on("boost +system +filesystem", when="%gcc@:7")
    depends_on("root @6.08: +gdml +math +python")
    with when("+ddeve"):
        depends_on("root @6.08: +x +opengl")
        depends_on("root +webgui", when="^root@6.28:")
        depends_on("root @:6.27", when="@:1.23")
    depends_on("root @6.08: +gdml +math +python +x +opengl",
               when="+utilityapps")

    extends("python")
    depends_on("xerces-c", when="+xercesc")
    depends_on("geant4@10.2.2:", when="+ddg4")
    depends_on("assimp@5.0.2:", when="+ddcad")
    depends_on("hepmc3", when="+hepmc3")
    depends_on("tbb", when="+tbb")
    depends_on("intel-tbb@:2020.3", when="+tbb @:1.23")
    depends_on("lcio", when="+lcio")
    depends_on("edm4hep", when="+edm4hep")
    depends_on("podio", when="+edm4hep")
    depends_on("podio@:0.16.03", when="@:1.23 +edm4hep")
    depends_on("podio@0.16:", when="@1.24: +edm4hep")
    depends_on("py-pytest", type=("build", "test"))

    # See https://github.com/AIDASoft/DD4hep/pull/771 and https://github.com/AIDASoft/DD4hep/pull/876
    conflicts(
        "^cmake@3.16:3.17.2",
        when="@1.15:1.18",
        msg="cmake version with buggy FindPython breaks dd4hep cmake config",
    )
    conflicts("~ddrec+dddetectors",
              msg="Need to enable +ddrec to build +dddetectors.")

    def cmake_args(self):
        spec = self.spec
        cxxstd = spec["root"].variants["cxxstd"].value
        # root can be built with cxxstd=11, but dd4hep requires 14
        if cxxstd == "11":
            cxxstd = "14"
        args = [
            self.define_from_variant("DD4HEP_USE_EDM4HEP", "edm4hep"),
            self.define_from_variant("DD4HEP_USE_XERCESC", "xercesc"),
            self.define_from_variant("DD4HEP_USE_TBB", "tbb"),
            self.define_from_variant("DD4HEP_USE_GEANT4", "ddg4"),
            self.define_from_variant("DD4HEP_USE_LCIO", "lcio"),
            self.define_from_variant("DD4HEP_USE_HEPMC3", "hepmc3"),
            self.define_from_variant("DD4HEP_USE_GEANT4_UNITS", "geant4units"),
            self.define_from_variant("DD4HEP_BUILD_DEBUG", "debug"),
            # Downloads assimp from github and builds it on the fly.
            # However, with spack it is preferrable to have a proper external
            # dependency, so we disable it.
            self.define("DD4HEP_LOAD_ASSIMP", False),
            "-DCMAKE_CXX_STANDARD={0}".format(cxxstd),
            "-DBUILD_TESTING={0}".format(self.run_tests),
            "-DBOOST_ROOT={0}".format(spec["boost"].prefix),
            "-DBoost_NO_BOOST_CMAKE=ON",
            "-DPYTHON_EXECUTABLE={0}".format(spec["python"].command.path),
        ]
        subpackages = []
        if spec.satisfies("+ddg4"):
            subpackages += ["DDG4"]
        if spec.satisfies("+ddcond"):
            subpackages += ["DDCond"]
        if spec.satisfies("+ddcad"):
            subpackages += ["DDCAD"]
        if spec.satisfies("+ddrec"):
            subpackages += ["DDRec"]
        if spec.satisfies("+dddetectors"):
            subpackages += ["DDDetectors"]
        if spec.satisfies("+ddalign"):
            subpackages += ["DDAlign"]
        if spec.satisfies("+dddigi"):
            subpackages += ["DDDigi"]
        if spec.satisfies("+ddeve"):
            subpackages += ["DDEve"]
        if spec.satisfies("+utilityapps"):
            subpackages += ["UtilityApps"]
        subpackages = " ".join(subpackages)
        args += [self.define("DD4HEP_BUILD_PACKAGES", subpackages)]
        return args

    def setup_run_environment(self, env):
        # used p.ex. in ddsim to find DDDetectors dir
        env.set("DD4hepINSTALL", self.prefix)
        env.set("DD4HEP", self.prefix.examples)
        env.set("DD4hep_DIR", self.prefix)
        env.set("DD4hep_ROOT", self.prefix)
        env.set("LD_LIBRARY_PATH", self.prefix.lib)
        env.set("LD_LIBRARY_PATH", self.prefix.lib64)

    def url_for_version(self, version):
        # dd4hep releases are dashes and padded with a leading zero
        # the patch version is omitted when 0
        # so for example v01-12-01, v01-12 ...
        base_url = self.url.rsplit("/", 1)[0]
        if len(version) == 1:
            major = version[0]
            minor, patch = 0, 0
        elif len(version) == 2:
            major, minor = version
            patch = 0
        else:
            major, minor, patch = version
        # By now the data is normalized enough to handle it easily depending
        # on the value of the patch version
        if patch == 0:
            version_str = "v%02d-%02d.tar.gz" % (major, minor)
        else:
            version_str = "v%02d-%02d-%02d.tar.gz" % (major, minor, patch)

        return base_url + "/" + version_str

    # dd4hep tests need to run after install step:
    # disable the usual check
    def check(self):
        pass

    # instead add custom check step that runs after installation
    @run_after("install")
    def build_test(self):
        with working_dir(self.build_directory):
            if self.run_tests:
                ninja("test")
