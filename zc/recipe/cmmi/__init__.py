import logging, os, shutil, tempfile, urllib2, urlparse

def system(c):
    if os.system(c):
        raise SystemError("Failed", c)

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        options['dest'] = os.path.join(buildout['buildout']['parts-directory'],
                                       self.name)

    def install(self):
        dest = self.options['dest']
        if os.path.exists(dest):
            return dest # already there

        url = self.options['url']
        f = urllib2.urlopen(url)
        _, _, urlpath, _, _, _ = urlparse.urlparse(url)
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        try:
            for suffix, handler in extractors.items():
                if urlpath.endswith(suffix):
                    handler(f, tmp)
                    break
            else:
                raise ValueError("Don't know how to expand", urlpath)
            

            os.mkdir(dest)
            here = os.getcwd()
            try:
                os.chdir(tmp)
                if not os.path.exists('configure'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find configure")
                    
                system("./configure --prefix="+dest)
                system("make")
                system("make install")
            except:
                os.chdir(here)
                os.rmdir(dest)
                raise

        finally:
            shutil.rmtree(tmp)

        return dest

def tar(stream, path, mode='r|'):
    import tarfile
    t = tarfile.open(mode=mode, fileobj=stream)
    while 1:
        info = t.next()
        if info is None:
            t.close()
            return
        t.extract(info, path)
    
def tgz(stream, path):
    return tar(stream, path, 'r|gz')
    
def tbz(stream, path):
    return tar(stream, path, 'r|bz2')
        
extractors = {
    '.tar': tar,
    '.tgz': tgz,
    '.tar.gz': tgz,
    '.tar.bz2': tbz,
    #'.zip': zip,
    }

                
