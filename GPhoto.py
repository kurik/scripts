#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apiclient
import oauth2client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
import httplib2
import oauth2client
import os

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)
except:
    flags = None

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
DIR_MIME = 'application/vnd.google-apps.folder'

class _GPIter(object):
    def __init__(self, keys):
        self.keys = keys
        self.count = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.count < len(self.keys):
            result = self.keys[self.count]
            self.count += 1
            return result
        raise StopIteration
            
class _GPhotoCache(object):
    def __init__(self):
        self.cache = {}
        self.cache['root'] = ("/", "")

    def __len__(self):
        return len(self.cache)

    def __getitem__(self, file_id):
        return self.cache[file_id]

    def __setitem__(self, file_id, value):
        (title, parent_id) = value
        self.cache[file_id] = (title, parent_id)

    def __delitem__(self, file_id):
        del self.cache[file_id]

    def __iter__(self):
        return _GPIter(self.cache.keys())

    def __contains__(self, file_id):
        return file_id in self.cache

    def find(self, title, parent_id):
        for c in self.cache:
            (t, p_id) = self.cache[c]
            if (parent_id == p_id) and (title == t):
                return c
        return None

class GPhoto(object):
    def __init__(self, oauth2json = None, oauth2storage = None):
        self.oauth2json = oauth2json
        self.oauth2storage = oauth2storage
        self.store = None
        self.creds = None
        self.service = None
        self.cache = _GPhotoCache()

    def auth(self, oauth2json = None, oauth2storage = None):
        if oauth2json is not None:
            self.oauth2json = oauth2json
        if oauth2storage is not None:
            self.oauth2storage = oauth2storage
        if self.oauth2json is None:
            raise ValueError('Attribute oauth2json needs to be defined')
        if self.oauth2storage is None:
            raise ValueError('Attribute oauth2storage needs to be defined')

        self.store = Storage(self.oauth2storage)
        self.creds = self.store.get()
        if self.creds is None or self.creds.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(self.oauth2json, OAUTH2_SCOPE)
            if flags is not None:
                self.creds = oauth2client.tools.run_flow(flow, self.store, flags.parse_args())
            else:
                self.creds = oauth2client.tools.run(flow, self.store)
            self.store.put(self.creds)
        self.service = discovery.build('drive', 'v2', http = self.creds.authorize(httplib2.Http()))

    def create_dir(self, folder_title, parent_folder = 'root'):
        # Check whether the directory does not already exists in cache
        dir_id = self.cache.find(folder_title, parent_folder)
        if dir_id is not None:
            dentry = self.cache[dir_id]
            return {
                'id': dir_id,
                'title': dentry[0],
                'parents': [{"id": dentry[1]}],
                'mimeType': DIR_MIME,
            }
        # The directory has not been found in the cache, lets ask Google
        body = {
            "title": folder_title,
            "parents": [{"id": parent_folder}],
            "mimeType": DIR_MIME,
        }
        directory = self.service.files().insert(body = body).execute()
        self.cache[directory['id']] = (folder_title, parent_folder)
        return directory

    def upload_file(self, filename, parent_folder = 'root'):
        media_body = apiclient.http.MediaFileUpload(filename, resumable = True)
        basename = os.path.basename(filename)
        body = {
            "title": basename,
            "parents": [{"id": parent_folder}],
        }
        try:
            f = self.service.files().insert(body = body, media_body = media_body).execute()
            self.cache[f['id']] = (basename, parent_folder)
            return f
        except apiclient.errors.HttpError as error:
            return None

    def get_id(self, path):
        path_list = path.split('/')
        pid = 'root'
        for p in path_list:
            fid = self.get_file_id(p, pid)
            if fid is None:
                return None
            pid = fid
        return fid

    def get_file_id(self, title, parent_id):
        # Try cache
        cache = self.cache.find(title, parent_id)
        if cache is not None:
            return cache
        # Not found in cache - ask Google
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                children = self.service.children().list(folderId = parent_id, **param).execute()
                for child in children.get('items', []):
                    if child['id'] not in self.cache:
                        ch = self.service.files().get(fileId = child['id']).execute()
                        self.cache[ch['id']] = (ch['title'], parent_id)
                        if ch['title'] == title:
                            return child['id']
                page_token = children.get('nextPageToken')
                if not page_token:
                    break
            except apiclient.errors.HttpError as error:
                raise
        return None

    def file_exists(self, file_name, root_dir = 'root'):
        fn = file_name.split('/')
        file_id = self.get_file_id(fn[0], root_dir)
        if len(fn) == 1:
            # Check existence of the file
            return file_id is not None
        # Go one level deeper
        fn.pop(0)
        return self.file_exists('/'.join(fn), file_id)

if __name__ == "__main__":
    oauth2json = os.path.expanduser('~/.gp.json')
    oauth2storage = os.path.expanduser('~/.gp')
    gp = GPhoto(oauth2json = oauth2json, oauth2storage = oauth2storage)
    gp.auth()
    #d = gp.create_dir("BufGuf")
    #gp.upload_file(os.path.expanduser('~/fscheck.sh'), d['id'])
    #gp.upload_file(os.path.expanduser('~/readiness-f23-alpha.txt'), d['id'])
    #print 'U-Temp', gp.file_exists('U-Temp')
    #print 'Work/Links', gp.file_exists('Work/Links')
    #print 'Personal', gp.file_exists('Personal')
    #print 'Personal/Blbost', gp.file_exists('Personal/Blbost')
    #print 'Pictures/Foto/2015/07/29', gp.file_exists('Pictures/Foto/2015/07/29')
    print('Pictures/Foto/2015/07/29/IMG_2552.JPG', gp.file_exists('Pictures/Foto/2015/07/29/IMG_2552.JPG'))
    print('Pictures/Foto/2015/07/29', gp.file_exists('Pictures/Foto/2015/07/29'))
    print('Pictures/Foto/2015/07/29/', gp.file_exists('Pictures/Foto/2015/07/29/'))
    print('Pictures/Foto/2015/07/29/IMG_2552.jpg', gp.file_exists('Pictures/Foto/2015/07/29/IMG_2552.jpg'))
    print('Pictures/Foto/2015/07/29/IMG2552.JPG', gp.file_exists('Pictures/Foto/2015/07/29/IMG2552.JPG'))
