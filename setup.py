# Copyright 2018-2019 Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import configparser
import datetime
import subprocess

from setuptools import setup
from setuptools.command.sdist import sdist
from wheel.bdist_wheel import bdist_wheel


def generate_manpage():
    # This function is a bit ugly, but we can live with it.
    # No error handling: if something goes wrong, we want to abort ASAP.
    print('Generating manpage')

    # First, generate the man page from our Markdown.
    cmd = 'pandoc -s -t man upt.1.md -o upt.1'
    subprocess.check_call(cmd.split(' '))

    # Then, insert the date and the version
    date = datetime.datetime.strftime(datetime.date.today(), '%-d %B %Y')
    parser = configparser.ConfigParser()
    parser.read('setup.cfg')
    version = parser['metadata']['version']
    cmd = [
        'sed', '-i',
        f's/DATEPLACEHOLDER".*/{date}" "upt {version}"/',
        'upt.1'
    ]
    subprocess.check_call(cmd)


class SdistCommand(sdist):
    def run(self):
        generate_manpage()
        sdist.run(self)


class BdistwheelCommand(bdist_wheel):
    def run(self):
        generate_manpage()
        bdist_wheel.run(self)


setup(
    cmdclass={
        'sdist': SdistCommand,
        'bdist_wheel': BdistwheelCommand,
    },
)
