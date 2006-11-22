##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util

def system(c):
    if os.system(c):
        raise SystemError("Failed", c)

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        options['location'] = options['prefix'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name)

    def install(self):
        dest = self.options['location']
        extra_options = self.options.get('extra_options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        extra_options = ' '.join(extra_options.split())

        url = self.options['url']
        _, _, urlpath, _, _, _ = urlparse.urlparse(url)
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        tmp2 = tempfile.mkdtemp('buildout-'+self.name)
        try:
            fname = os.path.join(tmp2, urlpath.split('/')[-1])
            open(fname, 'w').write(urllib2.urlopen(url).read())
            setuptools.archive_util.unpack_archive(fname, tmp)
            
            os.mkdir(dest)
            here = os.getcwd()
            try:
                os.chdir(tmp)
                try:
                    if not os.path.exists('configure'):
                        entries = os.listdir(tmp)
                        if len(entries) == 1:
                            os.chdir(entries[0])
                        else:
                            raise ValueError("Couldn't find configure")

                    system("./configure --prefix=%s %s" %
                           (dest, extra_options))
                    system("make")
                    system("make install")
                finally:
                    os.chdir(here)
            except:
                os.rmdir(dest)
                raise

        finally:
            shutil.rmtree(tmp)
            shutil.rmtree(tmp2)

        return dest

    def update(self):
        pass

                
