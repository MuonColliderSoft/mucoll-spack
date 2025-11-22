# [Spack](https://github.com/spack/spack) package repository for Muon Collider software stack

### Note: the main branch is now used for the 3.x release series.

This repository holds a set of Spack recipes for Muon Collider software (under namespace `mucoll`) based on [Key4hep](https://key4hep.github.io/key4hep-doc/) stack. It is built on top of the key4hep-dev-external environment from the [key4hep-stack](https://github.com/key4hep/key4hep-spack) repository, which is required for installation.

After installing [Spack](https://github.com/key4hep/spack) and downloading the [key4hep-spack](https://github.com/key4hep/key4hep-spack) and [mucoll-spack](https://github.com/MuonColliderSoft/mucoll-spack) repositories, the whole software stack can be installed using the following commands:

```bash
# Setup spack and install key4hep-externals
spack repo add ./key4hep-spack
spack env activate ./key4hep-spack/environments/key4hep-dev-external
spack concretize --reuse
spack install --only-concrete --no-add --fail-fast
spack env deactivate

# Now move on to mucoll
spack repo add ./mucoll-spack
spack env activate ./mucoll-spack/environments/mucoll-release
spack concretize --reuse
spack install --only-concrete --no-add --fail-fast

# Load the Muon Collider environment
source $MUCOLL_STACK
```

## Setting up the environment

When signing in to a machine with the installed sofware stack (VM or Docker container), it has to be loaded into the environment:

```bash
spack env activate ./mucoll-spack/environments/mucoll-release
source $MUCOLL_STACK
```

## Package versioning

Preferred convention for version names in Spack is numbers separated by dots, without leading zeros, e.g. `1.2.13`.
Conversion to tag names in `mucoll` packages is provided by `MCIlcsoftpackage` class defined in `packages/mucoll-stack/mucoll_utils.py`, e.g. for [`lcgeo`](https://github.com/MuonColliderSoft/lcgeo/releases/tag/v00-17-MC) package version `0.17` corresponds to tag name `v00-17-MC`.


## Adding new versions for individual packages

After a new tag for the package is created, e.g. `v00-17-MC` in `lcgeo` repository, it can be added to this Spack repository in two steps:

1. Get the archive checksum for the new tag
```bash
spack checksum lcgeo 0.17
# Validates archive URL and returns the checksum
    version('0.17', sha256='5ab33aaf5bc37deba82c2dde78cdce6c0041257222ed7ea052ecdd388a41cf9b')
```

2. Add the returned version definition to the corresponding package file: [`packages/lcgeo/package.py`](packages/lcgeo/package.py)

> NOTE: This repository only contains packages maintained by the Muon Collider collaboration.
> If the version of interest is missing from Spack for some other package, the line with a new version definition should be added to the package file in the corresponding repository.  
> To see locations of other repositories: `spack repo list`

## Creating a new stack release

To introduce a new release version for the whole software stack, update the version number in [`packages/mucoll-stack/package.py`](packages/mucoll-stack/package.py) and then update versions of all the relevant packages in [environments/mucoll-release/packages.yaml].  
Test this new configuration in a fresh environment:
```bash
# Create a development environment
spack env create dev ./mucoll-spack/environments/mucoll-release/spack.yaml
spack env activate dev

# Add stack with updated version to the environment
spack add mucoll-stack

# Check which packages would be installed
spack spec --reuse -NIt
```

Packages that are already installed in the `sim` environment are known to Spack and will be reused, providing a clear indication of which part of the dependency tree will be modified by the new release.

## Modifying an existing package

It is possible to modify code of one or more packages using the [development workflow](https://spack-tutorial.readthedocs.io/en/latest/tutorial_developer_workflows.html), which lets Spack build it from your own source folder and use this custom version instead of the one installed in the release.

> NOTE: This should primarily be used for simple code changes in a few packages that do not affect the overall build process and dependency tree of other packages in the release. For more global changes it's better to set up a new release.

Assume that we want to make changes in the `LCIO` package, which many other packages depend on.

To leave the original release untouched it is preferable to create a new Spack environment, e.g. called `dev_lcio`, using the `.lock` file of the original environment as a starting point:

```bash
# Create a new environment
spack env create dev_lcio $SPACK_ENV/spack.lock

# Activate the development environment
spack env activate dev_lcio
```

The general procedure to replace a package with a custom version is the following:
1. put your new source code in a development folder of your choice, e.g. `/opt/dev/LCIO`;
2. find the exact spec of this package in the release and mark it for development in the folder with the new source code;
3. reconcretize the environment to replace the default version of the package with the development one;
4. rebuild the modified package using `spack install <package>`;
5. rebuild the rest of the release, which will reinstall all the packages that depend on the one you've modified.

You can repeat the last 2 steps each time you modify the source code again.

```bash
# Create the development folder
mkdir -p /opt/dev/LCIO

# Download the original source code (and modify it)
git clone https://github.com/MuonColliderSoft/LCIO.git --branch v02-19-01-MC

# Find the exact spec of this package in the current release
spack find lcio  # lcio@2.19.1

# Mark the package with this spec for development
spack develop -p /opt/dev/LCIO lcio@2.19.1

# Reconcretize the environment
spack concretize -f --reuse

# Build the modified package
spack install lcio

# Build the rest of the release
spack install
```

> NOTE: The package spec you mark for development must match exactly the one in the release, even if the actual code comes from a different version of the package. Otherwise you'll have to modify the packages configuration in the relase to properly include the new spec in the dependency tree.

To return to the original version of the release:
```bash
# Deactivate the current environment (if on lxplus)
spack env deactivate
# Activate the default environment (if in a Docker container)
spack env activate sim
```
The stack image will be created:
- `${REPOSITORY}/mucoll-sim:${VERSION}-alma9`: Contains the full Muon Collider Spack environment.
