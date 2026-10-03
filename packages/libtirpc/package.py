# Overlay of the builtin libtirpc package, fixing the build with a C23 compiler.
#
# libtirpc 1.3.7 still uses K&R style function definitions, e.g. in
# src/bindresvport.c:
#
#     int
#     bindresvport(sd, sin)
#             int sd;
#             struct sockaddr_in *sin;
#
# C23 removed those, and apple-clang 21 defaults to C23: autoconf's AC_PROG_CC
# probe picks "-std=gnu23" and bakes it into CC, so the build dies with
# "unknown type name 'sd'" / "expected ';' after top level declarator".
#
# Pass -std=gnu17 through CFLAGS (build_system_flags), which automake places
# after CC's own flags, so the later -std wins. Disabling the probe with
# ac_cv_prog_cc_c23=no is not enough on its own: configure then reports C11 as
# "none needed" and leaves CC as plain clang, which still defaults to C23.
#
# libtirpc is only here because root+r pulls in R. Drop this overlay once
# libtirpc ships ANSI definitions (not yet in 1.3.7, the newest version spack
# packages) or spack handles the C23 default itself.

from spack_repo.builtin.packages.libtirpc.package import Libtirpc as BuiltinLibtirpc

from spack.package import *


class Libtirpc(BuiltinLibtirpc):
    __doc__ = BuiltinLibtirpc.__doc__

    def flag_handler(self, name, flags):
        if name == "cflags" and self.spec.satisfies("platform=darwin %c=apple-clang@21:"):
            flags.append("-std=gnu17")
            # None, None, flags -> hand them to configure as CFLAGS
            return (None, None, flags)
        return (flags, None, None)
