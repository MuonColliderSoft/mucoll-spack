# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyTorchSplineConv(PythonPackage):
    """PyTorch implementation of the spline-based convolution operator of
    SplineCNN.

    This package implements the Spline-Based Convolution Operator of SplineCNN,
    as described in: Matthias Fey, Jan Eric Lenssen, Frank Weichert, Heinrich
    Müller: SplineCNN: Fast Geometric Deep Learning with Continuous B-Spline
    Kernels (CVPR 2018). The operator works on all floating point data types
    and is implemented for both CPU and GPU.
    """

    homepage = "https://github.com/rusty1s/pytorch_spline_conv"
    pypi = "torch-spline-conv/torch_spline_conv-1.2.2.tar.gz"

    license("MIT")

    version("1.2.2", sha256="ed45a81da29f774665dbdd4709d7e534cdf16d2e7006dbd06957f35bd09661b2")
    version("1.2.1", sha256="364f658e0ecb4c5263a728c2961553e022fc44c11a633d5a1bf986cf169ab438")
    version("1.2.0", sha256="b7a1788004f6c6143d47040f2dd7d8a579a0c69a0cb0b5d7537416bf37c082a5")
    version("1.1.1", sha256="622e2f3763e41044f6364ff7a4c6a417cb73c7e6a6edec763abd14847863ebd2")
    version("1.1.0", sha256="e6029526205d1f7cb535389bebd81decf0649a20ea6a67688c02bd335a7f9339")

    variant("cuda", default=False, description="Enable CUDA support")

    depends_on("python@3.7:", type=("build", "run"))
    depends_on("py-setuptools", type="build")
    depends_on("py-pybind11")

    # torch must be present at setup.py execution time
    depends_on("py-torch+cuda", when="+cuda", type=("build", "run"))
    depends_on("py-torch~cuda", when="~cuda", type=("build", "run"))

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