# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyClassResolver(PythonPackage):
    """Lookup and instantiate classes with style.

    class-resolver provides a small utility (ClassResolver) that lets you
    look up subclasses of a given base class by name and instantiate them
    with keyword arguments. It is widely used by libraries such as PyKEEN
    and PyTorch Geometric to make components selectable by string name.
    """

    homepage = "https://github.com/cthoyt/class-resolver"
    pypi = "class-resolver/class_resolver-0.7.1.tar.gz"
    git = "https://github.com/cthoyt/class-resolver.git"

    license("MIT")

    maintainers("cthoyt")

    # --- Versions -----------------------------------------------------------
    version("0.7.1", sha256="86f73b8cc5ed9111b7d9c5e331b51856a32f205179c66a56a9c520d0f6e82f66")
    version("0.7.0", sha256="1a20c3e140b608ec29b56cf85433ee85fac6d7aebedf39717d71a56bb564618e")
    version("0.6.1", sha256="b30a21b77f9be1d9542f069dc15efa8768f60357c7eb721e03c84037d229d531")
    version("0.6.0", sha256="8a3c20ab771925477f65cad8a49bb431e11543c82fbfadbf611c6769228a6cae")
    version("0.5.5", sha256="1301e0dd399716d337e6aae31d3959a632359a0db8fcad1f7dc6c42d9d0ee98b")
    version("0.5.4", sha256="e09dc2ea33712f1c2dd151671cb6dc8e68777be80c1136c9748eacb84f83d638")
    version("0.5.3", sha256="2c27b3494643a94c5f3989999c2583fea5c7361cad754109b1f0fa8571e7795f")
    version("0.5.2", sha256="f3641d51d13cb6ffb95201c0d9102d39a04876c22d34d05c12243af6aeba952e")
    version("0.5.1", sha256="cf259264c59a2cf520563a16c5ea01dfcd64b6293004a7a19f58474b1380ffe2")
    version("0.5.0", sha256="5a36d9a96a29e08e89767e409825540c117014d2e23896ab43172b8de8b225bc")
    version("0.4.3", sha256="18bb9983cb377f669e5900979de4aa65449d95ead61838fa12862958998c71a2")

    # --- Optional features (mirroring upstream "extras") --------------------
    variant("click",    default=False, description="Enable click CLI integration")
    variant("numpy",    default=False, description="Enable the numpy resolver helpers")
    variant("optuna",   default=False, description="Enable the optuna resolver helpers")
    variant("sklearn",  default=False, description="Enable the scikit-learn resolver helpers")
    variant("tabulate", default=False, description="Enable tabulate-based pretty-printing")
    variant("torch",    default=False, description="Enable the torch resolver helpers")

    # --- Python version requirements ----------------------------------------
    depends_on("python@3.10:", type=("build", "run"), when="@0.7:")
    depends_on("python@3.9:",  type=("build", "run"), when="@0.5:0.6")
    depends_on("python@3.7:",  type=("build", "run"), when="@0.4")

    # --- Build backend ------------------------------------------------------
    # 0.4.x – 0.5.x use setuptools; 0.6.x+ switched to uv_build.
    with when("@:0.5"):
        depends_on("py-setuptools", type="build")
        depends_on("py-wheel",      type="build")

    with when("@0.6:"):
        # uv_build is provided by the py-uv-build Spack package (the
        # PEP 517 build backend shipped with uv). If your Spack does not
        # have it yet, you can either add a recipe for it or pin
        # class-resolver to @:0.5.5.
        depends_on("py-uv-build@0.6.6:", type="build")

    # --- Runtime dependencies ----------------------------------------------
    # typing-extensions was introduced as a runtime dep in 0.5.0
    depends_on("py-typing-extensions", type=("build", "run"), when="@0.5:")

    # importlib-metadata is only needed when running on Python < 3.10
    # (used as a stdlib backport).
    depends_on(
        "py-importlib-metadata@3.7:",
        type=("build", "run"),
        when="@0.4:0.6 ^python@:3.9",
    )

    # --- Optional (variant-gated) dependencies -----------------------------
    depends_on("py-click@8.2:",      type=("build", "run"), when="+click @0.7:")
    depends_on("py-click",           type=("build", "run"), when="+click @:0.6")
    depends_on("py-numpy",           type=("build", "run"), when="+numpy")
    depends_on("py-optuna",          type=("build", "run"), when="+optuna")
    depends_on("py-scikit-learn",    type=("build", "run"), when="+sklearn")
    depends_on("py-tabulate",        type=("build", "run"), when="+tabulate")
    depends_on("py-torch",           type=("build", "run"), when="+torch")
