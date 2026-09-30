# Overlay of the k4 (key4hep-spack) k4gaudipandora package, fixing the build on macOS.
#
# PandoraSDK's Helpers/XmlHelper.h does `#include "Xml/tinyxml.h"`, and DD4hep
# ships its own, different TinyXML as include/XML/tinyxml.h. On a
# case-insensitive filesystem (the macOS default) "Xml/" also matches DD4hep's
# "XML/", and DD4hep's include directory comes before PandoraSDK's on the
# compile line, so Pandora code is compiled against DD4hep's TinyXML
# ("unknown type name 'TiXmlHandle'; did you mean 'TiXmlHandle_t'?").
#
# On macOS, add PandoraSDK's include directory with -iquote, so quoted includes
# find it before any -I/-isystem directory. Neither -isystem nor -I works here:
# spack's compiler wrapper reorders -isystem paths, and clang drops a -I
# directory that is also given as -isystem (spack adds every dependency's
# include directory that way). This is safe: no DD4hep
# header includes its tinyxml.h, the two TinyXML copies use different include
# guards, and "Xml/tinyxml.h" / "Xml/tinystr.h" are the only headers the two
# include trees share. Drop this overlay once the include order or the header
# names no longer clash.

from spack.pkg.k4.k4gaudipandora import K4gaudipandora as K4K4gaudipandora

from spack.package import *


class K4gaudipandora(K4K4gaudipandora):
    __doc__ = K4K4gaudipandora.__doc__

    def cmake_args(self):
        args = super().cmake_args()
        if self.spec.satisfies("platform=darwin"):
            args.append(
                self.define("CMAKE_CXX_FLAGS", f"-iquote {self.spec['pandorasdk'].prefix.include}")
            )
        return args
