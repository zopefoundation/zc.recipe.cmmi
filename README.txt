************************************************************
Recipe installing a download via configure/make/make install
************************************************************

The configure-make-make-install recipe automates installation of
configure-based source distribution into buildouts.

.. contents::


SVN version:

  <svn://svn.zope.org/repos/main/zc.recipe.cmmi/trunk#egg=zc.recipe.cmmi-dev>


Options
*******

url
   The URL of a source archive to download

configure-command
   The name of the configure script.

   The option defaults to ``./configure``.

configure-options
   Basic configure options.

   Defaults to a ``--prefix`` option that points to the part directory.

extra_options
   A string of extra options to pass to configure in *addition to* the
   base options.

environment
   Optional environment variable settings of the forme NAME=VALUE.

   Newlines are ignored. Spaces may be included in environment values
   as long as they can't be mistaken for environment settings.  So::

      environment = FOO=bar
                    baz

   Sets the environment variable FOO, but::

      environment = FOO=bar xxx=baz

   Sets 2 environment values, FOO and xxx.

patch
   The name of an optional patch file to apply to the distribution.

patch_options
   Options to supply to the patch command (if a patch file is used).

   This defaults to ``-p0``

shared
   Share the build accross buildouts.

autogen
   The name of a script to run to generate a configure script.

source-directory-contains
   The name of a file in the distribution's source directory.

   This is used by the recipe to determine if it has found the source
   directory. It defaults top "configure".


.. note::

    This recipe is not expected to work in a Microsoft Windows environment.
