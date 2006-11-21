The configure-make-make-install recipe automates installation of
traditional configure-based source distribution into buildouts.

The only option is the url option which gives the location of a source
archive.   We have an archive with a demo foo tar ball:

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

We used the URL option to specify the location of the archive.

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

