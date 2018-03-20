# Universal Packaging Tool (upt)

A unified CLI tool that converts a package from a language-specific package
manager (such as PyPI or NPM) to an almost ready-to-use package for Free
Unix-based operating systems (such as a GNU/Linux distribution or \*BSD).


## Installing
Please note that Python 3.6 or newer is required to run upt.

You may install upt from PyPI:

    $ pip install upt

You may also install it from the Git repository or a tarball:

    $ python setup.py install

By itself, upt is useless. It requires frontends and or backends to provide
useful features. See the list of available frontends/backends at the end of this
document. You may install them by running:

    $ pip install upt-pypi
    $ pip install upt-openbsd
    $ pip install ...

You may also install upt and all its frontends by running:

    $ pip install upt[frontends]

You may also install upt and all its backends by running:

    $ pip install upt[backends]

You may also install upt and all of its frontends and backends by running:

    $ pip install upt[frontends,backends]


## Usage
You may get help by running:

    $ upt --help

Upt gathers data about a package using a **frontend** and writes a package
definition using a **backend**. You may list all installed frontends and
backends by running:

```
$ upt list-frontends
cpan
pypi
$ upt list-backends
guix
openbsd
```

To package [the requests library from
PyPI](https://pypi.python.org/pypi/requests) for [GNU
Guix](https://www.gnu.org/s/guix), just write:

    $ upt package --frontend pypi --backend guix requests

Or, using shorter options:

    $ upt package -f pypi -b guix requests

The package definition will be written to the standard output.


## Under the hood
There are two kinds of places from where packages may be installed:

- language specific package repositories (CPAN, CRAN, CTAN, Hackage, NPM, PyPI,
  RubyGems, etc.)
- traditional, language agnostic package managers (apt for Debian, dnf for
  Fedora, Nix, Guix, pkgsrc, the OpenBSD ports, etc.)

Packages available on the former are usually also packaged in the latter ones.
Since packaging is a tedious and repetitive task, packagers have written tools
to assist them in this endeavor: Guix has "guix import", a collection of scripts
that parse CPAN, PyPI and other language specific package repositories and
generate a Guix package definition; Debian has tools such as pypi2deb,
npm2deb... The same goes for RPM-based distributions, and other operating
systems.

Let's talk about PyPI. It seems that (almost) every single distribution has (or
will have) a tool that parses PyPI. Whatever the distribution may be (Debian,
Fedora, Guix...), parsing PyPI is basically always the same thing: it is just
reading a JSON document. This code is not shared among distributions though,
which means that they all end up writing the same kind of code. The same is true
for other language specific package managers.

The distribution specific code is usually not even shared among the various
tools provided by said distribution. Writing an OpenBSD port always involve
creating a directory, writing the maintainer's name to a Makefile, etc. These
operations are common to all packages: they should not be rewritten over and
over by every single tool OpenBSD developers may end up using. The same is true
for Debian: creating a Debian package involves a lot of operations that are not
truly specific to the piece of software being packaged.

We may also note that all these tools come with their own interface: packagers
working with more than one package repository and/or more than one distribution
therefore have to use different interfaces to perform similar tasks.

The Universal Packaging Tool (upt) aims at providing package maintainers with a
unified CLI that harnesses the power of a modular infrastructure, meant to
factorize as much code as possible. Upt is the "core" of the project. It exposes
a CLI and a small Python library that defines an internal representation for
packages. Two kind of objects have to talk to upt:

- frontends, which parse a package repository and return information about a
  given package using upt's internal representation;
- backends, which turn the internal representation of a package into a valid
  package definition for a language agnostic package manager.

