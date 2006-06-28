##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, re, unittest
import pkg_resources
from zope.testing import doctest, renormalizing

def test_suite():
    global __test__
    req = pkg_resources.Requirement.parse('zc.recipe.filestorage')
    __test__ = dict(README=pkg_resources.resource_string(req, 'README.txt'))
    return doctest.DocTestSuite(
             checker=renormalizing.RENormalizing([
               (re.compile('\S+%(sep)s\w+%(sep)s\w+.fs'
                           % dict(sep=os.path.sep)),
                r'/tmp/data/Data.fs'),
               (re.compile('\S+sample-(\w+)'), r'/sample-\1'),
               ]),
             )

