from datetime import datetime

from spack.package import *
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack.pkg.k4.key4hep_stack import Key4hepPackage, install_setup_script


class MucollStack(BundlePackage, Key4hepPackage, CudaPackage):
    """Bundle package to install Muon Collider Software Stack"""

    homepage = "https://github.com/MuonColliderSoft"

    maintainers = ["madbaron"]

    ##################### versions ########################
    #######################################################
    ###  nightly build
    # dependency versions are set in environments/mucoll-common/packages.yaml
    version(datetime.today().strftime("%Y-%m-%d"))

    ### stable build
    version("3.1")

    # this bundle package installs a custom setup script,
    # so need to add the install phase
    # (normally doesn't exist for a bundle package)
    phases = ["install"]

    variant(
        "devtools",
        default=True,
        description="add tools necessary for software development to the stack",
    )
    variant(
        "build_type",
        default="Release",
        description="CMake build type",
        values=("Debug", "Release", "RelWithDebInfo", "MinSizeRel"),
    )
    variant("llvm", default=False, description="Build with LLVM")
    variant("ml", default=False, description="Build with machine learning tools")
    # 'cuda' and 'cuda_arch' variants come from CudaPackage
    # (cuda_arch must be given with +cuda, e.g. cuda_arch=80)
    variant("pytools", default=False, description="Build with python tools")
    variant(
        "sim",
        default=False,
        description="Build with reconstruction and simulation tools",
    )
    variant("gen", default=False, description="Build with generators")

    # Add compilers to the build dependencies
    # so that we have them available to set them in the env script
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")

    with default_args(type="run"):
        depends_on("cmake")
        depends_on("pelican")
        depends_on("ccache")
        depends_on("ninja")

    # Minimal build for analysis only
    depends_on("edm4hep")
    depends_on("podio")

    with when("+sim"):
        ############################### Key4hep ###############
        #######################################################
        depends_on("dd4hep")
        depends_on("delphes")
        depends_on("hepmc3")

        depends_on("k4geo")
        depends_on("k4reco")
        depends_on("k4gaudipandora")
        depends_on("k4actstracking")
        depends_on("k4simgeant4")
        depends_on("k4clue")

    with when("+gen"):
        depends_on("whizard +openloops")
        depends_on("madgraph5amc")
        depends_on("pythia8")

    # py-torch is pulled in by +ml and by +sim (k4actstracking+gnn).
    # spack's py-torch defaults to +cuda on Linux; only enable it with mucoll-stack+cuda
    with when("+cuda"):
        for arch in CudaPackage.cuda_arch_values:
            with when(f"cuda_arch={arch}"):
                depends_on(f"py-torch+cuda cuda_arch={arch}", when="+ml")
                depends_on(f"py-torch+cuda cuda_arch={arch}", when="+sim")
                depends_on(f"py-onnxruntime+cuda cuda_arch={arch}", when="+ml")
                depends_on(f"py-onnxruntime+cuda cuda_arch={arch}", when="+sim")
                depends_on(f"acts+cuda cuda_arch={arch}", when="+sim")
                # acts requires torch-scatter+cuda but does not forward cuda_arch
                depends_on(f"torch-scatter+cuda cuda_arch={arch}", when="+sim")
        depends_on("k4actstracking+cuda", when="+sim")
    depends_on("py-torch~cuda", when="~cuda+ml")
    depends_on("py-torch~cuda", when="~cuda+sim")

    ##################### developer tools #################
    #######################################################
    with when("+devtools"), default_args(type="run"):
        depends_on("doxygen")
        depends_on("gdb")

    depends_on("llvm", when="+llvm")

    with when("+ml"), default_args(type="run"):
        # ML tools
        depends_on("acorn")
        depends_on("py-onnxruntime")
        depends_on("py-onnx")
        depends_on("py-torch")
        depends_on("py-scikit-learn")
        depends_on("py-xgboost")

    with when("+pytools"), default_args(type="run"):
        # Python tools
        depends_on("py-h5py")
        depends_on("py-matplotlib")
        depends_on("py-pandas")
        depends_on("py-particle")
        depends_on("py-pip")
        depends_on("py-scipy")
        depends_on("py-uproot")

    def setup_run_environment(self, env: EnvironmentModifications) -> None:
        # set locale to avoid certain issues with xerces-c
        # (see https://github.com/key4hep/key4hep-spack/issues/170)
        env.set("LC_ALL", "C")
        env.set("MUCOLL_STACK", join_path(self.prefix, "setup.sh"))
        env.set("MUCOLL_RELEASE_VERSION", str(self.spec.version))

        # Set MUCOLL_GEO for backward compatibility; prefer the k4geo configuration directly.
        if "k4geo" in self.spec:
            env.set("MUCOLL_GEO", self.spec["k4geo"].prefix.share)
        if "k4actstracking" in self.spec:
            env.set("ACTSTRACKING_DATA", self.spec["k4actstracking"].prefix.share)

        # ROOT needs to be in LD_LIBRARY_PATH to find cxxmodules
        if "root" in self.spec:
            env.prepend_path("LD_LIBRARY_PATH", self.spec["root"].prefix.lib.root)

        # set vdt, needed for root, see https://github.com/spack/spack/pull/37278
        if "vdt" in self.spec:
            env.prepend_path("CPATH", self.spec["vdt"].prefix.include)
            # When building podio with +rntuple there are warnings constantly without this
            env.prepend_path("LD_LIBRARY_PATH", self.spec["vdt"].libs.directories[0])

        # py-torch's cmake_prefix_paths only reaches dependents' *build* environment;
        # users building against libtorch from the setup script need it here too.
        if "py-torch" in self.spec:
            for path in self["py-torch"].cmake_prefix_paths:
                env.prepend_path("CMAKE_PREFIX_PATH", path)

    def install(self, spec: Spec, prefix: Prefix) -> None:
        install_setup_script(self, spec, prefix, "MUCOLL_LATEST_SETUP_PATH")
