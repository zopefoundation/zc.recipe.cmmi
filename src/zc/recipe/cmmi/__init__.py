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
import datetime
import sha
import shutil
import zc.buildout

def system(c):
    if os.system(c):
        raise SystemError("Failed", c)

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        directory = buildout['buildout']['directory']
        self.download_cache = buildout['buildout'].get('download-cache')
        self.install_from_cache = buildout['buildout'].get('install-from-cache')

        if self.download_cache:
            # cache keys are hashes of url, to ensure repeatability if the
            # downloads do not have a version number in the filename
            # cache key is a directory which contains the downloaded file
            # download details stored with each key as cache.ini
            self.download_cache = os.path.join(
                directory, self.download_cache, 'cmmi')

        # we assume that install_from_cache and download_cache values
        # are correctly set, and that the download_cache directory has
        # been created: this is done by the main zc.buildout anyway

        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        options['location'] = os.path.join(location, name)
        options['prefix'] = options['location']

    def install(self):
        logger = logging.getLogger(self.name)
        dest = self.options['location']
        url = self.options['url']
        extra_options = self.options.get('extra_options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        extra_options = ' '.join(extra_options.split())

        autogen = self.options.get('autogen', '')

        patch = self.options.get('patch', '')
        patch_options = self.options.get('patch_options', '-p0')

        fname = getFromCache(
            url, self.name, self.download_cache, self.install_from_cache)

        # now unpack and work as normal
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        logger.info('Unpacking and configuring')
        setuptools.archive_util.unpack_archive(fname, tmp)

        here = os.getcwd()
        if not os.path.exists(dest):
            os.mkdir(dest)

        environ = self.options.get('environment', '').split()
        if environ:
            for entry in environ:
                logger.info('Updating environment: %s' % entry)
            environ = dict([x.split('=', 1) for x in environ])
            os.environ.update(environ)

        try:
            os.chdir(tmp)
            try:
                if not (os.path.exists('configure') or
                        os.path.exists(autogen)):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                if patch is not '':
                    # patch may be a filesystem path or url
                    # url patches can go through the cache
                    if urlparse.urlparse( patch, None)[0] is not None:
                        patch = getFromCache( patch
                                            , self.name
                                            , self.download_cache
                                            , self.install_from_cache
                                            )
                    system("patch %s < %s" % (patch_options, patch))
                if autogen is not '':
                    logger.info('auto generating configure files')
                    system("./%s" % autogen)
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
            shutil.rmtree(dest)
            raise

        return dest

    def update(self):
        pass

def getFromCache(url, name, download_cache=None, install_from_cache=False):
    if download_cache:
        cache_fname = sha.new(url).hexdigest()
        cache_name = os.path.join(download_cache, cache_fname)
        if not os.path.isdir(download_cache):
            os.mkdir(download_cache)

    _, _, urlpath, _, _ = urlparse.urlsplit(url)
    filename = urlpath.split('/')[-1]

    # get the file from the right place
    fname = tmp2 = None
    if download_cache:
        # if we have a cache, try and use it
        logging.getLogger(name).debug(
            'Searching cache at %s' % download_cache)
        if os.path.isdir(cache_name):
            # just cache files for now
            fname = os.path.join(cache_name, filename)
            logging.getLogger(name).debug(
                'Using cache file %s' % cache_name)

        else:
            logging.getLogger(name).debug(
                'Did not find %s under cache key %s' % (filename, cache_name))

    if not fname:
        if install_from_cache:
            # no file in the cache, but we are staying offline
            raise zc.buildout.UserError(
                "Offline mode: file from %s not found in the cache at %s" %
                (url, download_cache))
        try:
            # okay, we've got to download now
            # XXX: do we need to do something about permissions
            # XXX: in case the cache is shared across users?
            tmp2 = None
            if download_cache:
                # set up the cache and download into it
                os.mkdir(cache_name)
                fname = os.path.join(cache_name, filename)
                if filename != "cache.ini":
                    now = datetime.datetime.utcnow()
                    cache_ini = open(os.path.join(cache_name, "cache.ini"), "w")
                    print >>cache_ini, "[cache]"
                    print >>cache_ini, "download_url =", url
                    print >>cache_ini, "retrieved =", now.isoformat() + "Z"
                    cache_ini.close()
                logging.getLogger(name).debug(
                    'Cache download %s as %s' % (url, cache_name))
            else:
                # use tempfile
                tmp2 = tempfile.mkdtemp('buildout-' + name)
                fname = os.path.join(tmp2, filename)
                logging.getLogger(name).info('Downloading %s' % url)
            open(fname, 'wb').write(urllib2.urlopen(url).read())
        except:
            if tmp2 is not None:
               shutil.rmtree(tmp2)
            if download_cache:
               shutil.rmtree(cache_name)
            raise

    return fname
