# Overlay of the k4 (key4hep-spack) k4actstracking package, fixing the data
# download on macOS.
#
# data/CMakeLists.txt fetches the detector/material files listed in
# data/file_list.txt at configure time by running data/download_files.sh, which
# downloads with wget. macOS ships curl but not wget, so every file fails
# ("Failed to download MuColl_v1.root"); the script's output is captured into a
# CMake variable and the result is never checked, so configure and build happily
# continue and the install phase is what finally dies:
#   file INSTALL cannot find ".../data/MuColl_v1.root"
# Pulling wget in as a build dependency is enough -- the files themselves are
# reachable, and macOS 26+ provides the md5sum the script verifies them with.
#
# Drop this overlay once the upstream script falls back to curl.

from spack.pkg.k4.k4actstracking import K4actstracking as K4K4actstracking

from spack.package import *


class K4actstracking(K4K4actstracking):
    __doc__ = K4K4actstracking.__doc__

    depends_on("wget", type="build")
