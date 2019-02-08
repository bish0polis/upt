# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from enum import Enum
import hashlib


class HashUnknown(Exception):
    def __init__(self, hash_name):
        self.hash_name = hash_name

    def __str__(self):
        return f'Unknown hash "{self.hash_name}"'


class HashUnavailable(Exception):
    def __init__(self, hash_name):
        self.hash_name = hash_name

    def __str__(self):
        return f'Hash "{self.hash_name}" is not available on your system'


def _compute_checksum(checksum_fn, filepath):
    # TODO: Compute this chunk by chunk?
    m = checksum_fn()
    with open(filepath, 'rb') as f:
        m.update(f.read())
    return m.hexdigest()


def _compute_md5_checksum(filepath):
    return _compute_checksum(hashlib.md5, filepath)


def _compute_rmd160_checksum(filepath):
    return _compute_checksum(lambda: hashlib.new('ripemd160'), filepath)


def _compute_sha256_checksum(filepath):
    return _compute_checksum(hashlib.sha256, filepath)


def compute_checksum(filepath, hash_name):
    hash_functions = {
        'md5': _compute_md5_checksum,
        'rmd160': _compute_rmd160_checksum,
        'sha256': _compute_sha256_checksum,
    }
    try:
        return hash_functions[hash_name](filepath)
    except KeyError:
        raise HashUnknown(hash_name)
    except ValueError:
        raise HashUnavailable(hash_name)
