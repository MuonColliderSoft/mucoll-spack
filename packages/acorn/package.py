import re

from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class Acorn(PythonPackage, CudaPackage):
    """Framework used for developing, testing and presenting the GNN-based
    ITk track reconstruction project GNN4ITk."""

    homepage = "https://gitlab.cern.ch/gnn4itkteam/acorn"
    git = "https://gitlab.cern.ch/gnn4itkteam/acorn.git"

    license("Apache-2.0")

    # Default branch upstream is 'dev'. Named 'develop' so spack treats it as
    # newer than every tagged release (a plain 'dev' would sort below 1.0.0).
    version("develop", branch="dev")

    # The model_store submodule is ssh-only and is not fetched.
    version("2.0.1", tag="2.0.1", commit="353c6370db22ee1efe5a52531cd10f473c59f266")
    version("2.0.0", tag="2.0.0", commit="0145a7054196237819fd7d8b07af19637bf8da79")
    version("1.2.0", tag="1.2.0", commit="8582ba06adc18679d407d438fefbd1e6720639fe")
    version("1.1.0", tag="1.1.0", commit="3d2c0727b4473b7d1c79933627e0316e855dbe9e")
    version("1.0.0", tag="1.0.0", commit="de637a2fec66ff554bad29e503d57cd488784200")

    conflicts("+cuda", when="@:2.0.1", msg="acorn CUDA extensions are only available on develop")
    variant("wandb", default=False, description="Enable Weights & Biases logging")

    depends_on("py-setuptools@42:", type="build")
    depends_on("py-wheel", type="build")

    with default_args(type=("build", "run")):
        depends_on("py-click")
        depends_on("py-tqdm")
        depends_on("py-networkx")
        depends_on("py-seaborn")
        depends_on("py-matplotlib")
        depends_on("py-pyyaml")
        depends_on("py-numpy")
        depends_on("py-scipy")
        depends_on("py-pandas")
        depends_on("py-scikit-learn")
        depends_on("py-uproot")
        depends_on("py-trackml")
        depends_on("py-atlasify")
        depends_on("py-class-resolver")
        depends_on("py-torch")
        depends_on("py-torch-geometric")
        depends_on("py-torch-scatter")

        # acorn imports 'pytorch_lightning' (not 'lightning')
        depends_on("py-pytorch-lightning@1.8.6", when="@1.0.0")
        depends_on("py-pytorch-lightning@2:", when="@1.1.0:")

        depends_on("py-numba", when="@2.0.0:")

        depends_on("py-torchmetrics", when="@2.0.2:")
        depends_on("py-polars", when="@2.0.2:")
        depends_on("py-pyarrow", when="@2.0.2:")

        depends_on("py-wandb", when="+wandb")

    with when("+cuda"):
        depends_on("c", type="build")
        depends_on("cxx", type="build")
        # The extensions are built against torch's C++ API
        depends_on("py-torch+cuda", type=("build", "link", "run"))
        for arch in CudaPackage.cuda_arch_values:
            depends_on(f"py-torch+cuda cuda_arch={arch}", when=f"cuda_arch={arch}")

    depends_on("py-pytest", type="test")
    depends_on("py-pytest-cov", type="test")

    def setup_build_environment(self, env):
        if self.spec.satisfies("+cuda"):
            env.set("ACORN_BUILD_CUDA_EXT", "1")
            archs = [a for a in self.spec.variants["cuda_arch"].value if a != "none"]
            if archs:
                env.set(
                    "TORCH_CUDA_ARCH_LIST",
                    ";".join(re.sub(r"(\d)([a-z]*)$", r".\1\2", a) for a in archs),
                )
