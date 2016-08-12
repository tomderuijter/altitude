altitude
========
Fast and lightweight querying of SRTM3 elevation data within Python.

---

## Getting started
Working with **altitude** is simple.
```python
from altitude import ElevationService
e = ElevationService('.cache/')
elevation = e.get_elevation(50.8, 7.5)
```

---

## Install
```
pip install altitude
```

---

## Contributing
This package is developed to be fast and lightweight. Contributions through pull-requests are very welcome, but should honour those two core principles.

---

## License
