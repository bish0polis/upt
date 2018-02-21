# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def _install_reqs():
    with open('requirements.txt') as f:
        return f.read().split('\n')

setup(
    name='upt',
    author='Cyril Roelandt',
    author_email='tipecaml@gmail.com',
    url='https://framagit.org/upt/upt',
    version='0.2',
    description='Package software from any package manager to any distribution',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires = _install_reqs(),
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['upt = upt.upt:main'],
    },
)
