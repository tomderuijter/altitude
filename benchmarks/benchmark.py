"""Script for testing various random access methods."""
import logging
import math
import struct
import timeit
from random import random

import numpy as np

from altitude import ElevationService, SRTM3DataLoader

TEST_FILE = 'N50E007.hgt'
FILE_SIDE_LENGTH = 1201  # Length of byte matrix
FILE_CORNER = (50, 7)
BYTE_SIZE = 2

TEST_POINT = (50.8, 7.5)
TEST_ELEVATION = 248


def random_point():
    return FILE_CORNER[0] + random(), FILE_CORNER[1] + random()


def latlon_to_file_index(latitude, longitude):
    row = math.floor(
        (FILE_CORNER[0] + 1 - latitude) *
        float(FILE_SIDE_LENGTH - 1))
    col = math.floor(
        (longitude - FILE_CORNER[1]) *
        float(FILE_SIDE_LENGTH - 1))
    byte_index = row * FILE_SIDE_LENGTH + col
    return byte_index


def test_struct_with_seek():
    byte_index = latlon_to_file_index(*TEST_POINT)
    i_start = byte_index * BYTE_SIZE
    with open(TEST_FILE, 'rb') as f:
        f.seek(i_start)
        unpacked = struct.unpack(">h", f.read(BYTE_SIZE))
    return unpacked[0]


# Persist file handle.
file_handle = open(TEST_FILE, 'rb')


def test_struct_with_seek_persisted():
    byte_index = latlon_to_file_index(*TEST_POINT)
    i_start = byte_index * BYTE_SIZE
    file_handle.seek(i_start)
    unpacked = struct.unpack(">h", file_handle.read(BYTE_SIZE))
    return unpacked[0]


def test_struct_with_seek_persisted_random():
    byte_index = latlon_to_file_index(*random_point())
    i_start = byte_index * BYTE_SIZE
    file_handle.seek(i_start)
    unpacked = struct.unpack(">h", file_handle.read(BYTE_SIZE))
    return unpacked[0]


# Persist whole file.
with open(TEST_FILE, 'rb') as f:
    elevations = np.fromfile(
        f, np.dtype('>i2'), FILE_SIDE_LENGTH * FILE_SIDE_LENGTH
    ).reshape((FILE_SIDE_LENGTH, FILE_SIDE_LENGTH))


def test_numpy_fromfile_persisted():
    lat, lon = TEST_POINT
    lat_row = int(round((lat - int(lat)) * (FILE_SIDE_LENGTH - 1), 0))
    lon_row = int(round((lon - int(lon)) * (FILE_SIDE_LENGTH - 1), 0))
    return elevations[
        (FILE_SIDE_LENGTH - 1) - lat_row, lon_row
    ].astype(int)


cache_dir = '.cache'
file_engine = ElevationService(cache_dir, SRTM3DataLoader(cache_dir))


def test_file_engine_random():
    return file_engine.get_elevation(*random_point())


def run_test(fun, test_descr, test_nr, nr_runs):
    print("Test %d - %s" % (test_nr, test_descr))
    t = timeit.timeit(
        fun,
        setup="from __main__ import %s" % fun.__name__,
        number=nr_runs
    )
    print("Test %d - finished (%.3fs)." % (test_nr, t))
    print("Test %d - value %d" % (test_nr, fun()))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level='DEBUG'
    )
    nr_runs = 250000
    # print("Running each test %d times." % nr_runs)
    tests = [
        (
            test_struct_with_seek,
            "STRUCT - Open file handle and seek specific bytes."
        ),
        (
            test_struct_with_seek_persisted,
            "STRUCT - Seek on persisted file handle."
        ),
        (
            test_struct_with_seek_persisted_random,
            "STRUCT - Randomly seek on persisted file handle."
        ),
        (
            test_file_engine_random,
            "MeteoGroup SRTM FileEngine."
        )
    ]
    for count, test in enumerate(tests):
        run_test(test[0], test[1], count + 1, nr_runs)

