##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
import re
import StringIO
import sys
import tarfile
import zc.buildout.testing

import unittest
import doctest
from zope.testing import renormalizing
from zc.buildout.tests import easy_install_SetUp
from zc.buildout.tests import normalize_bang

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.cmmi', test)
    distros = test.globs['distros'] = test.globs['tmpdir']('distros')

    tarpath = os.path.join(distros, 'foo.tgz')
    with tarfile.open(tarpath, 'w:gz') as tar:
        configure = configure_template % sys.executable
        info = tarfile.TarInfo('configure')
        info.size = len(configure)
        info.mode = 0o755
        tar.addfile(info, StringIO.StringIO(configure))

    tarpath = os.path.join(distros, 'bar.tgz')
    with tarfile.open(tarpath, 'w:gz') as tar:
        configure = configure_template % sys.executable
        info = tarfile.TarInfo('configure.in')
        info.size = len(configure)
        info.mode = 0o755
        tar.addfile(info, StringIO.StringIO(configure))

        autogen = autogen_template
        info = tarfile.TarInfo('autogen.sh')
        info.size = len(autogen)
        info.mode = 0o755
        tar.addfile(info, StringIO.StringIO(autogen))

    tarpath = os.path.join(distros, 'baz.tgz')
    with tarfile.open(tarpath, 'w:gz') as tar:
        configure = configure_template % sys.executable
        info = tarfile.TarInfo('configure.py')
        info.size = len(configure)
        info.mode = 0o755
        tar.addfile(info, StringIO.StringIO(configure))

def add(tar, name, src, mode=None):
    info.size = len(src)
    if mode is not None:
        info.mode = mode
    tar.addfile(info, StringIO.StringIO(src))

configure_template = """#!%s
import sys
print("configuring foo " + ' '.join(sys.argv[1:]))

Makefile_template = '''
all:
\techo building foo

install:
\techo installing foo
'''

open('Makefile', 'w').write(Makefile_template)

"""

autogen_template = """#!/bin/sh
mv configure.in configure
"""


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                (re.compile(r'--prefix=\S+sample-buildout'),
                 '--prefix=/sample_buildout'),
                (re.compile(r' = \S+sample-buildout'),
                 ' = /sample_buildout'),
                (re.compile('http://localhost:[0-9]{4,5}/'),
                 'http://localhost/'),
                (re.compile('occured'), 'occurred'),
               ]),
            optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
           ),
        doctest.DocFileSuite(
            'downloadcache.rst',
            'patching.rst',
            'shared.rst',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,

            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                normalize_bang,
                (re.compile('http://localhost:[0-9]{4,5}/'),
                 'http://localhost/'),
                (re.compile('extdemo[.]pyd'), 'extdemo.so'),
                (re.compile('[0-9a-f]{40}'), '<BUILDID>'),
                ]),
            optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE
            ),
        doctest.DocFileSuite(
            'misc.rst',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,

            checker=renormalizing.RENormalizing([
                (re.compile(r'--prefix=\S+sample-buildout'),
                 '--prefix=/sample_buildout'),
                (re.compile('http://localhost:[0-9]{4,5}/'),
                 'http://localhost/'),
                ]),
            optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE
            ),
        ))
