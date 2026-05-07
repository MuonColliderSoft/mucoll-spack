# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.go import GoPackage
from spack.package import *


class Pelican(GoPackage):
    """Pelican is an open-source platform for creating and operating data
    federations. It provides tools for publishing, discovering, and accessing
    distributed data across multiple storage systems using a common protocol.
    Pelican is the successor to StashCP and powers the Open Science Data
    Federation (OSDF)."""

    homepage = "https://docs.pelicanplatform.org"
    url = "https://github.com/PelicanPlatform/pelican/archive/refs/tags/v7.24.3.tar.gz"
    git = "https://github.com/PelicanPlatform/pelican.git"

    license("Apache-2.0")

    maintainers("turetske", "jhiemstrawisc", "joereuss12")

    version("7.24.3", sha256="fd73d4c9193f3a25d82c696e7269d10f84f4941786e957c8dffa1562d4b605a0")
    version("7.24.2", sha256="fbb92fc3d515317be7c6763f51061628d8a8140b758e3f8c253479b69208fa7d")
    version("7.23.3", sha256="e485038633aa03c149bcc76311f2f4a4d9d9e89faccd87a304377384f5f94930")

    # Pelican is a pure-Go binary; no C/C++ compiler needed at runtime.
    # The Go toolchain must be >= 1.21 (required by go.mod as of v7.x).
    depends_on("go@1.21:", type="build")

    # git is used by `go build` to resolve module replacements and for
    # the `develop` version fetched directly from the repository.
    depends_on("git", type="build")

    # -----------------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------------

    # GoPackage sets GOPATH, GOBIN, etc. automatically.
    # The default install() calls `go install ./...`, which is correct for
    # most Go projects.  Pelican's main entry point lives in ./cmd/pelican,
    # so we override build_targets / install_targets accordingly.

    build_targets = ["./cmd/pelican"]
    install_targets = ["./cmd/pelican"]

    def setup_build_environment(self, env):
        super().setup_build_environment(env)
        # Embed version information the same way goreleaser does.
        version_pkg = "github.com/pelicanplatform/pelican/version"
        env.append_flags(
            "GOFLAGS",
            "-ldflags=-s -w"
            f" -X {version_pkg}.version={self.spec.version}"
            " -X github.com/pelicanplatform/pelican/version.builtBy=spack",
        )
        # Disable CGO: the Pelican client binary is built with CGO_ENABLED=0
        # by upstream (see .goreleaser.yaml).
        env.set("CGO_ENABLED", "0")

    # -----------------------------------------------------------------------
    # Tests (run with `spack test run pelican`)
    # -----------------------------------------------------------------------

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        pelican = which(self.prefix.bin.pelican)
        out = pelican("--version", output=str, error=str)
        assert str(self.spec.version) in out, (
            f"pelican --version output does not contain {self.spec.version}:\n{out}"
        )