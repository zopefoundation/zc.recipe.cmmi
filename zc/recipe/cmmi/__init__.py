import logging, os

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        path = options.get('path')
        if path is None:
            path = os.path.join(buildout['buildout']['parts-directory'],
                                self.name, 'Data.fs')
            self.make_part = True
        else:
            path = os.path.join(buildout['buildout']['directory'], path)
            if not os.path.exists(path):
                logging.getLogger('zc.recipe.filestorage').error(
                    "%s does not exixt", path)
            self.make_part = False
            
        options['path'] = path
        options['zconfig'] = template % path

    def install(self):
        if self.make_part:
            part = os.path.dirname(self.options['path'])
            if not os.path.exists(part):
                os.mkdir(part)

template = """\
<zodb>
  <filestorage>
    path %s
  </filestorage>
</zodb>
"""
