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

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import datetime
try:
    from hashlib import sha1
except ImportError: # Python < 2.5
    from sha import new as sha1
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
            if not os.path.isdir(self.download_cache):
                os.mkdir(self.download_cache)

        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        options['location'] = os.path.join(location, name)

        self.url = self.options['url']
        extra_options = self.options.get('extra_options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        self.extra_options = ' '.join(extra_options.split())

        self.autogen = self.options.get('autogen', '')

        self.patch = self.options.get('patch', '')
        self.patch_options = self.options.get('patch_options', '-p0')

        self.environ = self.options.get('environment', '').split()
        if self.environ:
            self.environ = dict([x.split('=', 1) for x in self.environ])
        else:
            self.environ = {}

        self.shared = options.get('shared', None)
        if self.shared:
            if os.path.isdir(self.shared):
                # to prevent nasty surprises, don't use the directory directly
                # since we remove it in case of build errors
                self.shared = os.path.join(self.shared, 'cmmi')
            else:
                if not self.download_cache:
                    raise ValueError(
                        "Set the 'shared' option of zc.recipe.cmmi to an existing"
                        " directory, or set ${buildout:download-cache}")

                self.shared = os.path.join(
                    directory, self.download_cache, 'build')
                if not os.path.isdir(self.shared):
                    os.mkdir(self.shared)
                self.shared = os.path.join(self.shared, self._state_hash())

            options['location'] = self.shared

    def _state_hash(self):
        # hash of our configuration state, so that e.g. different
        # ./configure options will get a different build directory
        env = ''.join(['%s%s' % (key, value) for key, value
                       in self.environ.items()])
        state = [self.url, self.extra_options, self.autogen,
                 self.patch, self.patch_options, env]
        return sha1(''.join(state)).hexdigest()

    def install(self):
        logger = logging.getLogger(self.name)

        if self.shared:
            if os.path.isdir(self.shared):
                logger.info('using existing shared build')
                return self.shared
            else:
                os.mkdir(self.shared)

        dest = self.options['location']
        here = os.getcwd()
        if not os.path.exists(dest):
            os.mkdir(dest)

        fname, is_temp = getFromCache(
            self.url, self.name, self.download_cache, self.install_from_cache)

        try:
            # now unpack and work as normal
            tmp = tempfile.mkdtemp('buildout-'+self.name)
            logger.info('Unpacking and configuring')
            setuptools.archive_util.unpack_archive(fname, tmp)
        finally:
            if is_temp:
                os.remove(fname)

        for key, value in self.environ.items():
            logger.info('Updating environment: %s=%s' % (key, value))
        os.environ.update(self.environ)

        try:
            os.chdir(tmp)
            try:
                if not (os.path.exists('configure') or
                        os.path.exists(self.autogen)):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                if self.patch is not '':
                    # patch may be a filesystem path or url
                    # url patches can go through the cache
                    if urlparse.urlparse(self.patch, None)[0] is not None:
                        self.patch, is_temp = getFromCache(
                            self.patch, self.name, self.download_cache,
                            self.install_from_cache)
                    try:
                        system(
                            "patch %s < %s" % (self.patch_options, self.patch))
                    finally:
                        if is_temp:
                            os.remove(self.patch)
                if self.autogen is not '':
                    logger.info('auto generating configure files')
                    system("./%s" % self.autogen)
                if not os.path.exists('configure'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find configure")
                system("./configure --prefix=%s %s" %
                       (dest, self.extra_options))
                system("make")
                system("make install")
                shutil.rmtree(tmp)
            finally:
                os.chdir(here)
        except:
            if os.path.exists(tmp):
                logger.error("cmmi failed: %s", tmp)
            shutil.rmtree(dest)
            raise

        return dest

    def update(self):
        pass


def getFromCache(url, name, download_cache=None, install_from_cache=False):
    if download_cache:
        cache_fname = sha1(url).hexdigest()
        cache_name = os.path.join(download_cache, cache_fname)

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
                fd, tmp2 = tempfile.mkstemp('buildout-' + name)
                os.close(fd)
                fname = tmp2
                logging.getLogger(name).info('Downloading %s' % url)
            open(fname, 'wb').write(urllib2.urlopen(url).read())
        except:
            if tmp2 is not None:
               os.remove(tmp2)
            if download_cache:
               shutil.rmtree(cache_name)
            raise

    return fname, bool(tmp2)
