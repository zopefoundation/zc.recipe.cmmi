Various tests
=============

This doctest contains misc tests.

Creating the location folder
----------------------------

When the recipe is subclassed, the `location` folder might be created
before `zc.recipe.cmmi` has a chance to create it, so we need to make
sure it checks that the folder does not exists before it is created.
   
In the test below, the `foo` folder is created before the recipe
is launched::

    >>> location = join(sample_buildout, 'parts', 'foo')
    >>> mkdir(location)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ... log-level = DEBUG
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/foo.tgz
    ... """ % (distros))

    >>> print system('bin/buildout')
    Installing...
    ...
    installing foo
    <BLANKLINE>

    >>> import os.path
    >>> os.path.isdir(join(sample_buildout, "parts", "foo"))
    True

Removing the parts folder
-------------------------

As a result of featuring shared builds, the handling of zc.recipe.cmmi's
associated file-system paths is not entirely trivial. Let's make sure that
when not sharing the build, the recipe gets the book-keeping of its part
directory right.

The part's directory is created when the part is installed:

    >>> remove('.installed.cfg')
    >>> rmdir('parts', 'foo')

    >>> print system('bin/buildout')
    Installing...
    ...
    installing foo

    >>> os.path.isdir(join(sample_buildout, "parts", "foo"))
    True

The part's directory is removed when it is no longer needed (e.g. because the
part now uses a shared build or because the part is gone altogether):

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = 
    ... """)

    >>> print system('bin/buildout')
    Uninstalling foo.

    >>> os.path.isdir(join(sample_buildout, "parts", "foo"))
    False

Spaces in environment variables
-------------------------------

Unfortunately, environment option parsing is simplistic and makes it
hard to include spaces.  We allow spaces if the tokens after spaves
aren't of the form NAME=.....


    >>> distros_url = start_server(distros)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = %sfoo.tgz
    ... environment =
    ...   CFLAGS=-I/yyy -I/xxx --x=y 2=1+1 a=b
    ... """ % distros_url)

    >>> print system('bin/buildout'),
    Installing foo.
    foo: Downloading http://localhost/foo.tgz
    foo: Unpacking and configuring
    foo: Updating environment: CFLAGS=-I/yyy -I/xxx --x=y 2=1+1
    foo: Updating environment: a=b
    configuring foo --prefix=/sample_buildout/parts/foo
    echo building foo
    building foo
    echo installing foo
    installing foo
