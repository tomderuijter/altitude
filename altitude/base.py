import logging
import math as math
import os
import struct

from .srtm3_loader import SRTM3DataLoader


class ElevationService:
    """Query elevation data.

    This class is responsible for querying from local storage and interfacing
    with data loaders for downloading from remote repositories.
    """
    # TODO TdR 11/08/16: extract non-public methods to cache subclass
    def __init__(self, cache_dir, data_loader=None):
        if data_loader is None:
            data_loader = SRTM3DataLoader(cache_dir)

        # TODO TdR 10/08/16: Check whether data_loader implements DataLoader.
        self.data_loader = data_loader
        # TODO TdR 10/08/16: use semaphore for managing file handle pool.
        # TODO TdR 10/08/16: parallel reading could lead to further speeds.
        self.file_handles = {}

        self._cache_dir = os.path.join(cache_dir, data_loader.name)
        self._init_cache_dir()

        self.invalid_value = self.data_loader.invalid_value()

    def get_elevation(self, latitude, longitude):
        # Files are indexed by their corner coordinates.
        file_id = int(math.floor(latitude)), int(math.floor(longitude))
        if file_id not in self.file_handles:
            try:
                self._open_file_handle(file_id)
            except FileNotFoundError as e:
                logging.error(e)
                return None
        return self._get_elevation_from_file(file_id, latitude, longitude)

    def get_elevations(self, points):
        # TODO TdR 10/08/16: implement
        # TODO TdR 10/08/16: sort points on lon, then on lat.
        # TODO TdR 10/08/16: implement by calling get_elevation.
        pass

    def _get_elevation_from_file(self, file_id, latitude, longitude):

        file_handle = self.file_handles[file_id]

        byte_index = self.data_loader.get_byte_index(
            *file_id, latitude, longitude)
        byte_size = self.data_loader.byte_size
        file_handle.seek(byte_index)
        result = struct.unpack(">h", file_handle.read(byte_size))
        if result[0] != self.invalid_value:
            return result[0]
        else:
            return None

    def _open_file_handle(self, file_corner):
        file_name = _construct_tmp_name(file_corner)

        if not self._exists(file_name):
            byte_data = self.data_loader.download(file_corner)
            self._write(
                file_name,
                byte_data
            )
        self.file_handles[file_corner] = self._open(file_name)

    def _get_cache_dir(self):
        # TODO TdR 10/08/16: Cache anywhere but in HOME.
        name = self.data_loader.name
        if 'HOME' in os.environ:
            cache_dir = os.sep.join([os.environ['HOME'], '.cache', name])
        else:
            raise Exception('No cache directory specified.')
        return cache_dir

    def _init_cache_dir(self):
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def _exists(self, file_name):
        return os.path.exists('%s/%s' % (self._cache_dir, file_name))

    def _open(self, file_name):
        return open('%s/%s' % (self._cache_dir, file_name), 'rb')

    def _write(self, file_name, data):
        with open('%s/%s' % (self._cache_dir, file_name), 'wb') as f:
            f.write(data)


def _construct_tmp_name(file_corner):
    corner_lat, corner_lon = file_corner
    north_south = 'N' if corner_lat >= 0 else 'S'
    east_west = 'E' if corner_lon >= 0 else 'W'
    lat_str = str(int(abs(math.floor(corner_lat)))).zfill(2)
    lon_str = str(int(abs(math.floor(corner_lon)))).zfill(3)
    file_name = \
        north_south + lat_str + east_west + lon_str + '.hgt'
    return file_name
