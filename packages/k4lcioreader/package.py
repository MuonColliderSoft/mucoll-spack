from spack.pkg.k4.key4hep_stack import Key4hepPackage


class K4lcioreader(CMakePackage, Key4hepPackage):
    """LCIO reader based on PODIO and EDM4hep"""

    homepage = "https://github.com/madbaron/k4LCIOReader"
    url = "https://github.com/madbaron/k4LCIOReader/archive/v0.1.0.tar.gz"
    git = "https://github.com/madbaron/k4LCIOReader.git"

    maintainers = ["madbaron"]

    version("master", branch="master")

    depends_on("lcio")
    depends_on("podio@0.12:")
    depends_on("edm4hep")
    depends_on("edm4hep@0.5:", when="@0.4.2:")
    depends_on("edm4hep@0.8:", when="@0.5:")
    depends_on("k4fwcore@0.3.0:", when="@0.4:")
    depends_on("root")

    def cmake_args(self):
        args = []
        args.append(
            "-DCMAKE_CXX_STANDARD=%s" % self.spec["root"].variants["cxxstd"].value
        )
        return args
