# Overlay of the builtin dd4hep package, fixing plugin loading on macOS.
#
# DD4hep's plugin manager (libDD4hepGaudiPluginMgr) searched for ".components"
# files only in DYLD_LIBRARY_PATH on macOS, and dlopen()ed the plugin libraries
# by bare name, which dyld also resolves through DYLD_LIBRARY_PATH. System
# Integrity Protection strips DYLD_LIBRARY_PATH whenever a protected binary
# (/bin/sh, /usr/bin/env) is in the process chain -- e.g. k4run, which starts
# with "#!/usr/bin/env python" -- so GeoSvc could not load any DD4hep plugin:
# "Failed to locate plugin to interpret files of type lccdd".
#
# dd4hep-macos-plugin-search-path.patch additionally searches DD4HEP_LIBRARY_PATH
# and LD_LIBRARY_PATH (neither stripped by SIP), and dlopen()s a library that
# sits next to its ".components" file by its full path. DD4HEP_LIBRARY_PATH is set
# by the mucoll-stack setup script. Submitted upstream from
# github.com/madbaron/DD4hep, branch macos-plugin-search-path. Drop this overlay
# once a release with the fix is used.

from spack_repo.builtin.packages.dd4hep.package import Dd4hep as BuiltinDd4hep

from spack.package import *


class Dd4hep(BuiltinDd4hep):
    __doc__ = BuiltinDd4hep.__doc__

    patch("dd4hep-macos-plugin-search-path.patch", when="@1.37 platform=darwin")