This is basically what other common tools do: the [GCC
compiler](https://gcc.gnu.org/) has frontends for languages and backends for CPU
architectures. Similarly, [pandoc](https://pandoc.org/) can convert files from
one markup language to another using various frontends and backends.

```
                |               |          |                  |
   Package      |      upt      |    upt   |       upt        |    Package
 Repositories   |   Frontends   |          |     Backends     |  Definitions
                |               |          |                  |
  +------+      |  +----------+ |  +-----+ |  +-------------+ |  +----------+
  |      |      |  |          | |  |     | |  |             | |  |          |
  | PyPI |------|->| upt-pypi |-|->|     |-|->|  upt-guix   |-|->| Guix pkg |
  |      |      |  |          | |  |     | |  |             | |  |          |
  +------+      |  +----------+ |  |     | |  +-------------+ |  +----------+
                |               |  | upt | |                  |
  +------+      |  +----------+ |  |     | |  +-------------+ |  +----------+
  |      |      |  |          | |  |     | |  |             | |  |          |
  | CPAN |------|->| upt-cpan |-|->|     |-|->| upt-openbsd |-|->| Makefile |
  |      |      |  |          | |  |     | |  |             | |  |          |
  +------+      |  +----------+ |  +-----+ |  +-------------+ |  +----------+
                |               |          |                  |
```

Here we can see that using the [upt-pypi](https://pypi.python.org/pypi/upt-pypi)
and [upt-cpan](https://pypi.python.org/pypi/upt-cpan) frontends, upt is able to
retrieve information about packages hosted on [CPAN](https://www.cpan.org/) and
[PyPI](https://pypi.python.org/). Then, using the
[upt-guix](https://pypi.python.org/pypi/upt-guix) backend, it can generate a
package definition suitable for [GNU Guix](https://www.gnu.org/s/guix); using
the [upt-openbsd](https://pypi.python.org/pypi/upt-openbsd) backend, it can
generate a Makefile suitable for [OpenBSD](https://www.openbsd.org)'s ports.

Using this modular approach, we solved our two issues:
- We will only ever need *one* PyPI parser, *one* CPAN parser, etc.
- We will only have one backend per distribution. Backends will not be truly
  language-agnostic: the build systems will not be the same for Python packages
  and Ruby packages, for instance. Still, a lot of code may be factorized: the
  creation of the required directories, the writing of some common metadata...

Last but not least, frontends and backends are not part of the upt core project.
Every backend, every frontend is a separate project, living in its own
repository, written by its own team. This way, nobody has control over the full
project, and different communities may make different technical choices (testing
tools, coding standards, version control systems...) without having to impose
them upon everyone else.


## Contributing to upt
You may contribute by sending patches to tipecaml@gmail.com or by opening a pull
request.

Your patches should not break anything, so, prior to sending them, be sure to
run:

    $ tox -eflake8
    $ tox -epy36

You may also want to contribute to one of the frontends/backends: they are
separate projects, so you should not send your patches to upt.


## Adding frontends or backends

### Adding a frontend
Your setup.cfg should use an entry point, like this:

```
# Taken from the upt-rubygems project
[options.entry_points]
upt.frontends =
    rubygems = upt_rubygems.upt_rubygems:RubyGemsFrontend
```

Alternatively, if you want to use setup.py:

```
setup(
    ...
    entry_points = { 
        'upt.frontends': [
            'rubygems=upt_rubygems.upt_rubygems:RubyGemsFrontend',
        ]   
    },
    ...
)
```

Let us now look at the implementation of a frontend:

```
...
import upt
...
class MyFrontEndPackage(upt.Package):
    pass


class MyFrontendParser(upt.Parser):
        name = 'myfrontend'

        def parse(self, pkg_name):
            ...
            return MyFrontendPackage(pkg_name,
                version=...,  # A string, such as '1.2.3'
                homepage=...,  # A string
                summary=...,  # A string containing a short description
                description=...,  # A string, containing a longer description
                download_urls=[url1, url2, ...],  # A list of strings
                # upt.PackageRequirement takes two arguments:
                # - the name of the package
                # - a version specifier, as defined in
                # https://www.python.org/dev/peps/pep-0440/#version-specifiers
                requirements={
                    'build': [
                         upt.PackageRequirement('build-dep', '>1.2'),
                         ...
                     ],
                    'run': [
                         upt.PackageRequirement('runtime-dep', ''),
                         ...
                     ],
                    'test': [
                         upt.PackageRequirement('test-dep', '<=2.3'),
                         ...
                     ]
                },
                # The license(s) used by this package, as instances of
                # upt.License. The upt project provides a lot of licenses in
                # the upt.licenses module. Use help(upt.licenses) to see the
                # whole list.
                # If you may not determine the nature of a licenses, you should
                # return upt.UnknownLicense().
                # The list of licenses may be empty.
                licenses=[
                    upt.licenses.BSDThreeClauseLicense(),
                    upt.UnknownLicense(),
                ]
         )

```

The most interesting method here is MyFrontendParser.parse. It must return a
upt.Package object (you may define a subclass such as MyFrontendPackage if you
wish). Only the package name and its version must be passed to the constructor,
all other fields are optional.

### Adding a backend
Your setup.cfg should use an entry point, like this:

```
[options.entry_points]
# Taken from upt-openbsd
upt.backends =
    openbsd = upt_openbsd.upt_openbsd:OpenBSD
```

Alternatively, if you want to use setup.py:

```
setup(
    ...
    entry_points = { 
        'upt.backends': [
            'openbsd=upt_openbsd.upt_openbsd:OpenBSD',
        ]   
    },
    ...
)
```

Let us now look at the implementation of a backend:

```
...
import upt
...
class MyBackend(upt.Backend):
    # The name of the backend: this is what will be seen in the output of
    # "upt --list-backends".
    name = 'mybackend'

    def create_package(self, upt_pkg, output=None):
        # Parameters:
        # - upt_pkg: an instance of upt_pkg. See the "Adding a frontend"
        #            section for more info on its fields.
        # - output: currently unused, will always be None.

        # Do whatever you need to generate a valid "package definition" for
        # your package manager. Note that "upt_pkg.frontend" contains the name
        # of the frontend that was used: it should be helpful with the
        # language-specific parts of your backend.
        ...

        # Currently, all backends write the "package definition" to stdout.
        print(...)
```


### Logging
Whether you are writing a frontend or a backend, you can use a logger provided
by upt by running:

```
import logging
...
logger = logging.getLogger('upt-backend')
```

See the [logging module
documentation](https://docs.python.org/3/library/logging.html) for more info on
how to use this logger.


## Known frontends and backends
The following frontends are supported:

- [upt-cpan](https://pypi.python.org/pypi/upt-cpan) a frontend for
  [CPAN](https://www.cpan.org/)
- [upt-pypi](https://pypi.python.org/pypi/upt-pypi) a frontend for
  [PyPI](https://pypi.python.org/)
- [upt-rubygems](https://pypi.python.org/pypi/upt-rubygems) a frontend for
  [RubyGems](https://rubygems.org/)

The following backends are supported:

- [upt-guix](https://pypi.python.org/pypi/upt-guix) a backend for [GNU
  Guix](https://www.gnu.org/s/guix)
- [upt-nix](https://pypi.python.org/pypi/upt-nix) a backend for
  [Nix](https://nixos.org/nix/)
- [upt-openbsd](https://pypi.python.org/pypi/upt-openbsd) a backend for
  [OpenBSD](https://www.openbsd.org)

Please tell us about your own frontends/backends!

## Similar projects

Here are some tools used to turn a package from a language-specific archive to
a package suitable for a general purpose package manager. We can see that [GNU
Guix](https://www.gnu.org/s/guix), [NetBSD](https://www.netbsd.org/) and
[OpenBSD](https://www.openbsd.org) decided to write a single tool, thus having
a unified CLI to access all upstream packages.

|      | Debian       | Fedora   | Guix        | FreeBSD  | NetBSD  | OpenBSD |
|------|--------------| ---------|-------------|----------|---------|---------|
| CPAN | dh-make-perl | cpan2rpm | guix import | ?        | url2pkg | PortGen |
| NPM  | npm2deb      | npm2rpm  | N/A         | ?        | url2pkg | ?       |
| PyPI | pypi2deb     | pyp2rpm  | guix import | pytoport | url2pkg | PortGen | 
| Ruby | gem2deb      | gem2rpm  | guix import | ?        | url2pkg | PortGen |


## License
This project is distributed under the [3-Clause BSD
License](https://opensource.org/licenses/BSD-3-Clause). See the LICENSE file.
