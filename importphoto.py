#!/usr/bin/env python

from optparse import OptionParser
from ConfigParser import ConfigParser
import sys
import os.path
from gi.repository import GExiv2
import datetime
import shutil

# Defaults
defaults = {
    'srcdir':'.',
    'destdir':'.',
    'extensions':'jpg,jpeg,mpg,avi,png,gif',
    'move':False,
}

DEF_CFG_FILE = '~/.importphoto'

exifKeys = ['Exif.Image.DateTime', 'Exif.Photo.DateTimeDigitized', 'Exif.Photo.DateTimeOriginal']

# parse arguments
parser = OptionParser(usage="usage: %prog [options] srcdir destdir", version="%prog 0.1")
parser.add_option("-c", "--cfgfile", metavar = "FILE", dest = "cfgFile", default = DEF_CFG_FILE,
    help = "Configuration file to be used instead of the default one")
parser.add_option("-e", "--extensions", metavar = "LIST", dest = "extensions", default = None,
    help = "List of comma separated extensions to proceed")
parser.add_option("-m", "--move", action = "store_true", dest = "move", default = defaults['move'], help = "Files will be moved instead of copied (aka delete after copy)")

options, args = parser.parse_args()
if len(args) != 2:
    parser.error("incorrect number of arguments")

srcDir = args[0]
destDir = args[1]

### Expand all the paths
srcDir = os.path.expanduser(srcDir)
destDir = os.path.expanduser(destDir)

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
    exif = GExiv2.Metadata(f)
    exifKey = ''
    for ek in exifKeys:
        if ek in exif:
            exifKey = ek
            break
    if exifKey == '':
        # No exif date has been found, try general processing
        return general_processing(f)
    # We have found the exif key containing a date of the picture creation
    return exif[exifKey].split(' ')[0].split(':')

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

### Copy/move a file
def copy_move(f, dt, destDir, move):
    # Parse date
    year, month, day = dt
    # Check whether we have the destination directory
    try:
        destPath = destDir + '/' + year + '/' + month + '/' + day
        os.makedirs(destPath, 0755)
    except OSError as e:
        if e.errno != 17: # file exists
            raise
    print 'Copying %s to %s ... ' % (f, destPath), 
    sys.stdout.flush()
    # Check whether the destination file exists
    if os.path.isfile(destPath + '/' + os.path.basename(f)):
        # Do nothing
        print 'ALREADY EXISTS'
        sys.stdout.flush()
    else:
        try:
            if move:
                shutil.move(f, destPath)
            else:
                shutil.copy2(f, destPath)
        except shutil.Error as e:
            print 'FAILED'
            sys.stdout.flush()
            raise
        print 'OK'
        sys.stdout.flush()

### Look for all the files and handle these accordingly ###
for root, dirs, files in os.walk(srcDir):
    for f in files:
        ext = f.split('.')[-1].lower()
        if 'process_' + ext in locals(): # Check whether we have a special handler defined for this extension
            try:
                dt = locals()['process_' + ext](root + '/' + f) # Call the special handler
            except Exception as e:
                print('An error ocured processing file %s - ignoring' % f) 
                raise
            #try:
            copy_move(root + '/' + f, dt, destDir, options.move)
            #except Exception as e:
                #print('An error occured copying/moving file %s - ignoring' % f)
        else:
            # Call a general handler
            #general_processing(root + '/' + f)
            # Ignore the unknown file
            print('Unknown file %s - ignoring' % f)
    
