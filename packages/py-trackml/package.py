from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class Pytrackml(PythonPackage):
    """TrackML utilities for loading, storing, and manipulating TrackML data."""

    homepage = "https://github.com/LAL/trackml-library"
    git = "https://github.com/LAL/trackml-library.git"

    version('v2', branch='v2')

    depends_on("py-numpy")
    depends_on("py-pandas")
