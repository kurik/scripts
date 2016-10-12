#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configargparse
import logging
import re
import os
import sys
from googlelib.GDrive import GDrive
from googlelib.GAuth import parser as GAuthparser
import shutil


CFG_DEFAULT = "~/.config/gcprc"
GOOGLE_FILE = '(g|google|drive|gdrive):'
GOOGLE_FILE_RE = re.compile(GOOGLE_FILE + '(?P<gfile>.*)')
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
DIR_MIME = 'application/vnd.google-apps.folder'


parser = configargparse.ArgumentParser(config_arg_is_required = False, default_config_files = [CFG_DEFAULT],
    description = "Copy a file or files from/to Google drive.", parents=[GAuthparser],
    epilog = "For SRC and DEST arguments the following expression is used to distinguish between a local file and"
    "a file on Google Drive: " + GOOGLE_FILE)
parser.add_argument("files", nargs='+', metavar = "SRC", help = "File(s) to be copied")
parser.add_argument("dest", metavar = "DEST", help = "Destination for the copied file(s)")
parser.add_argument("-c", "--cfg", "--config", "--rc", metavar = "FILE", dest = "config",
    required = False, is_config_file = True, help = "Config file (RC file)")
parser.add_argument("-m", "--move", dest = "move", action = 'store_true', default = False,
    help = "Move file(s) instead of copying.")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", dest = "verbose", action = 'count', default = 0,
    help = "Be verbose. More -v parameters ensures more verbosity.")
group.add_argument("-q", "--quiet", dest = "verbose", action = 'store_const', const = -1, help = "Be quiet. Print only Errors.")
parser.add_argument("-l", "--log", "--logfile", dest = "logfile", metavar = "FILE", default = "-",
    help = "File to log to instead of logging into the stdout.")
parser.add_argument("-i", "--identity", "--credentials", dest = "credentials", metavar = "FILE", default = None,
    required = True, help = "JSON file containing the Google Account credentials.")
parser.add_argument("-s", "--store", "--storefile", dest = "store", metavar = "FILE", default = None,
    required = True, help = "File to store Google Auth info.")

cmdline = parser.parse_args()

# Set the required level of logging
if cmdline.verbose < 0:
    loglevel = logging.ERROR
elif cmdline.verbose == 0:
    loglevel = logging.WARNING
elif cmdline.verbose == 1:
    loglevel = logging.INFO
else:
    loglevel = logging.DEBUG

# Logging into a file
format = '%(asctime)s %(levelname)s[%(module)s] %(message)s'
if cmdline.logfile != "-":
    logging.basicConfig(filename = cmdline.logfile, level = loglevel, format = format)
else:
    logging.basicConfig(level = loglevel, format = format)

# Do authentication
logging.debug('Starting the authentication tovards Google.')
gd = GDrive(cmdline.credentials, cmdline.store, scope = OAUTH2_SCOPE)
gd.auth()
logging.debug('Authentication has been sucesfully finished.')

# Artefacts and attributes
class artefact():
    def __init__(self, fpath, gdrive = None):
        logging.debug('Initializing artefact object for %s' %fpath)
        self.gdrive = gdrive
        m = GOOGLE_FILE_RE.match(fpath)
        self.is_gdrive = (m != None)
        if self.is_gdrive:
            logging.debug('The artefact is a GDrive one: %s' % fpath)
            if gdrive is None:
                raise ValueError('gdrive parameter is required when the artefact %s is on GDrive' % fpath)
            self.fpath = m.group("gfile")
            if self.fpath == '':
                self.fpath = "/"
            self.gdrive = gdrive
        else:
            logging.debug('The artefact is a FileSystem one: %s' % fpath)
            self.fpath = fpath
        self.basename = self.fpath.split('/')[-1]
        self.dirname = "/".join(self.fpath.split('/')[:-1])

    def __unicode__(self):
        return self.fpath

    def __str__(self):
        return self.__unicode__()

    def is_dir(self):
        logging.debug("Checking %s for directory flag" % self.fpath)
        if self.is_gdrive:
            oid = self.gdrive.walk(self.fpath)
            if oid is None:
                return None
            return self.gdrive.is_dir(oid)
        else:
            if not os.path.exists(self.fpath):
                return None
            return os.path.isdir(self.fpath)
            
        


def fs2fs(src, dest, move = False):
    logging.info('Going to %s local file %s to local file %s' % (('copy', 'move')[move], str(src), str(dest)))
    if move:
        shutil.move(str(src), str(dest))
    else:
        shutil.copy(str(src), str(dest))


def fs2gd(src, dest, move = False):
    logging.info('Going to %s local file %s to GDrive %s' % (('copy', 'move')[move], str(src), str(dest)))
    dest.gdrive.upload(str(src), dest.basename, dest.gdrive.walk(dest.dirname))

def gd2gd(src, dest, move = False):
    logging.info('Going to %s GDrive file %s to GDrive %s' % (('copy', 'move')[move], str(src), str(dest)))
    srcdir = src.gdrive.walk(src.dirname)
    srcid = src.gdrive.get_id(src.basename, srcdir)
    destdir = dest.gdrive.walk(dest.dirname)
    src.gdrive.move(srcid, destdir)

def gd2fs(src, dest, move = False):
    logging.info('Going to %s GDrive file %s to local file %s' % (('copy', 'move')[move], str(src), str(dest)))
    src.gdrive.download(str(dest), src.gdrive.walk(str(src)))


def copy_artefact(src, dest, move = False):
    if src.is_gdrive:
        if dest.is_gdrive:
            return gd2gd(src, dest, move)
        else:
            return gd2fs(src, dest, move)
    else:
        if dest.is_gdrive:
            return fs2gd(src, dest, move)
        else:
            return fs2fs(src, dest, move)


# Create the destination artefact
dest = artefact(cmdline.dest, gd)

# Check whether the destination is a directory in case we have more sources
if len(cmdline.files) > 1:
    if not dest.is_dir():
        logging.error('The destionation (DEST) parameter needs to be a directory')
        sys.exit(1)

# Go through all the files to move/copy and proceed
for sf in cmdline.files:
    srcfile = artefact(sf, gd)
    copy_artefact(srcfile, dest, cmdline.move)
