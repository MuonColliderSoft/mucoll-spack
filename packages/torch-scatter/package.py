# Overlay of the builtin torch-scatter package (the C++ library acts+gnn links
# against), to build it as C++20.
#
# Recent py-torch headers (torch/all.h, ATen/ATen.h) refuse to compile below
# C++20 ("C++20 or later compatible compiler is required to use PyTorch"). The
# builtin recipe passes -DCMAKE_CXX_STANDARD=20, but upstream's CMakeLists.txt
# does `set(CMAKE_CXX_STANDARD 17)`, and that normal variable shadows the cache
# entry, so the build still runs with -std=gnu++17. Rewrite it before CMake runs.
# Drop once upstream (rusty1s/pytorch_scatter) or the builtin recipe handles it.

from spack_repo.builtin.packages.torch_scatter.package import (
    TorchScatter as BuiltinTorchScatter,
)

from spack.package import *


class TorchScatter(BuiltinTorchScatter):
    __doc__ = BuiltinTorchScatter.__doc__

    def patch(self):
        filter_file(
            r"set\(CMAKE_CXX_STANDARD 17\)",
            "set(CMAKE_CXX_STANDARD 20)",
            "CMakeLists.txt",
        )
