from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyAtlasify(PythonPackage):
    """Applies the ATLAS style to matplotlib plots."""

    homepage = "https://gitlab.cern.ch/fsauerbu/atlasify"
    pypi = "atlasify/atlasify-0.8.0.tar.gz"
    git = "https://gitlab.cern.ch/fsauerbu/atlasify.git"

    license("AGPL-3.0-only")

    version("master", branch="master")
    version(
        "0.8.0",
        sha256="4623c23c2795fc2e457550783712b390e3626f8ee64309fbe4d53d8c02d93105",
    )
    version(
        "0.7.3",
        sha256="44685143071e4a094f7e62fce55dcd9fe709ede4b557ea808a3027471bdbb67d",
    )
    version(
        "0.7.2",
        sha256="5acccbf3a51fc20a02940875d4cdce912c3baea8636e6ab725fe06f1774f4b1f",
    )
    version(
        "0.7.1",
        sha256="9ed14d0a8c5beff9187c4642ee3d628d38422b661bfdba3ec25256f6bffa952a",
    )
    version(
        "0.7.0",
        sha256="0b665a91f01d9a5999db9ac7ce9f506e781504700999b38cceff33b36c9514a1",
    )
    version(
        "0.6.1",
        sha256="77a277f6a8e9a568519bf1869bbd91932660f860de197ed98a9f607503e88a20",
    )
    version(
        "0.6.0",
        sha256="a06eb04281061e5f51316638c7cea9adf64d0a278ca1f2f48f94738b6efe9eeb",
    )
    version(
        "0.5.0",
        sha256="c4ac5763a77ef7b5d71330d280090b6670b55e785337904f7463ae65b624adc0",
    )

    depends_on("py-setuptools", type="build")

    with default_args(type=("build", "run")):
        depends_on("py-matplotlib")
        depends_on("py-packaging")
