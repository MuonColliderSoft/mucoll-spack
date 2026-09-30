# Overlay of the builtin range-v3 package, fixing its headers with recent Apple Clang.
#
# meta/meta.hpp forward-declares std::allocator, std::vector, std::map, ... when
# compiled with Apple Clang (__apple_build_version__). The libc++ shipped with
# the macOS 27 SDK declares these differently, so every includer fails with
# "redefinition of 'allocator' as different kind of symbol" (seen building
# gaudi@40.2). The block is purely an Apple/old-clang extra: it only adds
# meta::quote specializations for std containers, and GCC and current LLVM
# clang never compile it. Drop the Apple Clang condition so Apple Clang takes
# the same path as every other compiler.
#
# Drop this overlay once range-v3 no longer forward-declares std on Apple Clang.

from spack_repo.builtin.packages.range_v3.package import RangeV3 as BuiltinRangeV3

from spack.package import *


class RangeV3(BuiltinRangeV3):
    __doc__ = BuiltinRangeV3.__doc__

    def patch(self):
        super().patch()
        if self.spec.satisfies("@0.12.0"):
            filter_file(
                r"^#if defined\(__apple_build_version__\) \|\| "
                r"\(defined\(__clang__\) && __clang_major__ < 6\)$",
                "#if !defined(__apple_build_version__) && defined(__clang__) && __clang_major__ < 6",
                "include/meta/meta.hpp",
            )
