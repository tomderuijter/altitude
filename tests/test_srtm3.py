import logging
import srtm
from srtm.base import SRTM3DataLoader

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level='DEBUG'
)


class TestSRTM3Results:

    @classmethod
    def setup_class(cls):
        data_loader = SRTM3DataLoader()
        cls.file_engine = srtm.ElevationService(data_loader)
        cls.get_elevation = cls.file_engine.get_elevation

    def test_dead_sea(self):
        assert self.get_elevation(31.5, 35.5) == -415

    def test_around_zero_longitude(self):
        assert self.get_elevation(51.2, 0.0) == 61
        assert self.get_elevation(51.2, -0.1) == 100
        assert self.get_elevation(51.2, 0.1) == 59

    def test_around_zero_latitude(self):
        assert self.get_elevation(0, 15) == 393
        assert self.get_elevation(-0.1, 15) == 423
        assert self.get_elevation(0.1, 15) == 381

    def test_point_with_invalid_elevation(self):
        assert self.get_elevation(47.0, 13.07) is None

    def test_point_without_file(self):
        assert self.get_elevation(0, 0) is None

    def test_random_points(self):
        assert self.get_elevation(46.0, 13.0) == 63
        assert self.get_elevation(46.999999, 13.0) == 2714
        assert self.get_elevation(46.999999, 13.999999) == 1643
        assert self.get_elevation(46.0, 13.999999) == 553
        assert self.get_elevation(45.2732, 13.7139) == 203
        assert self.get_elevation(45.287, 13.905) == 460
