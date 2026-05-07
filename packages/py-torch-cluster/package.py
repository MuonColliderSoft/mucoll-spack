# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyTorchCluster(PythonPackage):
    """PyTorch Extension Library of Optimized Graph Cluster Algorithms.

    This package consists of a small extension library of highly optimized
    graph cluster algorithms for use in PyTorch, including FPS sampling,
    kNN, radius-graph, random walks, and more.
    """

    homepage = "https://github.com/rusty1s/pytorch_cluster"
    pypi = "torch-cluster/torch_cluster-1.6.3.tar.gz"

    license("MIT")

    version("1.6.3", sha256="78d5a930a5bbd0d8788df8c6d66addd68d6dd292fe3edb401e3dacba26308152")
    version("1.6.2", sha256="5d2024b38779e04d4e718d0c7f29b66b397bf90f16d66d86c0922f46f9da3a97")
    version("1.6.1", sha256="a760e0b4ba71b00d9d908bb6f834aa28f055783ee5af9aecc3f3f94853535f72")
    version("1.6.0", sha256="249c1bd8c33a887b22bf569a59d0868545804032123594dd8c76ba1885859c39")
    version("1.5.9", sha256="96209e9f3f073c8e7fe91fbf7dd2cdd8655622d14dfc95a7618b4893a658dca5")
    version("1.5.8", sha256="95c6e81e9c4a6235e1b2152ab917021d2060ad995199f6bd7fb39986d37310f0")
    version("1.5.7", sha256="71701d2f7f3e458ebe5904c982951349fdb60e6f1654e19c7e102a226e2de72e")

    variant("cuda", default=False, description="Enable CUDA support")

    # Python requirement raised to 3.8 in 1.6.x
    depends_on("python@3.8:", type=("build", "run"), when="@1.6:")
    depends_on("python@3.6:", type=("build", "run"), when="@:1.5")

    depends_on("py-setuptools", type="build")

    # torch is imported at setup time; must be present before build
    depends_on("py-torch+cuda", when="+cuda", type=("build", "run"))
    depends_on("py-torch~cuda", when="~cuda", type=("build", "run"))

    # scipy dropped as a runtime dep in 1.6.0 (knn/radius reimplemented with nanoflann)
    depends_on("py-scipy", type=("build", "run"), when="@:1.5")

    def setup_build_environment(self, env):
        if "+cuda" in self.spec:
            torch = self.spec["py-torch"]
            env.set("TORCH_CUDA_ARCH_LIST", " ".join(
                "{0:.1f}".format(float(a) / 10.0)
                for a in torch.variants["cuda_arch"].value
            ))
            env.set("FORCE_CUDA", "1")
        else:
            env.set("FORCE_CUDA", "0")