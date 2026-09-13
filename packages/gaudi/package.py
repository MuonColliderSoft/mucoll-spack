# Overlay of the builtin gaudi package, fixing the build on macOS.
#
# The genconf/confuserdb build steps import GaudiPluginService.cpluginsvc, which
# dlopen()s libGaudiPluginService by bare name and relies on the dynamic linker
# search path to find it. On macOS, System Integrity Protection strips
# DYLD_LIBRARY_PATH whenever a protected binary (/bin/sh, /usr/bin/env) is in the
# process chain -- which make and Gaudi's generated `run` wrapper always are --
# so the load fails: "dlopen(libGaudiPluginService.dylib) ... (no such file)".
#
# gaudi-pluginsvc-library-search.patch backports the library lookup from Gaudi
# master: search DYLD_LIBRARY_PATH/LD_LIBRARY_PATH explicitly and dlopen the
# absolute path. LD_LIBRARY_PATH is exported by the build's gaudienv.sh and is
# not stripped by SIP. Only the lookup is backported: master also renames the
# C API symbol the module calls, which 40.5 does not have.
#
# v40r6 still has the old lookup. Drop this overlay once a release with the fix
# is used.

from spack_repo.builtin.packages.gaudi.package import Gaudi as BuiltinGaudi

from spack.package import *


class Gaudi(BuiltinGaudi):
    __doc__ = BuiltinGaudi.__doc__

    patch("gaudi-pluginsvc-library-search.patch", when="@40.5")
