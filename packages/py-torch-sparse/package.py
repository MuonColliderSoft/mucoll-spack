# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyTorchSparse(PythonPackage):
    """PyTorch Extension Library of Optimized Autograd Sparse Matrix
    Operations.

    This package consists of a small extension library of optimized sparse
    matrix operations with autograd support for PyTorch, including sparse
    coalescing, sparse-dense matrix multiplication (SpMM), sparse-sparse
    matrix multiplication (SpSpMM), and more.
    """

    homepage = "https://github.com/rusty1s/pytorch_sparse"
    pypi = "torch-sparse/torch_sparse-0.6.18.tar.gz"

    license("MIT")

    version("0.6.18", sha256="2f14c510a6e93f404c6ea357210615b3c15a71731f9dbd86f25434e34fb5a741")
    version("0.6.17", sha256="06e268dd77f73eb641da8f9383306d7afac6423383c9197b9df120955e2a96bd")
    version("0.6.16", sha256="7657cfdcac221fb92aa00af7e6032853a7d2cc0d58151d9436485094ab7635ac")
    version("0.6.15", sha256="3a741ae8a7cc19247a44de549fa4d593c4257b5f741e1eb5110b712a14209dd9")
    version("0.6.14", sha256="36632fa7b219a71d54a6bb245765379ab4d387a694f34ab429a9a9f70879ad66")
    version("0.6.13", sha256="b4896822559f9b47d8b0186d74c94b7449f91db155a57d617fbeae9b722fa1f3")
    version("0.6.12", sha256="85db85bd45855cde4be093c7e2413b962b21b31151ad7eacd19ca4e2808bced2")
    version("0.6.11", sha256="1d57bc0fc9d9b6cfdc9dcc12017dc371c89c901e5d7a73e6149c8b866eca1267")
    version("0.6.10", sha256="2e2c7a3649d04e19b3b3960c1d7fc0e767017c93587de1e0d6eb7fda613a6b82")
    version("0.6.9",  sha256="089a3200044d0d392a4d0d84803f926da28a44532fe30f4c8d6c34f567680db3")

    variant("cuda", default=False, description="Enable CUDA support")
    variant(
        "metis",
        default=False,
        description="Enable METIS support for graph partitioning",
    )

    depends_on("python@3.8:", type=("build", "run"))
    depends_on("py-setuptools", type="build")

    # torch must be present at setup.py execution time
    depends_on("py-torch+cuda", when="+cuda", type=("build", "run"))
    depends_on("py-torch~cuda", when="~cuda", type=("build", "run"))

    # torch-scatter is a required runtime dependency
    depends_on("py-torch-scatter", type=("build", "run"))

    # scipy is a persistent runtime dependency across all 0.6.x versions
    depends_on("py-scipy", type=("build", "run"))

    # Optional METIS support for graph partitioning (64-bit IDXTYPEWIDTH required)
    depends_on("metis+int64", when="+metis", type=("build", "run"))

    def setup_build_environment(self, env):
        if "+cuda" in self.spec:
            torch = self.spec["py-torch"]
            env.set(
                "TORCH_CUDA_ARCH_LIST",
                " ".join(
                    "{0:.1f}".format(float(a) / 10.0)
                    for a in torch.variants["cuda_arch"].value
                ),
            )
            env.set("FORCE_CUDA", "1")
        else:
            env.set("FORCE_CUDA", "0")

        if "+metis" in self.spec:
            env.set("WITH_METIS", "1")
        else:
            env.set("WITH_METIS", "0")