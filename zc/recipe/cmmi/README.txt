We have an archive with a demo foo tar ball:

    >>> ls(distros)
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
    buildout: Installing foo
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
    buildout: Updating foo

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
    buildout: Uninstalling foo
    buildout: Installing foo
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
    __buildout_installed__ = /sample-buildout/parts/foo
    ...
    extra_options = -a -b c
    location = /sample-buildout/parts/foo
    ...
