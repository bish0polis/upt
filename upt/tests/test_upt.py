# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt


class TestPackageRequirement(unittest.TestCase):
    def test_str_with_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo', '>3.14')
        self.assertEqual(str(pkg_req), 'foo (>3.14)')

    def test_str_without_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo')
        self.assertEqual(str(pkg_req), 'foo')


class TestCommandLine(unittest.TestCase):
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
