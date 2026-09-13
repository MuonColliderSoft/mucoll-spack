# Overlay of the builtin delphes package, fixing the bundled FastJet with libc++.
#
# Delphes 3.5.0 bundles a FastJet whose internal/ClosestPair2D.hh declares
# `std::vector<Point> _points` while ClosestPair2D::Point is still an incomplete
# type (it is only defined after the enclosing class). Recent libc++ (Apple
# clang 21) rejects this: "arithmetic on a pointer to an incomplete type
# 'fastjet::ClosestPair2D::Point'".
#
# fastjet-closestpair2d-libcxx.patch moves the Point definition inside the class,
# ahead of the containers that hold it -- the same layout upstream FastJet and
# Delphes master use -- without pulling in the newer header's FASTJET_WINDLL
# macro, which 3.5.0's bundled FastJet does not define.
#
# delphes-libcxx-removed-apis.patch fixes two more spots libc++ rejects, both
# taken verbatim from Delphes master:
#   - external/PUPPI/puppiParticle.hh derives from std::binary_function, which
#     was removed in C++17 (libstdc++ still ships it, libc++ does not);
#   - D0RunIICone/ProtoJet.hpp prints a nonexistent member `this->_Et`; GCC never
#     checks the uninstantiated template body, clang does.
#
# Drop this overlay once a Delphes release newer than 3.5.0 is used.

from spack_repo.builtin.packages.delphes.package import Delphes as BuiltinDelphes

from spack.package import *


class Delphes(BuiltinDelphes):
    __doc__ = BuiltinDelphes.__doc__

    patch("fastjet-closestpair2d-libcxx.patch", when="@3.5.0")
    patch("delphes-libcxx-removed-apis.patch", when="@3.5.0")
