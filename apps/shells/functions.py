from django.db import models
from django.conf import settings
import sys, zipfile, os, os.path
import shutil


def unzipper(instance):
    '''
    If someone uploads a zip file with type "sndsl",
    try and unzip the file on the server in place.
    '''
    file = instance.file
    if instance.type == 'sndsl':

        # Get the extension - is it a zip?
        parts = str(instance.file).split(".")
        ext = parts[len(parts)-1]

        if ext == "zip":

            # Get the full base path for this file, and the dir the shells live in
            fullpath = os.path.join(settings.MEDIA_ROOT,str(file)) # Ends with .zip filename
            shelldir = os.path.join(settings.MEDIA_ROOT,"upload/shells",instance.page.shell.slug)

            # Start unzipping, creating subdirectories as needed
            fullpathhandle = open(fullpath, 'r')
            zfobj = zipfile.ZipFile(fullpathhandle)
            for name in zfobj.namelist():
                if name.endswith('/'):
                    try: # Don't try to create a directory if it already exists
                        os.mkdir(os.path.join(shelldir, name))
                    except:
                        pass
                else:
                    outfile = open(os.path.join(shelldir, name), 'wb')
                    outfile.write(zfobj.read(name))
                    outfile.close()

            # Now try and delete the original zip file and stub __MACOSX dir if exists.
            try:
                os.remove(fullpath)
            except:
                pass

            try:
                osxjunk = os.path.join(dirname,'__MACOSX')
                shutil.rmtree(osxjunk)
            except:
                pass

