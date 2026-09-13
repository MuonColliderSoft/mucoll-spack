# Overlay of the k4 (key4hep-spack) k4geo package, fixing the build with libc++.
#
# detectorSegmentations/src/FCCSWEndcapTurbine_k4geo.cpp uses std::numbers::pi
# without including <numbers>. libstdc++ happens to pull the header in
# transitively, so this builds on Linux, but libc++ (Apple clang on macOS) does
# not: "error: no member named 'numbers' in namespace 'std'".
#
# @main is a moving branch, so the include is inserted from patch() only when it
# is still missing, instead of shipping a .patch file that would stop applying
# as soon as upstream fixes it. Drop this overlay once k4geo includes <numbers>.

import os

from spack.pkg.k4.k4geo import K4geo as K4K4geo

from spack.package import *


class K4geo(K4K4geo):
    __doc__ = K4K4geo.__doc__

    def patch(self):
        super_patch = getattr(super(), "patch", None)
        if callable(super_patch):
            super_patch()

        source = "detectorSegmentations/src/FCCSWEndcapTurbine_k4geo.cpp"
        if not os.path.exists(source):
            return
        with open(source) as f:
            content = f.read()
        if "std::numbers" in content and "#include <numbers>" not in content:
            with open(source, "w") as f:
                f.write("#include <numbers>\n" + content)
