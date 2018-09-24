# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from io import StringIO
import unittest
from unittest import mock
import sys

import upt


class TestPackage(unittest.TestCase):
    def test_str(self):
        pkg = upt.Package('foo', '4.2')
        self.assertEqual(str(pkg), 'foo@4.2')

        pkg = upt.Package('foo', '4.2')
        self.assertNotEqual(str(pkg), 'foo@42')


class TestPackageRequirement(unittest.TestCase):
    def test_str_with_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo', '>3.14')
        self.assertEqual(str(pkg_req), 'foo (>3.14)')

    def test_str_without_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo')
        self.assertEqual(str(pkg_req), 'foo')

    def test_equality(self):
        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('foo', '>3.14')
        self.assertEqual(pkg_req_a, pkg_req_b)

        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('foo', '>13.37')
        self.assertNotEqual(pkg_req_a, pkg_req_b)

        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('bar', '>3.14')
        self.assertNotEqual(pkg_req_a, pkg_req_b)


class TestUtils(unittest.TestCase):
    @mock.patch('pkg_resources.iter_entry_points')
    def test_get_installed_plugins(self, m_iter_entry_points):
        plugin = mock.Mock()
        plugin_cls = mock.Mock()
        plugin_cls.name = 'fake-name'
        plugin.load.return_value = plugin_cls
        m_iter_entry_points.return_value = [plugin]
        self.assertDictEqual(upt.upt._get_installed_plugins('dummy'),
                             {'fake-name': plugin.load.return_value})

    @mock.patch('upt.upt._get_installed_plugins')
    def test_get_installed_frontends_backends(self, m_get_plugins):
        fake_frontends = {
            'fake-frontend': mock.Mock()
        }

        fake_backends = {
            'fake-backend': mock.Mock()
        }

        def get_plugins(entrypoint):
            if entrypoint == 'upt.frontends':
                return fake_frontends
            elif entrypoint == 'upt.backends':
                return fake_backends
            else:
                raise ValueError(entrypoint)

        m_get_plugins.side_effect = get_plugins
        self.assertDictEqual(upt.upt._get_installed_frontends(),
                             fake_frontends)
        self.assertDictEqual(upt.upt._get_installed_backends(),
                             fake_backends)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = upt.upt.create_parser()

    def test_package_missing_frontend(self):
        args = 'package -b guix requests'.split()
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)

    def test_package_missing_backend(self):
        args = 'package -f pypi requests'.split()
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)

    def test_package_missing_frontend_and_backend(self):
        args = 'package requests'.split()
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)

    def test_package_missing_package(self):
        args = 'package -f pypi -b guix'.split()
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)

    def test_package_exclusive_logging_options(self):
        args = 'package -f pypi -b guix --debug --quiet requests'.split()
        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        sys.argv = ['/path/to/upt']

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_no_args(self, m_stdout, m_stderr):
        with self.assertRaises(SystemExit):
            upt.upt.main()
        self.assertEqual(m_stdout.getvalue(), '')
        self.assertEqual(m_stderr.getvalue()[:6], 'usage:')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('upt.upt._get_installed_backends')
    def test_list_backends(self, m_get_backends, m_stdout, m_stderr):
        sys.argv.append('list-backends')
        m_get_backends.return_value = {
            'fake-backend-1': object(),
            'fake-backend-2': object(),
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(m_stdout.getvalue(),
                         'fake-backend-1\nfake-backend-2\n')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('upt.upt._get_installed_frontends')
    def test_list_frontends(self, m_get_frontends, m_stdout, m_stderr):
        sys.argv.append('list-frontends')
        m_get_frontends.return_value = {
            'fake-frontend-1': object(),
            'fake-frontend-2': object(),
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(m_stdout.getvalue(),
                         'fake-frontend-1\nfake-frontend-2\n')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('upt.upt._get_installed_frontends', return_value={})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid': mock.Mock()})
    def test_package_invalid_frontend(self, m_backends, m_frontends):
        sys.argv.extend('package -f invalid -b valid pkgname'.split())
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends', return_value={})
    def test_package_invalid_backend(self, m_backends, m_frontends):
        sys.argv.extend('package -f valid -b invalid pkgname'.split())
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends')
    def test_package_unhandled_frontend(self, m_backends, m_frontends):
        cmdline = 'package -f valid-frontend -b valid-backend pkgname'
        sys.argv.extend(cmdline.split())

        def backend_fail(*args, **kwargs):
            raise upt.exceptions.UnhandledFrontendError('valid-backend',
                                                        'valid-frontend')
        fake_backend = mock.Mock()
        fake_backend().create_package.side_effect = backend_fail
        m_backends.return_value = {
            'valid-backend': fake_backend
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends')
    def test_package_invalid_pkgname(self, m_backends, m_frontends):
        cmdline = 'package -f valid-frontend -b valid-backend pkgname'
        sys.argv.extend(cmdline.split())

        def backend_fail(*args, **kwargs):
            raise upt.exceptions.InvalidPackageNameError('valid-backend',
                                                         'pkgname')
        fake_backend = mock.Mock()
        fake_backend().create_package.side_effect = backend_fail
        m_backends.return_value = {
            'valid-backend': fake_backend
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)
