from setuptools import setup, find_packages

name = "zc.recipe.filestorage"
setup(
    name = name,
    version = "1.0",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for defining a file-storage",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3",
    url='http://svn.zope.org/'+name,

    packages = find_packages(),
    include_package_data = True,
    data_files = [('.', ['README.txt'])],
    namespace_packages = ['zc', 'zc.recipe'],
    install_requires = ['zc.buildout', 'zope.testing', 'setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    )
