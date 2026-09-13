# Overlay of the builtin py-torch package, fixing torch on macOS.
#
# py-torch@2.13 installs libtorch_cpu.dylib with `@loader_path` in LC_RPATH
# twice. Recent dyld/ld on macOS reject a Mach-O with duplicate LC_RPATH
# entries, so `import torch` fails ("Library not loaded: @rpath/libtorch_cpu.dylib")
# and anything linking against libtorch_cpu (e.g. torch-scatter) fails with
# "ld: duplicate LC_RPATH '@loader_path'". The builtin macos_rpath.patch that
# avoided this is gated to @2.7:2.12 and no longer applies to 2.13's setup.py.
#
# Rather than chase which of torch's CMake rpath settings adds the second entry,
# drop duplicate LC_RPATH entries from every installed Mach-O after install and
# ad-hoc re-sign the files that were touched (editing load commands invalidates
# the signature, which arm64 macOS enforces at load time).
#
# Drop this overlay once the builtin package handles the duplicate for 2.13+.

import os
import re

from spack_repo.builtin.packages.py_torch.package import PyTorch as BuiltinPyTorch

from spack.package import *


class PyTorch(BuiltinPyTorch):
    __doc__ = BuiltinPyTorch.__doc__

    @run_after("install", when="platform=darwin")
    def remove_duplicate_rpaths(self):
        otool = which("otool", required=True)
        install_name_tool = which("install_name_tool", required=True)
        codesign = which("codesign", required=True)
        rpath_re = re.compile(r"cmd LC_RPATH\n\s+cmdsize \d+\n\s+path (.+?) \(offset \d+\)")

        for root, _, files in os.walk(self.prefix):
            for name in files:
                path = os.path.join(root, name)
                if not name.endswith((".dylib", ".so")) or os.path.islink(path):
                    continue
                rpaths = rpath_re.findall(otool("-l", path, output=str, error=str))
                duplicates = [p for p in set(rpaths) for _ in range(rpaths.count(p) - 1)]
                if not duplicates:
                    continue
                for rpath in duplicates:
                    # removes one occurrence per call
                    install_name_tool("-delete_rpath", rpath, path)
                codesign("-f", "-s", "-", path)
