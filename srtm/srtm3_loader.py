import io
import logging
import math as math
import re
import urllib.request
import zipfile

import joblib

from .crawler import LinkCrawler


class SRTM3DataLoader(object):
    """Class for downloading SRTM3 .hgt files.

    Copy and override all public methods to specify custom dataset behaviour.
    The frequent use of 'file_corner' is because SRTM tile files are
    identified by their lower left corner's coordinates.
    """
    name = 'SRTM3'
    file_side_length = 1201
    byte_size = 2

    def __init__(self, cache_dir):
        # TODO TdR 10/08/16: change url to post-processed data source.
        self.url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'
        self.file_listing = None

        cache_engine = joblib.Memory(cachedir=cache_dir, verbose=0)
        self.crawl_page = cache_engine.cache(self.crawl_page)

    @classmethod
    def get_byte_index(cls, corner_latitude, corner_longitude,
                       request_latitude, request_longitude):
        # Override method
        max_index = cls.file_side_length - 1.0
        row = math.floor(
            (corner_latitude + 1 - request_latitude) * max_index)
        col = math.floor(
            (request_longitude - corner_longitude) * max_index)
        byte_index = (row * cls.file_side_length + col) * cls.byte_size
        return byte_index

    # TODO TdR 12/08/16: Put caching at this level?
    def download(self, file_corner):
        if not self.file_listing:
            logging.debug("No file listing loaded.")
            self._download_file_listing()
            logging.debug("Loaded file listing.")

        try:
            file_url = self.file_listing[file_corner]
        except KeyError:
            raise FileNotFoundError(
                "Tile (%d, %d) does not exist" % file_corner)

        logging.debug("Downloading file: %s" % file_url)
        with urllib.request.urlopen(file_url) as response:
            response_data = response.read()
        if file_url.endswith('.zip'):
            response_data = _unzip(response_data)
        logging.debug("Finished downloading.")
        return response_data

    def _download_file_listing(self):
        file_urls = self.crawl_page(self.url)
        file_listing = {}
        for url in file_urls:
            file_corner = self._parse_file_name_corner(url)
            if file_corner:
                file_listing[file_corner] = url
        self.file_listing = file_listing

    @classmethod
    def invalid_value(cls):
        return -(2 ** (cls.byte_size * 8 - 1))

    @classmethod
    def _parse_file_name_corner(cls, file_name):
        groups = re.findall('([NS])(\d+)([EW])(\d+)', file_name)
        if not(groups and len(groups) == 1 and len(groups[0]) == 4):
            return None
        groups = groups[0]
        if groups[0] == 'N':
            latitude = int(groups[1])
        else:
            latitude = -int(groups[1])

        if groups[2] == 'E':
            longitude = int(groups[3])
        else:
            longitude = -int(groups[3])
        return latitude, longitude

    @classmethod
    def crawl_page(cls, url):
        crawler = LinkCrawler()
        file_urls = crawler.crawl(url)
        return file_urls


def _unzip(byte_data):
    z_file = zipfile.ZipFile(io.BytesIO(byte_data))
    z_info = z_file.infolist()[0]
    unzipped_data = z_file.open(z_info).read()
    return unzipped_data
