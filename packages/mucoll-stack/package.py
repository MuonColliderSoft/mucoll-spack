from datetime import datetime
import os

# import common methods for use in recipe from mucoll_utils.py
# (so other recipe can import from spack.pkg.mucoll.mucoll_stack)
# (which is the most convenient way to make that code available
#  without creation of a new module
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mucoll_utils import *

from spack.package import *
from spack.pkg.k4.key4hep_stack import *

class MucollStack(BundlePackage, Key4hepPackage):
    """Bundle package to install Muon Collider Software Stack"""
    
    homepage = 'https://github.com/MuonColliderSoft'
    
    maintainers = ['bartosik-hep', 'madbaron']

    ##################### versions ########################
    #######################################################
    ###  nightly build
    # to install the latest version of every dependency
    # should use `environments/mucoll-common/packages.yaml`
    version(datetime.today().strftime('%Y-%m-%d'))

    version("master", branch="master")
    version("full_gaudi_test", branch="full_gaudi_test")

    ### stable build
    # to install exact specified version for every dependecy
    # should use `environments/mucoll-release/packages.yaml`
    version('2.9')

    # this bundle package installs a custom setup script,
    # so need to add the install phase
    # (normally doesn't exist for a bundle package)
    phases = ['install']

    variant('devtools', default=True,
            description='add tools necessary for software development to the stack')
    variant('build_type', default='Release',
            description='CMake build type',
            values=('Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'))
    variant('llvm', default=False, description='Build with LLVM')
    variant('ml', default=False, description='Build with machine learning tools')
    variant('pytools', default=False, description='Build with python tools')

    # Add compilers to the build dependencies
    # so that we have them available to set them in the env script
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")

    ############################### Key4hep ###############
    #######################################################
    depends_on('whizard +lcio +openloops')
    depends_on('k4marlinwrapper')
    depends_on('k4simdelphes')
    depends_on('k4simgeant4')
    #depends_on('k4reco')
    #depends_on('k4gaudipandora')
    depends_on('k4actstracking')
    depends_on('delphes')

    ############################### ILCSoft ###############
    #######################################################
    depends_on('aidatt')
    depends_on('raida')
    depends_on('sio')
    depends_on('ced')
    depends_on('cedviewer')
    depends_on('garlic')
    depends_on('k4marlinwrapper')
    depends_on('generalbrokenlines')
    depends_on('gear')
    depends_on('ilcutil')
    depends_on('lcfiplus')
    depends_on('lcfivertex')
    depends_on('marlin')
    depends_on('marlinutil')
    depends_on('marlindd4hep')
    depends_on('marlinreco')
    depends_on('marlinfastjet')
    depends_on('marlinkinfit')
    depends_on('marlinkinfitprocessors')
    depends_on('marlintrk')
    depends_on('kaldet')
    depends_on('ddkaltest')
    depends_on('kitrackmarlin')
    depends_on('kaltest')
    depends_on('kitrack')
    depends_on('fcalclusterer')
    depends_on('pandoraanalysis')
    depends_on('pandorapfa')
    depends_on('clicperformance')


    ############## modified ILCSoft packages ##############
    #######################################################
    depends_on('lcio')
    depends_on('lctuple')
    depends_on('marlintrkprocessors')
    depends_on('forwardtracking')
    depends_on('conformaltracking')
    depends_on('ddmarlinpandora')

    ############ custom Muon Collider packages ############
    #######################################################
    depends_on('muoncvxddigitiser')


    ##################### developer tools #################
    #######################################################
    with when('+devtools'):
        depends_on('cmake')
        depends_on('ninja')
        depends_on('doxygen')
        depends_on('gdb')

    depends_on('llvm', when='+llvm')

    with when('+ml'):
        # ML tools
        depends_on('onnx')
        depends_on('xgboost')
        depends_on('py-onnxruntime')
        depends_on('py-onnx')

    with when('+pytools'):
        # Python tools
        depends_on('py-h5py')
        depends_on('py-ipython')
        # depends_on('py-jupytext') # this requires rust and node-js which take too long to compile
        depends_on('py-matplotlib')
        depends_on('py-pandas')
        depends_on('py-particle')
        depends_on('py-pip')
        depends_on('py-scikit-learn')
        depends_on('py-scipy')
        depends_on('py-uproot')
        depends_on('py-xgboost')

    ##################### conflicts #######################
    #######################################################
    conflicts("%gcc@8.3.1",
              msg="There are known issues with compilers from redhat's devtoolsets" \
              "which are therefore not supported." \
              "See https://root-forum.cern.ch/t/devtoolset-gcc-toolset-compatibility/38286")

    def setup_run_environment(self, env):
        # set locale to avoid certain issues with xerces-c
        # (see https://github.com/key4hep/key4hep-spack/issues/170)
        env.set("LC_ALL", "C")
        env.set('MUCOLL_STACK', os.path.join(self.spec.prefix, 'setup.sh'))
        env.set('MUCOLL_RELEASE_VERSION', self.spec.version)

        # ROOT needs to be in LD_LIBRARY_PATH to prevent using system installations
        env.prepend_path("LD_LIBRARY_PATH", self.spec["root"].prefix.lib)
        env.prepend_path("PYTHONPATH", self.spec["root"].prefix.lib)

        # set vdt, needed for root, see https://github.com/spack/spack/pull/37278
        if "vdt" in self.spec:
            env.prepend_path("CPATH", self.spec["vdt"].prefix.include)
            # When building podio with +rntuple there are warnings constantly without this
            env.prepend_path("LD_LIBRARY_PATH", self.spec["vdt"].libs.directories[0])

    def install(self, spec, prefix):
        return install_setup_script(self, spec, prefix, 'MUCOLL_LATEST_SETUP_PATH')
