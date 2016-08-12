srtm.py
=======
Fast and lightweight querying of SRTM3 elevation data within Python.

---

## Getting started
Working with **srtm.py** is simple.
```python
from srtm import ElevationService
e = ElevationService()
elevation = e.get_elevation(50.8, 7.5)
```

---

## Install
The package will soon be available on PyPI. Until then a local copy of the source code is necessary.
Run:
```
git clone https://github.com/tomderuijter/srtm.py.git
pip install -e srtm.py
```

---

## Contributing
This package is developed to be fast and lightweight. Contributions through pull-requests are very welcome, but should honour those two core principles.

---

## License
