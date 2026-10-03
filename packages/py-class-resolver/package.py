from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyClassResolver(PythonPackage):
    """Lookup and instantiate classes with style."""

    homepage = "https://github.com/cthoyt/class-resolver"
    pypi = "class-resolver/class_resolver-0.8.2.tar.gz"
    git = "https://github.com/cthoyt/class-resolver.git"

    license("MIT")

    # 0.6.x (needs uv_build@:0.6) and 0.8.0 (needs uv_build@0.12.17:) are not
    # listed: no py-uv-build version satisfies them.
    version(
        "0.8.2",
        sha256="20dd9065acb2ccd790c932a0c2d7425c28dcaa6a572ebe607b606995f2e1e26a",
    )
    version(
        "0.8.1",
        sha256="eae529e7eb620973b13b88f36e198479e3b28dc8f0297ea0c8ecdc78d9a962b0",
    )
    version(
        "0.7.1",
        sha256="86f73b8cc5ed9111b7d9c5e331b51856a32f205179c66a56a9c520d0f6e82f66",
    )
    version(
        "0.7.0",
        sha256="1a20c3e140b608ec29b56cf85433ee85fac6d7aebedf39717d71a56bb564618e",
    )
    version(
        "0.5.5",
        sha256="1301e0dd399716d337e6aae31d3959a632359a0db8fcad1f7dc6c42d9d0ee98b",
    )
    version(
        "0.5.4",
        sha256="e09dc2ea33712f1c2dd151671cb6dc8e68777be80c1136c9748eacb84f83d638",
    )
    version(
        "0.4.3",
        sha256="18bb9983cb377f669e5900979de4aa65449d95ead61838fa12862958998c71a2",
    )

    # Optional extras, mirroring upstream's [project.optional-dependencies]
    variant("click", default=False, description="Enable click CLI integration")
    variant("numpy", default=False, description="Enable the numpy resolver helpers")
    variant("optuna", default=False, description="Enable the optuna resolver helpers")
    variant(
        "sklearn", default=False, description="Enable the scikit-learn resolver helpers"
    )
    variant(
        "tabulate", default=False, description="Enable tabulate-based pretty-printing"
    )
    variant("torch", default=False, description="Enable the torch resolver helpers")
    variant(
        "torch_geometric",
        default=False,
        description="Enable the torch-geometric resolver helpers",
    )

    with default_args(type=("build", "run")):
        depends_on("python@3.11:", when="@0.8:")
        depends_on("python@3.10:", when="@0.7:")
        depends_on("python@3.9:", when="@0.5:")
        depends_on("python@3.7:")

    with default_args(type="build"):
        depends_on("py-uv-build@0.11.2:0", when="@0.8.1:")
        depends_on("py-uv-build@0.6.6:0", when="@0.7")
        depends_on("py-setuptools", when="@:0.5")
        depends_on("py-wheel", when="@:0.5")

    with default_args(type=("build", "run")):
        depends_on("py-typing-extensions", when="@0.5:")
        depends_on("py-importlib-metadata@3.7:", when="@0.4:0.5 ^python@:3.9")

        depends_on("py-click@8.5:", when="@0.8:+click")
        depends_on("py-click@8.2:", when="@0.7+click")
        depends_on("py-click", when="+click")
        depends_on("py-numpy", when="+numpy")
        depends_on("py-optuna", when="+optuna")
        depends_on("py-scikit-learn", when="+sklearn")
        depends_on("py-tabulate", when="+tabulate")
        depends_on("py-torch", when="+torch")
        depends_on("py-torch", when="+torch_geometric")
        depends_on("py-torch-sparse", when="+torch_geometric")
        depends_on("py-torch-geometric", when="+torch_geometric")
