#!/usr/bin/env python

from django_ogone import __version__, __maintainer__, __email__
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except:
    README = None

try: 
    LICENSE = open('LICENSE.txt').read() 
except: 
    LICENSE = None


setup(
    name = 'django-ogone',
    version = __version__,
    description='Python/Django client to the ogone payment system.',
    long_description=README,
    author = __maintainer__,
    author_email = __email__,
    license = LICENSE,
    url = 'http://github.com/tschellenbach/Django-ogone',
    packages = find_packages(),
    data_files=('',['README.md', 'LICENSE.txt']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
    ],
)
