altitude [![Code Health](https://landscape.io/github/tomderuijter/altitude/master/landscape.svg?style=flat)](https://landscape.io/github/tomderuijter/altitude/master)
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

## Referencing
```latex
@misc{altitude,
  author = {{Tom de Ruijter}},
  title = {{altitude}: Querying SRTM data on the fly.},
  howpublished = {\url{http://github.com/tomderuijter/altitude}},
  year = {since 2016}
}
```
---

## Contributing
This package is developed to be fast and lightweight. Contributions through pull-requests are very welcome, but should honour those two core principles.

---

## Contributors
- [Tom de Ruijter](https://github.com/tomderuijter/)

The library is inspired by [srtm.py](https://github.com/tkrajina/srtm.py/).

---

## License
This code is licensed under the Apache 2.0 license.
