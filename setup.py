#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name = "csv2psql",
    version = '0.4.2',
    packages = ['csv2psql'],
    package_dir = {'':'src'},   # tell distutils packages are under src
    zip_safe = True,
    author = "Darren Hardy",
    author_email = "hardy@nceas.ucsb.edu",
    description = "Convert CSV files into PostgreSQL tables",
    url = "http://www.nceas.ucsb.edu/",
    entry_points='''
[console_scripts]
csv2psql = csv2psql.__init__:main
'''
)
