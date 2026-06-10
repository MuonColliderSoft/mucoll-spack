from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyAtlasify(PythonPackage):
    """Atlasify library for plotting."""

    homepage = "https://gitlab.cern.ch/fsauerbu/atlasify"
    git = "https://gitlab.cern.ch/fsauerbu/atlasify.git"

    version('master', branch='master')

    depends_on("py-setuptools", type="build")
    depends_on("py-wheel", type="build")

    depends_on("py-matplotlib")
    depends_on("py-packaging")
