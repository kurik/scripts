#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import os
import sys
from datetime import timedelta
import stat
import time

DEFAULT_CACHE_DIR = '~/.cache'

_debug = False

def _debug_msg(msg, eol = True):
    if _debug:
        if eol:
            print('DEBUG:', msg)
        else:
            print('DEBUG:', msg, eol = '')
        sys.stdout.flush()

class _ItemCacheIterator:
    def __init__(self, keylist):
        self.index = -1
        self.keylist = keylist

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if len(self.keylist) > self.index:
            return self.keylist[self.index]
        else:
            raise StopIteration()

class ItemCache(object):
    def __init__(self, expiration = timedelta()):
        if expiration is None:
            self.exp = None
            _debug_msg('Expiration of cache is switched off')
        else:
            try:
                self.exp = expiration.total_seconds()
            except:
                # Do it in the python 2.6 way
                self.exp = expiration.days * 86400 + expiration.seconds
            _debug_msg('Setting expiration time to %s seconds' % self.exp)


    ### ItemCache interface to be implementd by child classes
    def getItem(self, key):
        raise KeyError(key)

    def setItem(self, key, value):
        raise KeyError(key)

    def delItem(self, key):
        raise KeyError(key)

    def contains(self, key):
        return False

    def getKeys(self):
        return list()

    def expired(self, key):
        raise KeyError(key)

    ### Define container interface
    def __getitem__(self, key):
        return self.getItem(key)

    def __setitem__(self, key, value):
        return self.setItem(key, value)

    def __delitem__(self, key):
        return self.delItem(key)

    def __contains__(self, key):
        return self.contains(key)

    def __iter__(self):
        return _ItemCacheIterator(self.getKeys())

    def __len__(self):
        return len(self.getKeys())


class ItemMemCache(ItemCache):
    cache = {}
    def __init__(self, expiration = timedelta()):
        ItemCache.__init__(self, expiration)

    def getItem(self, key):
        return self.cache[str(key)]

    def setItem(self, key, value):
        self.cache[str(key)] = value

    def delItem(self, key):
        del self.cache[str(key)]

    def contains(self, key):
        return str(key) in self.cache

    def getKeys(self):
        return self.cache.keys()

    def expired(self, key):
        # Memory cache never expires
        return False

class ItemDiskCache(ItemMemCache):
    def __init__(self, cacheName = "", diskCacheDir = DEFAULT_CACHE_DIR, expiration = timedelta()):
        ItemMemCache.__init__(self, expiration)
        self.cacheName = cacheName
        self.diskCacheDir = diskCacheDir
        self.dirname = os.path.expanduser(diskCacheDir + '/' + cacheName.replace('/', '.'))
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def _getItemPath(self, key):
        key = "".join(i for i in key if ord(i)<128)
        return self.dirname + '/' + str(key).replace('/', '.')

    def expired(self, key):
        if (self.exp is None) or (self.exp <= 0):
            # Never expires
            return False
        item_path = self._getItemPath(key)
        mtime = os.stat(item_path).st_mtime
        return (mtime + self.exp) < time.time()

    def getItem(self, key):
        key = str(key)
        value = None
        try:
            value = ItemMemCache.getItem(self, key)
        except KeyError:
            # The item has not be found in MemCache
            # Lets try to found in DiskCache
            item_path = self._getItemPath(key)
            if os.path.exists(item_path) and not self.expired(key):
                with open(item_path, 'rb') as f:
                    try:
                        value = pickle.load(f)
                    except:
                        # The cache is somehow corrupted; remove it
                        self.delItem(key)
                        raise KeyError('Disk Cache for item %s is corupted' % key)
            else:
                # Not found even in disk cache or is expired
                raise KeyError(key)
        # We have got the value from cache
        return value

    def setItem(self, key, value):
        # Save it to MemCache first
        ItemMemCache.setItem(self, key, value)
        key = str(key)
        item_path = self._getItemPath(key)
        with open(item_path, 'wb') as f:
            result = pickle.dump(value, f)
            return result

    def delItem(self, key):
        key = str(key)
        item_path = self._getItemPath(key)
        os.remove(item_path)

    def contains(self, key):
        key = str(key)
        item_path = self._getItemPath(key)
        return (os.path.exists(item_path) and not self.expired(key))
       
    def getKeys(self):
        item_path = self._getItemPath('')
        for (dirpath, dirnames, filenames) in os.walk(item_path):
            return filenames
        

# Module testing
if __name__ == "__main__":
    _debug = True
    c = ItemDiskCache("ItemDiskCache", "/tmp", timedelta(days = 5))
    try:
        del c['blah']
        del c['blah2']
    except:
        pass
    c['blah'] = "Bubaq"
    c['blah2'] = 'Bubaq2'
    for k in c:
        print('Key = %s, Value = %s' % (k, c[k]))
    print('Is blah in cache: ', 'blah' in c)
    if 'blah' in c:
        print('Is blah expired: ', c.expired('blah'))
    print('Is blah333 in cache: ', 'blah333' in c)
    if 'blah333' in c:
        print('Is blah333 expired: ', c.expired('blah333'))
    del c['blah']
    del c['blah2']
    try:
        del c['blah333']
    except:
        print('Key blah333 does not exists in the cache')
