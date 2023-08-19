#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Convert from html to on disk format
# Copyright (C) 2023 Chris Clark - clach04
"""setup.py dependencies NOT working yet
"""

import os
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


is_py3 = sys.version_info >= (3,)

if len(sys.argv) <= 1:
    print("""
Suggested setup.py parameters:

    * build
    * install
    * develop (instead of install)
    * sdist  --formats=zip
    * sdist  # NOTE requires tar/gzip commands

    python -m pip install -e .
""")

readme_filename = 'README.md'
if os.path.exists(readme_filename):
    f = open(readme_filename)
    long_description = f.read()
    f.close()
else:
    long_description = None

exec(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'w2d', '_version.py')).read())

# TODO/FIXME dupe of requirements.txt - also chi_io missing here (as not on pypi)
install_requires = [
    'pypub @ https://github.com/clach04/pypub/tarball/main#egg=package-1.0',  # FIXME this is not working for Python 3.6.9 with pip 9.0.1
    'markdownify',
    'readability-lxml',
    ]
if is_py3:
    install_requires += [
    'trafilatura',
    ]
install_requires = []  # FIXME hack so can install binary without dependencies, requires installing from requirements.txt


setup(
    name='w2d',
    version=__version__,
    author='clach04',
    url='https://github.com/clach04/wd2',
    description='Dumb web to disk tool; html, markdown / md / text, epub ',  # TODO update
    long_description=long_description,
    #packages=['w2d'],
    packages=find_packages(where=os.path.dirname(__file__), include=['*']),
    entry_points={
        'console_scripts': [
            'w2d = w2d:main',
        ],
    },
    #data_files=[('.', [readme_filename])],  # does not work :-( ALso tried setup.cfg [metadata]\ndescription-file = README.md # Maybe try include_package_data = True and a MANIFEST.in?
    classifiers=[  # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Text Processing :: Markup :: XML',  # closest to epub
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',  # Python 3.6.9
        'Programming Language :: Python :: 3.10',
        # FIXME TODO more
        ],
    platforms='any',  # or distutils.util.get_platform()
    install_requires=install_requires,
    #dependency_links=['pypub @ https://github.com/clach04/pypub/tarball/main#egg=package-1.0',],
)
