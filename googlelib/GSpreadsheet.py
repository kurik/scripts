#!/usr/bin/env python3
# -*- coding: utf-8 -*-


try:
    from . import GAuth
except:
    import GAuth
import logging

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/spreadsheets'

class GSpreadsheet(GAuth.GAuth):
    def __init__(self, oauth2json = None, oauth2storage = None, scope = OAUTH2_SCOPE):
        GAuth.GAuth.__init__(self, oauth2json, oauth2storage, scope)
        logging.debug('GSpreadsheet object created')

if __name__ == "__main__":
    spreadsheetid = '1_1ovntMxvt1pFA7IWEcuAEVsUvYknelJpdkt298d7d4'
    logging.basicConfig(level = logging.DEBUG)
    gs = GSpreadsheet(oauth2json = 'GSpreadsheet-test.json', oauth2storage = 'GSpreadsheet-test.store')
    gs.auth()
    data = {'values': [['XYZ', 'BUBUBU', 'JEJEJE']]}
    r = gs.service.spreadsheets().values().append(spreadsheetId = spreadsheetid, range = 'DAILY!A2',
        insertDataOption='INSERT_ROWS', valueInputOption='RAW', body = data).execute()
    result = gs.service.spreadsheets().values().get(spreadsheetId = spreadsheetid, range = 'DAILY!A1:C12').execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            #print('%s, %s, %s' % (row[0], row[1], row[2]))
            print(row)

