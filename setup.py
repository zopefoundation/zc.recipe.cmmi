##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
from setuptools import setup, find_packages


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


name = "zc.recipe.cmmi"

setup(
    name=name,
    version='3.1.0.dev0',
    author="Jim Fulton",
    author_email="jim@zope.com",
    description="ZC Buildout recipe for configure/make/make install",
    license="ZPL 2.1",
    keywords="zc.buildout buildout recipe cmmi configure make install",
    classifiers=[
        "Environment :: Plugins",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    url='http://github.com/zopefoundation/' + name,
    long_description=(
        read('README.rst')
        + '\n' +
        read('CHANGES.rst')
        + '\n' +
        '======================\n'
        'Detailed Documentation\n'
        '======================\n'
        + '\n' +
        read('src', 'zc', 'recipe', 'cmmi', 'README.rst')
        + '\n' +
        '==============\n'
        'Download Cache\n'
        '==============\n'
        'The recipe supports use of a download cache in the same way\n'
        'as zc.buildout. See downloadcache.txt for details\n'
        + '\n'
    ),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    namespace_packages=['zc', 'zc.recipe'],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=[
        'zc.buildout >= 2.9.4',
        'setuptools'],
    extras_require={
        'test': [
            # we import zc.buildout's 'test' package. It does have a
            # 'test' extra, but we really don't want all the things
            # that drags in, so we just list what's necessary for our
            # own tests to run.
            'manuel',
            'zope.testing',
            'zope.testrunner',
        ],
    },
    entry_points={
        'zc.buildout': [
            'default = %s:Recipe' % name
        ],
    },
    zip_safe=True,
)
