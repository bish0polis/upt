---
title: UPT(1)
author: Cyril Roelandt <upt@framalistes.org>
date: DATEPLACEHOLDER
---

# NAME

upt - Universal Packaging Tool

# SYNOPSIS

upt list-backends

upt list-frontends

upt package [-f FRONTEND] [-b BACKEND] [-o OUTPUT] [-u/\--update] [\--debug] [\--quiet] PACKAGE[@VERSION]

# DESCRIPTION
Create a package for a distribution (such as OpenBSD, Fedora, etc.) from a
language-specific package archive (such as the Python Package Index, the
Comprehensive Perl Archive Network, etc.).

Upt works with two kinds of modules:

- frontends, which parse package metadata from a software archive;

- backends, which create package definitions suitable for inclusion in your
  favorite distribution.

The following subcommands are available:

**list-backends**
: List all installed backends.

**list-frontends**
: List all installed frontends.

**package [options...] \<package>[@version]**
: Package the given package. This usually requires options, described below.
  If no version is specified, the latest one is used.


# OPTIONS
-b *BACKEND*, \--backend *BACKEND*

: Specify backend to use. Must be one of the values returned by "upt
list-backends". At least one backend must be installed. If only one backend is
installed, this is optional; otherwise it is required. See BACKENDS.

\--debug

: Print debug messages. Cannot be used with \--quiet.

-f *FRONTEND*, \--frontend *FRONTEND*

: Specify frontend to use. Must be one of the values returned by "upt
list-frontends". At least one frontend must be installed. If only one frontend
is installed, this is optional; otherwise it is required. See FRONTENDS.

-h, \--help

: Show help and return.

-o, \--output *OUTPUT*

: Specify an output file or directory. If this option is not specified, stdout
will be used (if possible). The exact meaning of this option may vary depending
on the backend: it should do the most natural thing.

-q, \--quiet

: Suppress all logging output. Cannot be used with \--debug.

-r, \--recursive

: Recursively package requirements.

-u, \--update

: Update a package.


# BACKENDS
**upt-fedora**
: Create packages for Fedora

**upt-freebsd**
: Create packages for FreeBSD

**upt-guix**
: Create packages for GNU Guix

**upt-macports**
: Create packages for MacPorts

**upt-nix**
: Create packages for Nix

**upt-openbsd**
: Create packages for OpenBSD

# FRONTENDS
**upt-cpan**
: Gather metadata about packages hosted on cpan.org

**upt-pypi**
: Gather metadata about packages hosted on pypi.org

**upt-rubygems**
: Gather metadata about packages hosted on rubygems.org

# EXAMPLES

**List installed frontends**

: upt list-frontends

**List installed backends**

: upt list-backends

**Package "requests" from PyPI, for use in GNU Guix**

: upt package -f pypi -b guix requests

**Same, omitting "-b" when there is only one installed backend**

: upt package -f pypi requests

**Same, omitting "-f" when there is only one installed frontend**

: upt package requests


**Same, but package a given version**

: upt package requests@2.16.0

**Update an existing package**

: upt package -f pypi -b macports -u requests

**Update an existing package to a specific version**

: upt package -f pypi -b macports -u requests@2.22.0

# BUGS

Bugs can be reported to upt@framalistes.org. A web interface is also available
at https://framagit.org/upt (one may sign in using their
github.com/gitlab.com/bitbucket.org credentials). Feel free to suggest new
backends and frontends.

Users are also welcome in the #upt-packaging channel on Freenode.
