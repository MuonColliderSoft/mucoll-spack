# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.pkg.k4.k4marlinwrapper import K4marlinwrapper as K4mwBase


class K4marlinwrapper(K4mwBase):
    """MuColl overlay of the key4hep/k4MarlinWrapper recipe.

    TEMPORARY: redirects the ``@main`` version at a fork branch under test
    (madbaron/k4MarlinWrapper@fix-pidmeta-equality-comparable) instead of
    upstream key4hep/k4MarlinWrapper@main. This carries the fix for storing
    edm4hep::utils::ParticleIDMeta via the MetadataSvc, which fails to build
    against the current k4fwcore@main (putParameter now requires
    std::equality_comparable<T>, which ParticleIDMeta does not satisfy).

    The fork branch is based on upstream main, so ``@main`` keeps its usual
    "newest" version ordering and all version-gated depends_on constraints
    inherited from the base recipe still resolve correctly.

    Remove this whole overlay (packages/k4marlinwrapper/) once the fix is
    merged upstream so the stack tracks key4hep/k4MarlinWrapper@main again.
    """

    git = "https://github.com/madbaron/k4MarlinWrapper.git"

    version("main", branch="fix-pidmeta-equality-comparable")
