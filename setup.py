#!/usr/bin/env python

import os
from distutils.core import setup
from django_ogone import __version__, __maintainer__, __email__


license_text = open('LICENSE.txt').read()
long_description = open('README.md').read()

CLASSIFIERS = [
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'Framework :: Django',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Environment :: Web Environment',
              ]

DESCRIPTION = """Python/Django client to the ogone payment system. Aids in setting up secure payment functionality."""


setup(
    name = 'django-ogone',
    version = __version__,
    url = 'http://github.com/tschellenbach/Django-ogone',
    author = __maintainer__,
    author_email = __email__,
    license = license_text,
    packages = ['django_ogone'],
    data_files=[('', ['LICENSE.txt',
                      'README.rst'])],
    description = DESCRIPTION,
    long_description=long_description,
    classifiers = CLASSIFIERS
)