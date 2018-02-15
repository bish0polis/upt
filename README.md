# Universal Packaging Tool (upt)

A unified CLI tool that converts a package from a language-specific package
manager (such as PyPI or NPM) to an almost ready-to-use package for Free
Unix-based operating systems (such as a GNU/Linux distribution or \*BSD).


## Installing
Please note that Python 3.6 or newer is required to run upt.

You may install upt from PyPI:

    $ pip install upt

You may also install it from the Git repository or a tarball:

    $ python setup.py develop

By itself, upt is useless. It requires frontends and or backends to provide
useful features. See the list of available frontends/backends at the end of this
document. You may install them by running:

    $ pip install upt-pypi
    $ pip install upt-openbsd
    $ pip install ...


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
  RubyGems)
- traditional, language agnostic package managers (apt for Debian, dnf for
  Fedora, Nix, Guix, pkgsrc, the OpenBSD ports)

Packages available on the former are usually also packaged in the latter ones.
Since packaging is a tedious and repetitive task, packagers have written tools
to assist them in this endeavor: Guix has "guix import", a collection of scripts
that parse CPAN, PyPI and other language specific package repositories and
generate a Guix package definition; Debian has tools such as pypi2deb,
npm2deb... The same goes for RPM-based distributions.

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
Your setup.py should use the entry points like this:

```
setup(
    ...
    entry_points = { 
        'upt.frontends': [
            'myfrontend=upt_myfrontend.upt_myfrontend:MyFrontendParser',
        ]   
    },
    ...
)
```

Let us now look at your upt_myfrontend/upt_myfrontend.py file:

```
...
import upt
...
class MyFrontEndPackage(upt.Package):
    pass

class MyFrontendParser(upt.Parser):
 16     name = 'myfrontend'
        def parse(self, pkg_name):
            ...
            return MyFrontendPackage(pkg_name,
                version=...,
                homepage=...,
                summary=...,
                description=...,
                download_urls=[url1, url2, ...],
                requirements={
                    'build': [pkg1, ...],
                    'run': [pkg2, ...],
                    'test': [pkg3, ...]
                })

```

The most interesting method here is MyFrontendParser.parse. It must return a upt.Package object (you may define a subclass such as MyFrontendPackage if you wish). Only the package name and its version must be passed to the constructor, all other fields are optional.

### Adding a backend
```
setup(
    ...
    entry_points = { 
        'upt.backends': [
            'mybackend=upt_mybackend.upt_mybackend:MyBackend',
        ]   
    },
    ...
)
```


## Known frontends and backends
The following frontends are supported:

- [upt-cpan](https://pypi.python.org/pypi/upt-cpan) a frontend for
  [CPAN](https://www.cpan.org/)
- [upt-pypi](https://pypi.python.org/pypi/upt-pypi) a frontend for
  [PyPI](https://pypi.python.org/)

The following backends are supported:

- [upt-guix](https://pypi.python.org/pypi/upt-guix) a backend for [GNU
  Guix](https://www.gnu.org/s/guix)
- [upt-openbsd](https://pypi.python.org/pypi/upt-openbsd) a backend for
  [OpenBSD](https://www.openbsd.org)

Please tell us about your own frontends/backends!


## License
This project is distributed under the [3-Clause BSD
License](https://opensource.org/licenses/BSD-3-Clause). See the LICENSE file.
