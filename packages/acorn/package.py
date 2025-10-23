from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class Acorn(PythonPackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://gitlab.cern.ch/gnn4itkteam/acorn"
    url = "https://gitlab.cern.ch/lbauckha/acorn.git"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    license("Apache-2.0")

    # FIXME: Add proper versions and checksums here.
    version("dev-lukas", branch="dev-lukas", preferred=True)

    depends_on("py-yaml")
