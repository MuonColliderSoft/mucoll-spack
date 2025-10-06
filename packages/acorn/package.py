from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class Acorn(PythonPackage):
    """Framework used for developing, testing and presenting the GNN-based 
    ITk track reconstruction project GNN4ITk."""

    homepage = "https://gitlab.cern.ch/gnn4itkteam/acorn"
    git = "https://gitlab.cern.ch/lbauckha/acorn.git"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    license("Apache-2.0")

    # FIXME: Add proper versions and checksums here.
    version('dev-lukas', branch='dev-lukas')

    depends_on("py-setuptools")
    depends_on("py-click")
    depends_on("py-numba")
    depends_on("py-tqdm")
    depends_on("py-networkx")
    depends_on("py-seaborn")
    depends_on("py-pyyaml")
    #depends_on("py-ipykernel")
    depends_on("py-lightning@2.4.0")
    depends_on("py-torch-geometric")
    #depends_on("py-pytest")
    #depends_on("py-pytest-cov")
    depends_on("py-uproot")
    depends_on("py-numpy")
    depends_on("py-scikit-learn")
    #depends_on("py-black")