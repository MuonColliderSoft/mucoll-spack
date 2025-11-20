# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Mybibutils(CMakePackage, MCIlcsoftpackage):
    """A collection of legacy BIB-related Processors used in some MAIA studies"""

    homepage = "https://github.com/madbaron/MyBIBUtils"
    git      = "https://github.com/madbaron/MyBIBUtils.git"
    url      = "https://github.com/madbaron/MyBIBUtils/archive/refs/tags/v0.1.tar.gz"

    maintainers = ['madbaron']

    version('main', branch='main')
    version("0.1", sha256="fa21f3dadbcb610e6c372f457e469488d5995c7c74744be3ccc544990b787caf", preferred=True)    

    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('root')

    def setup_run_environment(self, spack_env):
        spack_env.prepend_path('MARLIN_DLL', self.prefix.lib + "/libMyBIBUtils.so")

    def cmake_args(self):
        return [
            self.define('CMAKE_CXX_STANDARD',
                        self.spec['root'].variants['cxxstd'].value)
        ]
