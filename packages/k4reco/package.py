import os

from spack.package import *
from spack.pkg.k4.key4hep_stack import Key4hepPackage


class K4reco(CMakePackage, Key4hepPackage):
    """Reconstruction algorithms using Gaudi in native key4hep"""

    homepage = "https://github.com/MuonColliderSoft/k4Reco"
    url = "https://github.com/MuonColliderSoft/k4Reco/archive/v00-01-00.tar.gz"
    git = "https://github.com/MuonColliderSoft/k4Reco.git"

    version("main", branch="last-bits")
    version(
        "0.3",
        sha256="59584e758c8f73838495f8411b3d6da22b05dd0244623e7d74f77ff221100004",
        preferred=True,
    )
    version(
        "0.2", sha256="a5b02425b6970777f9f2982fd2907d38599c00996d24ff0be839a0e315509cd4"
    )
    version(
        "0.1", sha256="b0fa2c7decfa140159e09e271074ba03ba49eeccfcbb2bfb1c464e719d8373c3"
    )

    variant("conformal_tracking", default=True, description="Build Conformal Tracking")

    depends_on("podio")
    depends_on("dd4hep")
    depends_on("edm4hep")
    depends_on("gaudi")
    depends_on("k4fwcore")
    depends_on("k4geo")
    depends_on("root")
    depends_on("fastjet")

    # The branch built as @main (last-bits) added find_package(k4SimGeant4 REQUIRED)
    # to the top-level CMakeLists.txt; without the dependency the configure step
    # fails with "Could not find a package configuration file provided by
    # k4SimGeant4". The tagged releases do not need it.
    depends_on("k4simgeant4", when="@main")
    # ...and its cmake/FindFastJet.cmake additionally requires the fastjet
    # contribs (fastjet/contrib/ValenciaPlugin.hh plus the fastjetcontribfragile
    # library), which the fastjet package does not install; without fjcontrib the
    # configure step fails with "Could NOT find FastJet (missing:
    # FASTJET_CONTRIB_INCLUDE_DIR FASTJETCONTRIB_LIBRARY)". The FindFastJet.cmake
    # of the tagged releases does not look for the contribs.
    depends_on("fjcontrib", when="@main")

    depends_on("lcio", when="+conformal_tracking")
    depends_on("ilcutil", when="+conformal_tracking")
    depends_on("kaltest", when="+conformal_tracking")
    depends_on("ddkaltest", when="+conformal_tracking")

    def patch(self):
        # CaloDigi/src/CalorimeterHitType.cc defines caloIDFromString() and friends
        # used by RealisticCaloDigi.cc, but it is missing from the k4RecoPlugins
        # source list. Linux links modules with undefined symbols, so this goes
        # unnoticed there; macOS refuses to link the bundle
        # ("Undefined symbols ... caloIDFromString").
        cml = join_path("k4Reco", "CMakeLists.txt")
        hit_type = join_path("k4Reco", "CaloDigi", "src", "CalorimeterHitType.cc")
        if os.path.exists(hit_type) and "CalorimeterHitType.cc" not in open(cml).read():
            filter_file(
                r"^(\s*)CaloDigi/src/RealisticCaloDigi\.cc$",
                r"\1CaloDigi/src/RealisticCaloDigi.cc CaloDigi/src/CalorimeterHitType.cc",
                cml,
            )

    def cmake_args(self):
        args = [
            self.define(
                "CMAKE_CXX_STANDARD", self.spec["root"].variants["cxxstd"].value
            ),
            self.define_from_variant("BUILD_TRACKING", "conformal_tracking"),
        ]
        return args

    def setup_run_environment(self, env):
        env.prepend_path("PYTHONPATH", self.prefix.python)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4reco"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["k4reco"].prefix.lib64)
