# Overlay of the k4 (key4hep-spack) k4reccalorimeter package, fixing the build on macOS.
#
# RecCaloCommon/IDMap.h constrains its constructors with
# std::result_of_t<VALFUNC(size_t)>. std::result_of was removed in C++20;
# libstdc++ (Linux) still provides it, but libc++ (Apple clang) does not, so the
# build fails with "no member named 'result_of_t' in namespace 'std'".
#
# Replace it with the C++17 equivalent std::invoke_result_t<VALFUNC, size_t>.
# filter_file instead of a patch file, so it keeps working as @main moves.
# Drop this overlay once upstream stops using std::result_of.

from spack.pkg.k4.k4reccalorimeter import K4reccalorimeter as K4K4reccalorimeter

from spack.package import *


class K4reccalorimeter(K4K4reccalorimeter):
    __doc__ = K4K4reccalorimeter.__doc__

    @run_before("cmake")
    def replace_result_of(self):
        filter_file(
            r"std::result_of_t<(\w+)\(size_t\)>",
            r"std::invoke_result_t<\1, size_t>",
            "RecCaloCommon/include/RecCaloCommon/IDMap.h",
            ignore_absent=True,
        )
