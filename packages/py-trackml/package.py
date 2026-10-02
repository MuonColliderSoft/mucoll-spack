from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyTrackml(PythonPackage):
    """TrackML utilities for loading, storing, and manipulating TrackML data."""

    homepage = "https://github.com/LAL/trackml-library"
    git = "https://github.com/LAL/trackml-library.git"

    license("MIT")

    version("master", branch="master")
    # Version 3 (phase-2 hit weights) was never tagged; it is the tip of master.
    version("3", commit="53a165e15a2c885f54c2bef1bd1ed53db6ed9648")
    version("2", tag="v2", commit="8e4bc0d5b2d0614836b2b7f6be8885bdb814b005")
    version("1", tag="v1", commit="568cc23b9167db4b37be5c5d8c96e4c67201caf0")

    depends_on("py-setuptools", type="build")

    with default_args(type=("build", "run")):
        depends_on("py-numpy")
        depends_on("py-pandas@0.21:", when="@3:")
        depends_on("py-pandas")
