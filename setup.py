from distutils.core import setup


def setup_config():
    config = {
        'name': 'altitude',
        'version': '0.1',
        'description': 'Lightweight Python parser for SRTM elevation data.',
        'author': 'Tom de Ruijter',
        'author_email': 'deruijter.tom@gmail.com',
        'url': 'https://github.com/tomderuijter/altitude',
        'download_url': 'https://github.com/tomderuijter/altitude/tarball/v0.1',
        'packages': ['altitude'],
        'keywords': ['altitude', 'elevation', 'geographic', 'srtm'],
        'classifiers': [
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
        ],
        'install_requires': ['joblib'],
    }
    return config


if __name__ == "__main__":
    setup(**setup_config())
