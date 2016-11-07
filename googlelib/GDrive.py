#!/usr/bin/env python3
# -*- coding: utf-8 -*-


try:
    from . import GAuth
    from . import GCache
except:
    import GAuth
    import GCache
import logging
import os
import apiclient
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
import time

DIR_MIME = 'application/vnd.google-apps.folder'
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Number of bytes to send/receive in each request.
CHUNKSIZE = 2 * 1024 * 1024
# Mimetype to use if one can't be guessed from the file extension.
DEFAULT_MIMETYPE = 'application/octet-stream'


class GDrive(GAuth.GAuth):
    def __init__(self, oauth2json = None, oauth2storage = None, scope = OAUTH2_SCOPE):
        GAuth.GAuth.__init__(self, oauth2json, oauth2storage, scope)
        self.cache = GCache.GCache()
        logging.debug('GDrive object created')

    def get_id_from_cache(self, name, parent_folder = 'root'):
        # Check whether an object does not already exists in cache
        return self.cache[(name, parent_folder)]

    def get_id_from_gdrive(self, name, parent_folder = 'root'):
        logging.info('Fetching metadata for %s in %s' % (name, parent_folder))
        q = "name='%s' and '%s' in parents" % (name, parent_folder)
        logging.debug("Google Drive query: %s" % q)
        param = {
            'q' : q,
            'fields' : 'files(id)',
        }
        response = self.service.files().list(**param).execute()
        id = response['files'][0]['id']
        logging.debug('Data fetched: %s', response['files'])
        # Save to the cache
        self.cache[id] = (name, parent_folder)
        return id

    def get_id(self, name, parent_folder = 'root'):
        # Try if it exists in cache
        try:
            return self.get_id_from_cache(name, parent_folder)
        except:
            pass
        # Try if it exists in GDrive
        try:
            return self.get_id_from_gdrive(name, parent_folder)
        except IndexError:
            raise KeyError('"%s" in "%s"' % (name, parent_folder))

    def is_dir(self, object_id):
        logging.debug('Fetching metadata for %s' % (object_id,))
        response = self.service.files().get(fileId = object_id, fields = 'mimeType').execute()
        logging.debug('mimeType of the object: %s' % response.get('mimeType'))
        return response.get('mimeType') == DIR_MIME
        

    def mkdir(self, folder_title, parent_folder = 'root'):
        try:
            return self.get_id(folder_title, parent_folder)
        except:
            pass
        # Looks like there is no such directory yet, so let's create it
        body = {
            "name": folder_title,
            "parents": [{"id": parent_folder}],
            "mimeType": DIR_MIME,
        }
        directory = self.service.files().create(body = body).execute()
        did = directory['id']
        logging.debug('Directory %s in %s has been created as ID %s' % (folder_title, parent_folder, did))
        self.cache[did] = (folder_title, parent_folder)
        return did
        
    def rm(self, object_id):
        logging.info("Removing an object with id %s" % object_id)
        try:
            self.service.files().delete(fileId=object_id).execute()
            logging.debug("Object with id %s has been sucesfully removed" % object_id)
        except e:
            logging.error("Removal of object id %s has failed: %s" % (object_id, str(e)))
            raise
        try:
            del self.cache[object_id]
        except:
            pass

    def ls(self, folder_id = 'root'):
        logging.info('Fetching metadata for %s' % (folder_id,))
        q = "'%s' in parents" % (folder_id,)
        logging.debug("Google Drive query: %s" % q)
        param = {
            'q' : q,
            'fields' : 'files(id,name)',
        }
        response = self.service.files().list(**param).execute()
        ids = list()
        for o in response['files']:
            # Save to the cache
            self.cache[o['id']] = (o['name'], folder_id)
            # Append the id to the final list
            ids.append(o['id'])
        logging.debug('Fetched: %s objects', len(ids))
        return id
            
    def upload(self, filename, gdrivename = None, parent_folder = 'root'):
        logging.debug('Going to upload file to GDrive. filename=%s , gdrivename=%s , parent_folder=%s' % (filename, gdrivename, parent_folder))
        # Convert the name of the file on GDrive in case it is not provided
        if gdrivename is None or gdrivename == '':
            gdrivename = filename.split('/')[-1]
        # Check whether the file does not already exists
        try:
            self.get_id(gdrivename, parent_folder)
        except:
            pass
        else:
            logging.error("The file to upload %s already exists" % gdrivename)
            raise FileExistsError(gdrivename)
        # Prepare for the file upload
        logging.debug("Creating the media object for uploading from %s" % filename)
        media = MediaFileUpload(filename, chunksize = CHUNKSIZE, resumable = True)
        if not media.mimetype():
            logging.debug("MIME type of the file has not been recognized, using the default %s" % DEFAULT_MIMETYPE)
            media = MediaFileUpload(filename, mimeType = DEFAULT_MIMETYPE, chunksize = CHUNKSIZE, resumable = True)
        body = {
            'name': gdrivename,
            #'parents': [{"id": parent_folder}],
            'parents': [parent_folder],
        }
        logging.debug('Starting upload of the %s file as %s' % (filename, gdrivename))
        request = self.service.files().create(body = body, media_body = media, fields='id')
        retry = 5
        while retry > 0:
            try:
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        logging.info("Uploaded %d%%." % int(status.progress() * 100))
                logging.info("Upload has been completed")
                # No need for a retry
                retry = -1
            except apiclient.errors.HttpError as e:
                if e.resp.status in [404]:
                    # Start the upload all over again.
                    request = self.service.files().create(body = body, media_body = media, fields='id')
                elif e.resp.status in [500, 502, 503, 504]:
                    # Call next_chunk() again, but use an exponential backoff for repeated errors.
                    logging.warning('Upload of a chunk has failed, retrying ...')
                    retry -= 1
                    time.sleep(3)
                else:
                    # Do not retry. Log the error and fail.
                    logging.error('The upload has failed: %s' % str(e))
                    raise
        if retry == 0:
            logging.error('The upload has failed.')
            raise ConnectionError
        fid = response.get('id')
        self.cache[fid] = (gdrivename, parent_folder)
        return fid

    def move(self, object_id, folder_id = 'root'):
        logging.debug("Copying an object with id %s to a folder with id %s" % (object_id, folder_id))
        # Retrieve the existing parents to remove
        f = self.service.files().get(fileId = object_id, fields = 'parents').execute()
        previous_parents = ",".join(f.get('parents'))
        # Move the file to the new folder
        f = self.service.files().update(fileId = object_id,
            addParents = folder_id,
            removeParents = previous_parents,
            fields = 'id').execute()
        logging.info("Object with id %s has been sucesfully copied to a folder with id %s" % (object_id, folder_id))
        return f.get('id')

    def download(self, filename, object_id):
        logging.debug('Starting download of object %s to %s' % (object_id, filename))
        with open(filename, 'wb') as fd:
            request = self.service.files().get_media(fileId = object_id)
            downloader = MediaIoBaseDownload(fd, request, chunksize = CHUNKSIZE)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logging.info("Download %d%%." % int(status.progress() * 100))
        logging.info('Object %s has been downloaded as %s' % (object_id, filename))

    def walk(self, path):
        logging.debug('Walking through %s' % path)
        dirs = path.split('/')
        dirs = [d for d in dirs if d != '']
        if len(dirs) == 0:
            return 'root'
        dirs = ['root'] + dirs
        index = 1
        oid = None
        while index < len(dirs):
            logging.debug('Diving into %s/%s' % (dirs[index - 1], dirs[index]))
            try:
                oid = self.get_id(dirs[index], dirs[index - 1])
            except KeyError as e:
                logging.info('The artefact has not been found')
                return None
            dirs[index] = oid
            index += 1
        logging.info('The artefact has been found as OID=%s' % oid)
        return oid

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s %(levelname)s[%(module)s] %(message)s')
    gd = GDrive(oauth2json = '/home/jkurik/.gp.json', oauth2storage = '/home/jkurik/.gp')
    gd.auth()
    dname = "Nazdarek ke smazani"
    did = gd.mkdir(dname)
    #print("ID of a new object:", gd.get_id_from_gdrive(dname))
    #print("ID of a new object in a cache:", gd.get_id_from_cache(dname))
    gd.rm(did)
    gd.ls()
    #fid = gd.upload('/home/jkurik/the.hacker.playbook.practical.guide.to.penetration.testing.pdf')
    #fid = gd.upload('/home/jkurik/kalendar2016v3.xls')
    #did = gd.mkdir('tmp')
    #gd.is_dir(did)
    #gd.move(fid, did)
    #gd.download('/tmp/xxx', fid)
    #gd.rm(fid)
    #gd.rm(did)

