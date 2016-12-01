#!/usr/bin/env python3

import sys
import os.path
try:
    import gi
    gi.require_version('GExiv2', '0.10')
    from gi.repository import GExiv2
    exifAvailable = True
except ImportError:
    exifAvailable = False
except ValueError:
    exifAvailable = False

import datetime
import shutil
import GPhoto
import argparse
import re

# Defaults
defaults = {
    'srcdir':'.',
    'destdir':'.',
    'extensions':'jpg,jpeg,mpg,avi,png,gif',
    'move': False,
    'gdrive': False,
}

DEF_CFG_FILE = '~/.importphoto'

#exifKeys = ['Exif.Image.DateTime', 'Exif.Photo.DateTimeDigitized', 'Exif.Photo.DateTimeOriginal']
exifKeys = ['Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized', 'Exif.Image.DateTime']

# parse arguments
#parser = argparse.ArgumentParser(parents = [GPhoto.flags])
parser = GPhoto.flags
parser.add_argument("-e", "--extensions", metavar = "LIST", dest = "extensions", default = None,
    help = "List of comma separated extensions to proceed")
parser.add_argument("-t", "--test", action = "store_true", dest = "test", default = False, help = "Runs in test (dry-run) mode")
parser.add_argument("-f", "--force", action = "store_true", dest = "force", default = False, help = "Copy/move file even it exists at the desination")
parser.add_argument("-N", "--No time stamp resolving", action = "store_true", dest = "notimestamp", default = False, help = "Do notparse timestamp of the uploaded file. Use the destdir as the destination instead.")
parser.add_argument("-g", "--gdrive", action = "store_true", dest = "gdrive", default = defaults['gdrive'], help = "Files will be copied/moved to GDrive instead of to the local filesystem.")
parser.add_argument("-m", "--move", action = "store_true", dest = "move", default = defaults['move'], help = "Files will be moved instead of copied (aka delete after copy)")
parser.add_argument("srcdir", help = "Source directory of photos")
parser.add_argument("destdir", help = "Destination directory of photos")

cmdline = parser.parse_args()

### Expand all the paths
srcDir = os.path.expanduser(cmdline.srcdir)
destDir = os.path.expanduser(cmdline.destdir)

# Connect to GDrive
gdrive = None
if cmdline.gdrive:
    oauth2json = os.path.expanduser('~/.gp.json')
    oauth2storage = os.path.expanduser('~/.gp')
    gdrive = GPhoto.GPhoto(oauth2json = oauth2json, oauth2storage = oauth2storage)
    gdrive.auth()

### Definition of handlers for extensions ###
# PNG
def process_png(f):
    return process_jpg(f)
# 3gp
def process_3gp(f):
    return general_processing(f)
# JPEG
def process_jpeg(f):
    return process_jpg(f)
# JPG
def process_jpg(f):
    expr = re.compile('(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)-(?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d)\.')
    m = expr.match(os.path.basename(f))
    if m is None:
        # The filename does not match YYYMMDD-HHMMSS convention try Exif
        exifKey = ''
        if exifAvailable:
            exif = GExiv2.Metadata()
            try:
                exif.open_path(f)
            except:
                return general_processing(f)
            for ek in exifKeys:
                if ek in exif:
                    exifKey = ek
                    break
        if exifKey == '':
            # No exif date has been found, try general processing
            return general_processing(f)
        # We have found the exif key containing a date of the picture creation
        return exif[exifKey].split(' ')[0].split(':')
    else:
        return (m.group('year'), m.group('month'), m.group('day'))

# MPG
def process_mpg(f):
    return general_processing(f)
# AVI
def process_avi(f):
    return general_processing(f)
# MOV
def process_mov(f):
    return general_processing(f)

# General handler
def general_processing(f):
    dt=os.path.getmtime(f)
    d = datetime.datetime.fromtimestamp(dt)
    return ('%04d' % d.year, '%02d' % d.month, '%02d' % d.day)

def gdrive_makedirs(destPath, parent_id = 'root'):
    dPath = destPath.split('/')
    pid = parent_id
    for d in dPath:
        fid = gdrive.get_file_id(d, pid)
        if fid is None:
            directory = gdrive.create_dir(d, pid)
            pid = directory['id']
        else:
            pid = fid

def file_exists(filename):
    if cmdline.force:
        return False
    if cmdline.gdrive:
        return gdrive.file_exists(filename)
    else:
        return os.path.exists(filename)

### Copy/move a file
def copy_move(f, dt, destDir, move):
    # Parse date
    if dt is None:
        year, month, day = ('', '', '')
    else:
        year, month, day = dt
    # Check whether we have the destination directory
    try:
        destPath = destDir + '/' + year + '/' + month + '/' + day
        destPath = '/'.join([ x for x in destPath.split('/') if x != ''])
        if not file_exists(destPath):
            print('Creating directory:', destPath, '...', end='')
            sys.stdout.flush()
            if cmdline.gdrive:
                if not cmdline.test:
                    gdrive_makedirs(destPath)
            else:
                if not cmdline.test:
                    os.makedirs(destPath, 0o755)
            print('OK')
            sys.stdout.flush()
    except OSError as e:
        if e.errno != 17: # file exists
            print('FAILED')
            sys.stdout.flush()
            raise
    print('Copying %s to %s ... ' % (f, destPath), end="")
    sys.stdout.flush()
    # Check whether the destination file exists
    if file_exists(destPath + '/' + os.path.basename(f)):
        # Do nothing
        print('ALREADY EXISTS')
        sys.stdout.flush()
    else:
        if cmdline.gdrive:
            did = gdrive.get_id(destPath)
            if did is None:
                print('FAILED')
                sys.stdout.flush()
                return
        try:
            if move:
                if not cmdline.test:
                    if cmdline.gdrive:
                        fh = gdrive.upload_file(f, did)
                        if fh is not None:
                            print('Removing the source file: %s ... ' % f, end = '')
                            os.remove(f)
                    else:
                        shutil.move(f, destPath)
            else:
                if not cmdline.test:
                    if cmdline.gdrive:
                        gdrive.upload_file(f, did)
                    else:
                        shutil.copy2(f, destPath)
        except shutil.Error as e:
            print('FAILED')
            sys.stdout.flush()
            raise
        print('OK')
        sys.stdout.flush()

def treat_file(f, root = ''):
    if root != '':
        if root[-1] != '/':
            root += '/'
    if cmdline.notimestamp:
        copy_move(root + f, None, destDir, cmdline.move)
    else:
        ext = f.split('.')[-1].lower()
        if 'process_' + ext in globals(): # Check whether we have a special handler defined for this extension
            try:
                dt = globals()['process_' + ext](root + f) # Call the special handler
            except Exception as e:
                print('An error ocured processing file %s - ignoring' % f)
                raise
            copy_move(root + f, dt, destDir, cmdline.move)
        else:
            print('Unknown file %s - ignoring' % f)

### Look for all the files and handle these accordingly ###
if os.path.isfile(srcDir):
    treat_file(srcDir)
else:
    for root, dirs, files in os.walk(srcDir):
        for f in files:
            treat_file(f, root)
