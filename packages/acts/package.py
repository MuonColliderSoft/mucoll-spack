# Overlay of the builtin acts package for macOS.
#
# Plugins/Gnn/CMakeLists.txt passes the GNU ld flag -Wl,-no-as-needed (to keep
# libtorchscatter linked), which Apple's ld rejects ("ld: unknown options:
# -no-as-needed"). Apple's ld never drops dylibs given on the command line
# unless -dead_strip_dylibs is used, so the flag is skipped there.

import os

from spack_repo.builtin.packages.acts.package import Acts as BuiltinActs

from spack.package import *


class Acts(BuiltinActs):
    __doc__ = BuiltinActs.__doc__

    def patch(self):
        gnn_cmake = join_path("Plugins", "Gnn", "CMakeLists.txt")
        if self.spec.satisfies("platform=darwin") and os.path.exists(gnn_cmake):
            filter_file(
                r'"-Wl,-no-as-needed"',
                r'"$<$<NOT:$<PLATFORM_ID:Darwin>>:-Wl,-no-as-needed>"',
                gnn_cmake,
                string=True,
            )
