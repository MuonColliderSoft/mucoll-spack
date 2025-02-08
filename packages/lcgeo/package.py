# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.mucoll.mucoll_stack import MCIlcsoftpackage
from spack.package import *

class Lcgeo(CMakePackage, MCIlcsoftpackage):
    """DD4hep geometry models for future colliders."""

    homepage = "https://github.com/MuonColliderSoft/lcgeo"
    git      = "https://github.com/MuonColliderSoft/lcgeo.git"
    url      = "https://github.com/MuonColliderSoft/lcgeo/archive/refs/tags/v00-17-MC.tar.gz"

    generator = 'Ninja'

    maintainers = ['gianelle', 'pandreetto']

    version('master',  branch='master')
    version('0.20', sha256='7afdb3ad06b577481ca17003981b2dc8182d5c49ac032a3ee20ae545d97695e1', preferred=True)
    version("0.18.1",  sha256="5fcfcbd6110792bb607aba82a8dcbf887b40065aa12835f720af700f26c53bcc")
    version("0.18",    sha256="271062288aac419ce6affc98e199c597c340be57830c30f3b3e1d774cccc608b")
    version('0.17',    sha256='5ab33aaf5bc37deba82c2dde78cdce6c0041257222ed7ea052ecdd388a41cf9b')
    version('0.16.8',  sha256='03417825f5bf242e0cd3ba24f7b4e7c3030126bcbb961f6d2e045e3d9404abfe')
    version('0.16.7',  sha256='8090819e1e35b0e5f439bcf1cd0940bb861ac2bbba7a2d2a19858ed9fa5c6ccb')
    version('0.16.6',  sha256='d03977f5d3f20e885e2183e63eaeed612b6c8df168ff08140ac9fa105b1b07ed')

    variant('cxxstd',
            default='17',
            values=('14', '17'),
            multi=False,
            description='Use the specified C++ standard when building.')

    depends_on('lcio')
    depends_on('dd4hep')
    depends_on('lcio')
    depends_on('boost')
    depends_on('root')
    depends_on('python', type='build')
    depends_on('ninja', type='build')

    def cmake_args(self):
        args = []  
        args.append(self.define_from_variant('CMAKE_CXX_STANDARD', 'cxxstd'))
        args.append(self.define('BUILD_TESTING', self.run_tests))
        return args

    @run_after('install')
    def install_compact(self):
        install_tree('CaloTB', self.prefix.share.lcgeo.compact.CaloTB)
        install_tree('CLIC', self.prefix.share.lcgeo.compact.CLIC)
        install_tree('FCalTB', self.prefix.share.lcgeo.compact.FCalTB)
        install_tree('FCCee', self.prefix.share.lcgeo.compact.FCCee)
        install_tree('fieldmaps', self.prefix.share.lcgeo.compact.fieldmaps)
        install_tree('ILD', self.prefix.share.lcgeo.compact.ILD)
        install_tree('SiD', self.prefix.share.lcgeo.compact.Sid)
        install_tree('MuColl', self.prefix.share.lcgeo.compact.MuColl)

    def setup_run_environment(self, env):
        env.set('LCGEO', self.prefix.share.lcgeo.compact)
        env.set('lcgeo_DIR', self.prefix.share.lcgeo.compact)
        env.prepend_path("LD_LIBRARY_PATH", self.spec['lcgeo'].prefix.lib)

    def setup_build_environment(self, env):
        env.set('LCGEO', self.prefix.share.lcgeo.compact)
        env.set('lcgeo_DIR', self.prefix.share.lcgeo.compact)
        env.prepend_path("LD_LIBRARY_PATH", self.spec['lcio'].libs.directories[0])
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)

    def setup_dependent_build_environment(self, env, dependent_spec):
        env.set('LCGEO', self.prefix.share.lcgeo.compact)
        env.set('lcgeo_DIR', self.prefix.share.lcgeo.compact)
        env.prepend_path("LD_LIBRARY_PATH", self.spec['lcgeo'].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec['lcio'].libs.directories[0])

    # dd4hep tests need to run after install step:
    # disable the usual check
    def check(self):
        pass

    # instead add custom check step that runs after installation
    @run_after('install')
    def install_check(self):
        print(self)
        with working_dir(self.build_directory):
            if self.run_tests:
                ninja('test')

