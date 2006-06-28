Recipe for setting up a filestorage
===================================

This recipe can be used to define a file-storage.  It creates 
a ZConfig file-storage database specification that can be used
by other recipes to generate ZConfig configuration files. 

This recipe takes an optional path option.  If none is given, 
it creates and uses a subdirectory of the buildout parts directory
with the same name as the part.

The recipe records a zconfig option for use by other recipes.

We'll show a couple of examples, using a dictionary as a simulated 
buildout object:

    >>> import zc.recipe.filestorage
    >>> buildout = dict(
    ...   buildout = {
    ...      'directory': '/buildout',
    ...      },
    ...   db = {
    ...      'path': 'foo/Main.fs',
    ...      },
    ...   )
    >>> recipe = zc.recipe.filestorage.Recipe(
    ...                   buildout, 'db', buildout['db'])
    
    >>> print buildout['db']['path']
    /buildout/foo/Main.fs

    >>> print buildout['db']['zconfig'],
    <zodb>
      <filestorage>
        path /buildout/foo/Main.fs
      </filestorage>
    </zodb>

    >>> recipe.install()

    >>> import tempfile
    >>> d = tempfile.mkdtemp()
    >>> buildout = dict(
    ...   buildout = {
    ...      'parts-directory': d,
    ...      },
    ...   db = {},
    ...   )

    >>> recipe = zc.recipe.filestorage.Recipe(
    ...                   buildout, 'db', buildout['db'])
    
    >>> print buildout['db']['path']
    /tmp/tmpQo0DTB/db/Data.fs

    >>> print buildout['db']['zconfig'],
    <zodb>
      <filestorage>
        path /tmp/tmpQo0DTB/db/Data.fs
      </filestorage>
    </zodb>
    
    >>> recipe.install()
    
    >>> import os
    >>> os.listdir(d)
    ['db']

To do
-----

- Add support for various file-storage options

- Create a ZODB-configuration recipe that is meant to be a base class
  for storage recipes and provides database-configuration options.
