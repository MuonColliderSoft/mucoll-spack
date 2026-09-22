# Overlay of the builtin llvm package, so LLVM can be built inside the stack
# on the free GitHub runners (4 cores, 16 GB RAM, 6 h job limit) instead of
# being taken from the system as an external.
#
# The builtin package already exposes most of the knobs needed for a slim
# build as variants (see the llvm entry in environments/mucoll-common/
# packages.yaml), but two expensive parts are hard-wired whenever +clang is
# on and one resource setting is not exposed at all:
#
# 1. clang-tools-extra (clangd, clang-tidy, clang-include-fixer, ...) is always
#    added to LLVM_ENABLE_PROJECTS. It is a large chunk of the clang build and
#    nothing in the stack uses it. Exposed as the `clang_tools_extra` variant.
#
# 2. The clang static analyzer (and ARCMigrate, which cannot be enabled
#    without it on llvm@:20) is always built. Exposed as the `static_analyzer`
#    variant. clang-tidy needs it, hence the conflict below.
#
# 3. Link jobs run at the full build parallelism. Statically linking clang,
#    lld and the LLVM tools with GNU ld is memory hungry, and several of them
#    at once is what OOM-kills the build on the runners. LLVM_PARALLEL_LINK_JOBS
#    (honoured by the Ninja generator the builtin package uses) serialises the
#    links without slowing down compilation. Tests and benchmarks, which are
#    never installed, are also dropped from the build.
#
# Both variants default to the upstream behaviour, so they change nothing unless
# packages.yaml asks for them. The stack currently builds llvm ~clang, so only
# the link-job cap and the tests/benchmarks switches (3.) are in effect; the
# variants are there for when clang is turned back on.

from spack_repo.builtin.packages.llvm.package import Llvm as BuiltinLlvm

from spack.package import *


class Llvm(BuiltinLlvm):
    __doc__ = BuiltinLlvm.__doc__

    variant(
        "clang_tools_extra",
        default=True,
        when="+clang",
        description="Build clang-tools-extra (clangd, clang-tidy, ...)",
    )
    variant(
        "static_analyzer",
        default=True,
        when="+clang",
        description="Build the clang static analyzer (and ARCMigrate on llvm@:20)",
    )
    conflicts("~static_analyzer", when="+clang_tools_extra")
    conflicts("~static_analyzer", when="+z3")

    def cmake_args(self):
        args = super().cmake_args()
        define = self.define

        if self.spec.satisfies("~clang_tools_extra"):
            prefix = "-DLLVM_ENABLE_PROJECTS:"
            for i, arg in enumerate(args):
                if arg.startswith(prefix):
                    projects = arg.partition("=")[2].split(";")
                    projects = [p for p in projects if p and p != "clang-tools-extra"]
                    args[i] = define("LLVM_ENABLE_PROJECTS", projects)

        if self.spec.satisfies("~static_analyzer"):
            args.extend(
                [
                    define("CLANG_ENABLE_STATIC_ANALYZER", False),
                    define("CLANG_ENABLE_ARCMT", False),
                ]
            )

        args.extend(
            [
                define("LLVM_PARALLEL_LINK_JOBS", 1),
                define("LLVM_INCLUDE_TESTS", False),
                define("LLVM_INCLUDE_BENCHMARKS", False),
                define("LLVM_INCLUDE_EXAMPLES", False),
            ]
        )
        return args
