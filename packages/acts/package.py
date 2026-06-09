# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.builtin.acts import Acts as BuiltinActs

from spack.package import *


class Acts(BuiltinActs):
    """Override of the builtin acts package that applies a verification patch
    for the CylindricalSpacePointGrid fill-path regression on acts@main.

    acts@main currently fails to compile downstream code that instantiates
    CylindricalSpacePointGridCreator::fillGrid (e.g. k4actstracking seeding):
    the post-fill sorting loop calls grid.atPosition(binIndex) with a
    std::size_t global-bin index, which after acts-project/acts#5541 resolves
    to the position-lookup overload and subscripts a scalar in
    MultiAxisHelper ("subscripted value is neither array nor pointer").

    The patch changes that call to grid.at(binIndex), matching the global-bin
    accessor used a few lines above. Remove this override once the fix lands
    upstream in acts main.
    """

    patch(
        "cylindrical_grid_atposition.patch",
        sha256="4d7c2730148ca629da8d0fb336e21309f8bc117eaf6eeb7086dba25ff03eb5fb",
        when="@main",
    )
