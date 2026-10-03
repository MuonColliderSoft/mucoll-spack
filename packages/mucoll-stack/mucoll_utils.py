"""
Common methods for Muon Collider recipes
"""

from spack.pkg.k4.key4hep_stack import Key4hepPackage


class MCIlcsoftpackage(Key4hepPackage):
    """Repeating the equivalent class in key4hep-spack repository"""

    maintainers = ["gianelle", "pandreetto"]

    def url_for_version(self, version):
        """Translate version numbers to the MuColl forked ILCSoft convention
        i.e. using dashed separator, leading zeros and '-MC' suffix
        e.g. 0.1   -> 00-01-MC
        e.g. 0.1.0 -> 00-01-MC
        e.g. 0.1.4 -> 00-01-04-MC
        """
        base_url = self.url.rsplit("/", 1)[0]
        if len(version) == 1:
            major = version[0]
            minor, patch = 0, 0
        elif len(version) == 2:
            major, minor = version
            patch = 0
        else:
            major, minor, patch = version
        # By now the data is normalized enough to handle it easily depending
        # on the value of the patch version
        if patch == 0:
            version_str = "v%02d-%02d-MC.tar.gz" % (major, minor)
        else:
            version_str = "v%02d-%02d-%02d-MC.tar.gz" % (major, minor, patch)
        return base_url + "/" + version_str
