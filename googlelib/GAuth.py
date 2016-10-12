#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import oauth2client.client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
import httplib2
import logging

parser = tools.argparser

class GAuth(object):
    def __init__(self, oauth2json = None, oauth2storage = None, scope = None):
        self.oauth2json = oauth2json
        self.oauth2storage = oauth2storage
        self.scope = scope
        self.store = None
        self.creds = None
        self.service = None
        logging.debug('GAuth object created')

    def auth(self, oauth2json = None, oauth2storage = None, scope = None):
        if oauth2json is not None:
            self.oauth2json = oauth2json
        if oauth2storage is not None:
            self.oauth2storage = oauth2storage
        if scope is not None:
            self.scope = scope
        if self.oauth2json is None:
            raise ValueError('Attribute oauth2json needs to be defined')
        if self.oauth2storage is None:
            raise ValueError('Attribute oauth2storage needs to be defined')
        if self.scope is None:
            raise ValueError('Attribute scope needs to be defined')

        logging.debug('Authenticating to Google, using json(%s) and store(%s)' % (self.oauth2json, self.oauth2storage))
        self.store = Storage(self.oauth2storage)
        self.creds = self.store.get()
        if self.creds is None or self.creds.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(self.oauth2json, self.scope)
            self.creds = oauth2client.tools.run_flow(flow, self.store, parser.parse_args())
            self.store.put(self.creds)
        if 'spreadsheets' in self.scope.lower():
            logging.debug('Authenticating as sheets')
            discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
            self.service = discovery.build('sheets', 'v4', http = self.creds.authorize(httplib2.Http()),
                discoveryServiceUrl = discoveryUrl)
        else:
            logging.debug('Authenticating as drive')
            self.service = discovery.build('drive', 'v3', http = self.creds.authorize(httplib2.Http()))
        logging.debug('Authentication to Google is done')

