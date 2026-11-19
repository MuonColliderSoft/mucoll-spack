# Overlay of the key4hep-spack (k4 namespace) k4fwcore package, adding a
# version that builds the upstream fix_inconsistent_overlay_tof_correction
# branch of k4FWCore:
#   https://github.com/key4hep/k4FWCore/tree/fix_inconsistent_overlay_tof_correction
#
# The version is named "main-tof-fix" rather than after the branch: a name
# starting with "main" sorts above every numbered release (like @main does), so
# it still satisfies the k4fwcore@1.6: / @1.7: constraints of the k4 recipes
# that depend on it (k4reco, k4simgeant4, k4reccalorimeter, ...). A plain
# alphabetic name would sort below 0 and break those constraints.
#
# environments/mucoll-common/packages.yaml selects it with @=main-tof-fix.
# Drop this overlay (and go back to @main) once the branch is merged upstream.

from spack.package import *
from spack.pkg.k4.k4fwcore import K4fwcore as K4K4fwcore


class K4fwcore(K4K4fwcore):
    __doc__ = K4K4fwcore.__doc__

    version("main-tof-fix", branch="fix_inconsistent_overlay_tof_correction")
