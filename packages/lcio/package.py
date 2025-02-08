# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *
from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage

class Lcio(CMakePackage, MCIlcsoftpackage):
    """HEP Library for Linear Collider Input/Output"""

    homepage = "http://lcio.desy.de"
    git      = "https://github.com/MuonColliderSoft/LCIO.git"
    url      = "https://github.com/MuonColliderSoft/LCIO/archive/refs/tags/v02-17-MC.tar.gz"

    tags = ["hep"]

    maintainers = ['gianelle', 'pandreetto']

    version("master",  branch="master")
    version('2.22.4', sha256='2c2bd66cb8c5b58ab27ab7d36f16df3bed3f0bcefd880e69b9d3f5a8d01ffb0b', preferred=True)
    version('2.22', sha256='2ae4361c0c67f7dffb24a06525ef909e97a18545d1cef4e36887e220b2420e4b')
    version('2.19.1', sha256='ae2c417381025bbebeef9c9806ab104c3404474ab555569f64c5dabd5c69b5d5')
    version('2.17',    sha256='b04422eaf224a0e64d5410bedc47bf0259912990fda136ec3dcdaee8c79e6b86')
    version('2.16.1',  sha256='e5319053c1f8fe7be40fb250e3694c926595533b13e108a08cb718a04bef137e')
    version('2.15.4',  sha256='80a6be5bf14c33e62710f55850985a347529b42c8279e6d230ba7b48a420b596')

    variant(
        "cxxstd",
        default="17",
        values=("11", "14", "17", "20"),
        multi=False,
        description="Use the specified C++ standard when building.",
    )
    variant("jar", default=False, description="Turn on to build/install lcio.jar")
    variant("rootdict", default=True, description="Turn on to build/install ROOT dictionary.")
    variant("examples", default=False, description="Turn on to build LCIO examples")

    depends_on("sio@0.0.2:", when="@2.14:")
    depends_on("sio@0.1:", when="@2.16:")

    depends_on("root@6.04:", when="+rootdict")
    for cxx in ['11', '14', '17', '20']:
        depends_on(f"root@6.04: cxxstd={cxx}", when=f"+rootdict cxxstd={cxx}")
    depends_on("openjdk", when="+jar")
    # build error with +termlib, to be investigated
    depends_on("ncurses~termlib", when="+examples")
    depends_on("delphes", when="+examples")
    depends_on("readline", when="+examples")

    def cmake_args(self):
        args = [
            self.define("CMAKE_CXX_STANDARD", self.spec.variants["cxxstd"].value),
            self.define("BUILD_TESTING", self.run_tests),
            self.define_from_variant("BUILD_LCIO_EXAMPLES", "examples"),
            self.define_from_variant("BUILD_ROOTDICT", "rootdict"),
            self.define_from_variant("INSTALL_JAR", "jar"),
        ]
        return args

    def setup_run_environment(self, env):
        env.set("LCIO", self.prefix)
        env.prepend_path("PYTHONPATH", self.prefix.python)
        # needed for the python bindings to find "Exceptions.h"
        env.prepend_path("CPATH", self.prefix)

    @run_after("install")
    def install_source(self):
        # these files are needed for the python bindings and root to
        # find the headers
        if self.spec.version > Version("2.17"):
            # This has been fixed upstream
            return

        install_tree("src/cpp/include/pre-generated/", self.prefix.include + "/pre-generated")
        install("src/cpp/include/IOIMPL/LCEventLazyImpl.h", self.prefix.include + "/IOIMPL/")
        install("src/cpp/include/SIO/SIOHandlerMgr.h", self.prefix.include + "/SIO/")
        install("src/cpp/include/SIO/SIOObjectHandler.h", self.prefix.include + "/SIO/")
