# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

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
    depends_on("node-js@20", type="build")
    depends_on("npm", type="build")

    # -----------------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------------

    # GoPackage builds from the module root by default.
    # Pelican's main package lives in ./cmd, so append it to the
    # go build arguments for this Spack Go builder implementation.
    @property
    def build_args(self):
        args = super().build_args
        args.append("./cmd")
        return args

    def setup_build_environment(self, env):
        super().setup_build_environment(env)
        # Embed version information the same way goreleaser does.
        version_pkg = "github.com/pelicanplatform/pelican/version"
        env.append_flags(
            "GOFLAGS",
            "-ldflags=-s -w"
        )
        # Disable CGO: the Pelican client binary is built with CGO_ENABLED=0
        # by upstream (see .goreleaser.yaml).
        env.set("CGO_ENABLED", "0")

    @run_before("build")
    def build_web_ui(self):
        metadata = "web_ui/frontend/public/data/parameters.json"
        mkdirp(os.path.dirname(metadata))
        with open(metadata, "w", encoding="utf-8") as f:
            # Keep frontend build working in source tarballs that omit generated metadata.
            f.write("[]\n")

        npm = which("npm", required=True)
        with working_dir("web_ui/frontend"):
            npm("ci")
            npm("run", "build")

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