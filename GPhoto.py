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
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

class GPhoto(object):
    def __init__(self, oauth2json = None, oauth2storage = None):
        self.oauth2json = oauth2json
        self.oauth2storage = oauth2storage
        self.store = None
        self.creds = None
        self.service = None

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
            if flags:
                self.creds = oauth2client.tools.run_flow(flow, self.store, flags)
            else:
                self.creds = oauth2client.tools.run(flow, self.store)
            self.store.put(self.creds)
        self.service = discovery.build('drive', 'v2', http = self.creds.authorize(httplib2.Http()))

    def create_dir(self, folder_title, parent_folder = 'root'):
        body = {
            "title": folder_title,
            "parents": [{"id": parent_folder}],
            "mimeType": "application/vnd.google-apps.folder",
        }
        directory = self.service.files().insert(body = body).execute()
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
            return f
        except apiclient.errors.HttpError as error:
            return None

if __name__ == "__main__":
    oauth2json = os.path.expanduser('~/.gp.json')
    oauth2storage = os.path.expanduser('~/.gp')
    gp = GPhoto(oauth2json = oauth2json, oauth2storage = oauth2storage)
    gp.auth()
    d = gp.create_dir("BufGuf")
    #gp.upload_file(os.path.expanduser('~/fscheck.sh'), d['id'])
    gp.upload_file(os.path.expanduser('~/readiness-f23-alpha.txt'), d['id'])
