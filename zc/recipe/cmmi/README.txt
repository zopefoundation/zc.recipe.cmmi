We have an archive with a demo foo tar ball:

    >>> ls(distros)
    -  bar.tgz
    -  foo.tgz

Let's update a sample buildout to installs it:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/foo.tgz
    ... """ % distros)

We used the url option to specify the location of the archive.

If we run the buildout, the configure script in the archive is run.
It creates a make file which is also run:

    >>> print system('bin/buildout'),
    Installing foo.
    foo: Downloading .../distros/foo.tgz
    foo: Unpacking and configuring
    configuring foo --prefix=/sample-buildout/parts/foo
    echo building foo
    building foo
    echo installing foo
    installing foo

The recipe also creates the parts directory:

    >>> ls(sample_buildout, 'parts')
    d  foo

If we run the buildout again, the update method will be called, which
does nothing:

    >>> print system('bin/buildout'),
    Updating foo.

You can supply extra configure options:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/foo.tgz
    ... extra_options = -a -b c
    ... """ % distros)

    >>> print system('bin/buildout'),
    Uninstalling foo.
    Installing foo.
    foo: Downloading .../distros/foo.tgz
    foo: Unpacking and configuring
    configuring foo --prefix=/sample-buildout/parts/foo -a -b c
    echo building foo
    building foo
    echo installing foo
    installing foo

The recipe sets the location option, which can be read by other
recipes, to the location where the part is installed:

    >>> cat('.installed.cfg')
    ... # doctest: +ELLIPSIS
    [buildout]
    installed_develop_eggs = 
    parts = foo
    <BLANKLINE>
    [foo]
    __buildout_installed__ = /sample_buildout/parts/foo
    ...
    extra_options = -a -b c
    location = /sample_buildout/parts/foo
    ...

It may be necessary to set some environment variables when running configure
or make. This can be done by adding an environment statement:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/foo.tgz
    ... environment =
    ...   CFLAGS=-I/usr/lib/postgresql7.4/include
    ... """ % distros)


    >>> print system('bin/buildout'),
    Uninstalling foo.
    Installing foo.
    foo: Downloading .../distros/foo.tgz
    foo: Unpacking and configuring
    foo: Updating environment: CFLAGS=-I/usr/lib/postgresql7.4/include
    configuring foo --prefix=/sample_buildout/parts/foo
    echo building foo
    building foo
    echo installing foo
    installing foo

Sometimes it's necessary to patch the sources before building a package.
You can specify the name of the patch to apply and (optional) patch options:

First of all let's write a patchfile:

    >>> import sys
    >>> mkdir('patches')
    >>> write('patches/config.patch',
    ... """--- configure
    ... +++ /dev/null
    ... @@ -1,13 +1,13 @@
    ...  #!%s
    ...  import sys
    ... -print "configuring foo", ' '.join(sys.argv[1:])
    ... +print "configuring foo patched", ' '.join(sys.argv[1:])
    ...
    ...  Makefile_template = '''
    ...  all:
    ... -\techo building foo
    ... +\techo building foo patched
    ...
    ...  install:
    ... -\techo installing foo
    ... +\techo installing foo patched
    ...  '''
    ...
    ...  open('Makefile', 'w').write(Makefile_template)
    ...
    ... """ % sys.executable)

Now let's create a buildout.cfg file. Note: If no patch option is beeing
passed, -p0 is appended by default.

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/foo.tgz
    ... patch = ${buildout:directory}/patches/config.patch
    ... patch_options = -p0
    ... """ % distros)

    >>> print system('bin/buildout'),
    Uninstalling foo.
    Installing foo.
    foo: Downloading .../distros/foo.tgz
    foo: Unpacking and configuring
    patching file configure
    configuring foo patched --prefix=/sample_buildout/parts/foo
    echo building foo patched
    building foo patched
    echo installing foo patched
    installing foo patched

It is possible to autogenerate the configure files:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.cmmi
    ... url = file://%s/bar.tgz
    ... autogen = autogen.sh
    ... """ % distros)

    >>> print system('bin/buildout'),
    Uninstalling foo.
    Installing foo.
    foo: Downloading .../distros/bar.tgz
    foo: Unpacking and configuring
    foo: auto generating configure files
    configuring foo --prefix=/sample_buildout/parts/foo
    echo building foo
    building foo
    echo installing foo
    installing foo
