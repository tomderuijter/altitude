import math as math
import os
import re
import struct


class FileEngine:
    """Interface to data files.

    This class is responsible for local storage and interfacing with data
    loaders for downloading from remote repositories.
    """
    def __init__(self, data_loader):
        # TODO TdR 10/08/16: Check whether data_loader implements DataLoader.
        self.data_loader = data_loader
        # TODO TdR 10/08/16: use semaphore for managing file handle pool.
        self.file_handles = {}
        self.cache_dir = self.get_cache_dir()

    def get_elevation(self, latitude, longitude):
        import pdb
        pdb.set_trace()
        file_name = self.data_loader.get_file_name(latitude, longitude)
        file_corner = self.data_loader.parse_file_name(file_name)
        file_descriptor = FileDescriptor(file_name, *file_corner)

        if file_descriptor not in self.file_handles:
            self.open_file_handle(file_descriptor)

        elevation = \
            self.get_elevation_from_file(file_descriptor, latitude, longitude)
        return elevation

    def get_elevations(self, points):
        # TODO TdR 10/08/16: implement
        # TODO TdR 10/08/16: sort points on lon, then on lat.
        # TODO TdR 10/08/16: implement by calling get_elevation.
        pass

    def get_elevation_from_file(self, file_descriptor, latitude, longitude):
        file_handle = self.file_handles[file_descriptor]
        corner_lat = file_descriptor.latitude
        corner_lon = file_descriptor.longitude

        byte_index = self.data_loader.get_byte_index(
            corner_lat, corner_lon, latitude, longitude)
        byte_size = self.data_loader.byte_size
        file_handle.seek(byte_index)
        import pdb
        pdb.set_trace()
        # TODO TdR 10/08/16: Continue here.
        result = struct.unpack(
            ">i" + str(byte_size),
            file_handle.read(byte_size)
        )
        return result[0]

    def open_file_handle(self, file_descriptor):
        file_name = file_descriptor.name
        if self.exists(file_name):
            self.file_handles[file_descriptor] = self.open_file(file_name)

        # TODO TdR 10/08/16: Continue implementation.
        # Load data from repository and store to cache.

    def exists(self, file_name):
        return os.path.exists('%s/%s' % (self.cache_dir, file_name))

    def open_file(self, file_name):
        return open('%s/%s' % (self.cache_dir, file_name), 'rb')

    @classmethod
    def get_cache_dir(cls):
        # TODO TdR 10/08/16: Cache anywhere but in HOME.
        if 'HOME' in os.environ:
            cache_dir = os.sep.join([os.environ['HOME'], '.cache', 'srtm'])
        elif 'HOMEPATH' in os.environ:
            cache_dir = os.sep.join([os.environ['HOMEPATH'], '.cache', 'srtm'])
        else:
            raise Exception('No cache directory specified.')
        return cache_dir

    @classmethod
    def init_cache_dir(cls):
        cache_dir = cls.get_cache_dir()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)


class FileDescriptor(object):
    """Data file descriptor.

    latitude and longitude encode the file's lower left corner.
    """
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def __eq__(self, other):
        return self.latitude == other.latitude and \
               self.longitude == other.longitude

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name)


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
        file_name = '%s%s%s%s.hgt' % (
            north_south, str(int(abs(math.floor(latitude)))).zfill(2),
            east_west, str(int(abs(math.floor(longitude)))).zfill(3)
        )
        return file_name

    @classmethod
    def parse_file_name(cls, file_name):
        """Return coordinates in file name."""
        groups = re.findall('([NS])(\d+)([EW])(\d+)\.hgt', file_name)
        assert groups and len(groups) == 1 and len(groups[0]) == 4, \
            'Invalid file name {0}'.format(file_name)
        file_parts = groups[0]

        if file_parts[0] == 'N':
            latitude = float(file_parts[1])
        else:
            latitude = -float(file_parts[1])

        if file_parts[2] == 'E':
            longitude = float(file_parts[3])
        else:
            longitude = -float(file_parts[3])
        return latitude, longitude

    @classmethod
    def get_byte_index(cls, corner_latitude, corner_longitude,
                       request_latitude, request_longitude):
        # TODO TdR 10/08/16: implement
        row = math.floor(
            (corner_latitude + 1 - request_latitude) *
            float(cls.file_side_length - 1))
        col = math.floor(
            (request_longitude - corner_longitude) *
            float(cls.file_side_length - 1))
        byte_index = (row * cls.file_side_length + col) * cls.byte_size
        return byte_index
