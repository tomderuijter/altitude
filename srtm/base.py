import math as math
import os
import re
import struct


class ElevationService:
    """Interface to data files.

    This class is responsible for local storage and interfacing with data
    loaders for downloading from remote repositories.
    """
    def __init__(self, data_loader):
        # TODO TdR 10/08/16: Check whether data_loader implements DataLoader.
        self.data_loader = data_loader
        # TODO TdR 10/08/16: use semaphore for managing file handle pool.
        # TODO TdR 10/08/16: parallel reading could lead to further speeds.
        self.file_handles = {}

        self._init_cache_dir()
        self.cache_dir = self._get_cache_dir()

    def get_elevation(self, latitude, longitude):

        # Files are indexed by their corner coordinates.
        file_corner = int(math.floor(latitude)), int(math.floor(longitude))

        if file_corner not in self.file_handles:
            self._open_file_handle(file_corner)
        return \
            self._get_elevation_from_file(file_corner, latitude, longitude)

    def get_elevations(self, points):
        # TODO TdR 10/08/16: implement
        # TODO TdR 10/08/16: sort points on lon, then on lat.
        # TODO TdR 10/08/16: implement by calling get_elevation.
        pass

    def _get_elevation_from_file(self, file_corner, latitude, longitude):
        file_handle = self.file_handles[file_corner]

        byte_index = self.data_loader.get_byte_index(
            *file_corner, latitude, longitude)
        byte_size = self.data_loader.byte_size
        file_handle.seek(byte_index)
        result = struct.unpack(">h", file_handle.read(byte_size))
        return result[0]

    def _open_file_handle(self, file_corner):
        file_name = self.data_loader.get_file_name(*file_corner)
        if self._exists(file_name):
            self.file_handles[file_corner] = self._open_file(file_name)
        else:
            raise NotImplementedError("Downloading not implemented yet.")
        # TODO TdR 10/08/16: Continue implementation.
        # Load data from repository and store to cache.

    def _exists(self, file_name):
        return os.path.exists('%s/%s' % (self.cache_dir, file_name))

    def _open_file(self, file_name):
        return open('%s/%s' % (self.cache_dir, file_name), 'rb')

    def _get_cache_dir(self):
        # TODO TdR 10/08/16: Cache anywhere but in HOME.
        name = self.data_loader.name
        if 'HOME' in os.environ:
            cache_dir = os.sep.join([os.environ['HOME'], '.cache', name])
        elif 'HOMEPATH' in os.environ:
            cache_dir = os.sep.join([os.environ['HOMEPATH'], '.cache', name])
        else:
            raise Exception('No cache directory specified.')
        return cache_dir

    def _init_cache_dir(self):
        cache_dir = self._get_cache_dir()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)


class SRTM3DataLoader(object):
    """Class for downloading SRTM .hgt files.

    Subclass to specify custom dataset behaviour.
    """
    name = 'SRTM3'
    file_side_length = 1201
    byte_size = 2

    def __init__(self):
        # TODO TdR 10/08/16: change url to post-processed data source.
        self.url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'

    @classmethod
    def get_file_name(cls, latitude, longitude):
        """Map a point to a repository file name."""
        north_south = 'N' if latitude >= 0 else 'S'
        east_west = 'E' if longitude >= 0 else 'W'
        lat_str = str(int(abs(math.floor(latitude)))).zfill(2)
        lon_str = str(int(abs(math.floor(longitude)))).zfill(3)
        file_name = north_south + lat_str + east_west + lon_str + '.hgt'
        return file_name

    @classmethod
    def get_corner_coordinates(cls, latitude, longitude):
        return int(math.floor(latitude)), int(math.floor(longitude))

    @classmethod
    def get_byte_index(cls, corner_latitude, corner_longitude,
                       request_latitude, request_longitude):
        max_index = cls.file_side_length - 1.0
        row = math.floor(
            (corner_latitude + 1 - request_latitude) * max_index)
        col = math.floor(
            (request_longitude - corner_longitude) * max_index)
        byte_index = (row * cls.file_side_length + col) * cls.byte_size
        return byte_index
