# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import argparse
from enum import Enum
import logging
import os
import urllib.request
import sys

import pkg_resources

import upt.checksum
import upt.exceptions
import upt.log


class Backend(object):
    pass


class Frontend(object):
    """Base class for all upt Frontends."""
    pass


class ArchiveType(Enum):
    SOURCE_TARGZ = 1


class ArchiveUnavailable(Exception):
    def __str__(self):
        return 'No such archive could be found'


class Archive(object):
    '''An archive file.

    This can be a source tarball, a Python wheel, a Ruby gem, a binary, etc.
    '''
    def __init__(self, url, archive_type=ArchiveType.SOURCE_TARGZ, size=0,
                 md5=None, sha256=None, rmd160=None):
        self.url = url
        self.archive_type = archive_type
        self._size = size
        self._filepath = None
        self._hashes = {}
        if md5 is not None:
            self.md5 = md5
        if sha256 is not None:
            self.sha256 = sha256
        if rmd160 is not None:
            self.rmd160 = rmd160

    @property
    def filepath(self):
        if self._filepath is None:
            self._filepath, _ = urllib.request.urlretrieve(self.url)
        return self._filepath

    @property
    def size(self):
        if self._size == 0:
            self._size = os.stat(self.filepath).st_size
        return self._size

    def _checksum(self, hash_name):
        try:
            return self._hashes[hash_name]
        except KeyError:
            value = upt.checksum.compute_checksum(self.filepath, hash_name)
            self._hashes[hash_name] = value
            return value

    @property
    def md5(self):
        return self._checksum('md5')

    @md5.setter
    def md5(self, value):
        self._hashes['md5'] = value

    @property
    def rmd160(self):
        return self._checksum('rmd160')

    @rmd160.setter
    def rmd160(self, value):
        self._hashes['rmd160'] = value

    @property
    def sha256(self):
        return self._checksum('sha256')

    @sha256.setter
    def sha256(self, value):
        self._hashes['sha256'] = value


class PackageRequirement(object):
    """Package Requirement.

    Two main attributes are used:
    - name: a string, representing the name of the package.
    - specifier: a string, representing a version specifier as defined in
                 https://www.python.org/dev/peps/pep-0440/#version-specifiers .
                 The format of the specifier is subject to changes.
    """
    def __init__(self, name, specifier=None):
        self.name = name
        self.specifier = specifier

    def __str__(self):
        if self.specifier is not None:
            return f'{self.name} ({self.specifier})'
        else:
            return f'{self.name}'

    def __eq__(self, other):
        return (self.name == other.name and
                self.specifier == other.specifier)


class Package(object):
    """Base class for all packages.

    Constructor arguments:
    - name: required, the name of the package
    - version: required, the version of the package, as a str

    Optional keyword arguments:
    - homepage: a string, representing the official homepage of the package
    - summary: a short summary of the package's purpose
    - description: a long description of the package's purpose
    - download_urls: deprecated
    - requirement: a dict with 3 keys:
        - 'build': the build dependencies of the package;
        - 'run': the runtime dependencies of the package;
        - 'test': the test dependencies of the package.
      The values associated with these keys are always lists of
      PackageRequirement objects.
    - licenses: a list of upt.licenses.License objects
    """
    def __init__(self, name, version, **kwargs):
        self.name = name
        self.version = version
        self.homepage = kwargs.get('homepage', '')
        self.summary = kwargs.get('summary', '')
        self.description = kwargs.get('description', '')
        # TODO: Remove download urls.
        self.download_urls = kwargs.get('download_urls', [])
        # Software requirements, as instances of PackageRequirement: {
        #     'build': [pkg1, ...],
        #     'run': [pkg2, ...],
        #     'test': [pkg3, ...]
        # }
        self.requirements = kwargs.get('requirements', {})
        self.licenses = kwargs.get('licenses', [])
        self.archives = kwargs.get('archives', [])

    def __str__(self):
        return f'{self.name}@{self.version}'

    def get_archive(self, archive_type=ArchiveType.SOURCE_TARGZ):
        for archive in self.archives:
            if archive.archive_type == archive_type:
                return archive
        else:
            raise ArchiveUnavailable()

    def _clean(self):
        for archive in self.archives:
            if archive._filepath is not None:
                os.remove(archive._filepath)


def create_parser():
    parser = argparse.ArgumentParser(prog='upt')

    subparsers = parser.add_subparsers(title='Commands', dest='cmd')

    # List backends
    subparsers.add_parser('list-backends',
                          help='List installed backends')

    # List frontends
    subparsers.add_parser('list-frontends',
                          help='List installed frontends')

    # Actually package software
    parser_package = subparsers.add_parser('package',
                                           help='Package a piece of software')
    required_args = parser_package.add_argument_group('Required arguments')
    required_args.add_argument('-f', '--frontend', required=True,
                               help='Frontend to use')
    required_args.add_argument('-b', '--backend', required=True,
                               help='Backend to use')
    logger_group = parser_package.add_mutually_exclusive_group()
    logger_group.add_argument('--debug', action='store_const',
                              const=logging.DEBUG, dest='log_level',
                              help='Print debug messages.')
    parser_package.add_argument('-o', '--output',
                                help='Output file/directory. Defaults to '
                                     'stdout/current directory. This may be '
                                     'ignored by the backend.')
    logger_group.add_argument('-q', '--quiet', action='store_const',
                              const=logging.CRITICAL+1, dest='log_level',
                              help='Suppress all logging output')
    parser_package.add_argument('package', help='Name of the package')

    return parser


def _get_installed_plugins(entrypoint):
    plugins = {}
    for ep in pkg_resources.iter_entry_points(entrypoint):
        plugin_cls = ep.load()
        plugins[plugin_cls.name] = plugin_cls

    return plugins


def _get_installed_frontends():
    return _get_installed_plugins('upt.frontends')


def _get_installed_backends():
    return _get_installed_plugins('upt.backends')


def main():
    parser = create_parser()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.cmd == 'list-backends':
        for backend in _get_installed_backends().keys():
            print(backend)
        sys.exit(0)

    if args.cmd == 'list-frontends':
        for frontend in _get_installed_frontends().keys():
            print(frontend)
        sys.exit(0)

    if args.cmd == 'package':
        frontends = _get_installed_frontends()
        backends = _get_installed_backends()

        try:
            frontend = frontends[args.frontend]()
        except KeyError:
            print(f'No frontend named {args.frontend}.')
            sys.exit(1)

        try:
            backend = backends[args.backend]()
        except KeyError:
            print(f'No backend named {args.backend}.')
            sys.exit(1)

        logger = upt.log.create_logger(args.log_level)

        try:
            upt.log.logger_set_formatter(logger, 'Frontend')
            upt_pkg = frontend.parse(args.package)
            upt_pkg.frontend = args.frontend
            upt.log.logger_set_formatter(logger, 'Backend')
            backend.create_package(upt_pkg, output=args.output)
        except upt.exceptions.UnhandledFrontendError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except upt.exceptions.InvalidPackageNameError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        finally:
            upt_pkg._clean()
