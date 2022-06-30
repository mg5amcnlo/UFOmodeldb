import os
devnull = open(os.devnull,'w')
import subprocess as subproc
import shutil
import sys

################################################################################
# class to change directory with the "with statement"
# Exemple:
# with chdir(path) as path:
#     pass
################################################################################
class chdir:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def validate_UFO_link(link, name="unknow"):
    """download the model/check the validity
       return the name of the UFO model if find one
       return False if the link is not in a good format"""
    
    # create tmp directory to avoid side effect
    try:
        shutil.rmtree('tmp')
    except Exception as  error:
        print(error)
        pass
    os.mkdir('tmp')
    
    with chdir('tmp'):
        #download the file
        if link.startswith('http'):
            if sys.platform == "darwin":
                subproc.call(['curl', link, '-otmp.tgz'], stdout=devnull, stderr=devnull)
            else:
                subproc.call(['wget', link, '--output-document=tmp.tgz'],stdout=devnull, stderr=devnull)
        elif link.startswith('./'):
            shutil.copy(os.path.join('..', link), 'tmp.tgz')
            
        #untar the file
        # .tgz
        if link.endswith(('.tgz','.tar.gz','.tar', '.tar.2.gz')):
            try:
                proc = subproc.call('tar -xzpvf tmp.tgz', shell=True, stdout=devnull, stderr=devnull)
                if proc: 
                    raise Exception('can not untar %s!' %name)
            except:
                try:
                    proc = subproc.call('tar -xpvf tmp.tgz', shell=True, stdout=devnull, stderr=devnull)
                    if proc:
                        print('fail to download %s:%s' % (name, link))
                        return False
                except:
                    return False
        # .zip
        elif link.endswith(('.zip')):
            try:
                proc = subproc.call('unzip tmp.tgz', shell=True, stdout=devnull, stderr=devnull)
                if proc: 
                    print('fail to download %s:%s' % (name, link))
                    return False
            except:
                try:
                    subproc.call('tar -xzpvf tmp.tgz', shell=True, stdout=devnull, stderr=devnull)
                except:
                    print("Fail for ", link)
                    return False
        else:
            print('unknow format for %s:%s' %(name,link))
            return False
            #raise Exception, 'unknow format'
    
        #check if the model seems valid
        listdir = os.listdir('.')
        if 'tmp.tgz' in listdir:
            listdir.remove('tmp.tgz')
        if '__MACOSX' in listdir:
            listdir.remove('__MACOSX')
        listdir = [ent for ent in listdir if not ent.startswith('.')]
        if len(listdir) != 1:
            print(link, "has too manyfile (not a single directory)", listdir)
            return False
        name = listdir.pop()
        
        if os.path.exists('%s/__init__.py' % name) and os.path.exists('%s/particles.py' % name):
            return name
        elif os.path.exists('%s/interactions.dat' % name):
            return name
        else: 
            print('fail to have valid UFO for', link, 'named found', name)
            return False

if __name__ == "__main__":

    authors = {}
    email = {} 
    names = {}
    pwd= os.getcwd()
    
    if 'server_path' in os.environ:
        server_path = os.path.join(os.environ['server_path'], 'Downloads', 'models')
    else: 
        server_path = './'
    
    for line in open('model_database.dat'):
        os.chdir(pwd)
        split = line.split()
        if len(split) == 2:
            name, link = split
        elif len(split) ==1:
            link = line.strip()
        else:
            continue
        
        name = validate_UFO_link(link, name=name)
        if not name:
            continue
        
        if name in names:
            print('WARNING: multiple model using the name %s: \n%s \n %s' % (name, link, names[name]))
        else:
            if link.startswith('./'):
                link = server_path +'/'+ link[2:]
            names[name] = link
    
    #    if os.path.exists('%s/__init__.py' % name) and os.path.exists('%s/particles.py' % name):
    #        names[name] = link
    #    elif os.path.exists('%s/interactions.dat' % name) and '_v4' in name:
    #        names[name] = link
    
        os.chdir('..')
    
    
    fsock = open('%s/new_model_db.dat' % pwd ,'w')
    for key, link in list(names.items()):
        fsock.write('%s\t\t\t%s\n' % (key,link)) 
    
    #fsock = open('import.dat','w')
    #for key, link in names.items():
    #    fsock.write('import model %s\n' % key)
