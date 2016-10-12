#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

class GCache(object):
    def __init__(self, store = None):
        self.store = store
        self.cache = {}

    def put(self, v1, v2):
        try:
            (x, y) = v1
            a = v2
            v2 = v1
            v1 = a
        except:
            pass
        self.cache[v1] = v2
        logging.debug('Value %s saved as a key %s' % (v2, v1))

    def get(self, v):
        try:
            (x, y) = v
            for a in self.cache:
                if self.cache[a] == v:
                    logging.debug('Value %s has been found as key %s' % (v, a))
                    return a
        except:
            if v in self.cache:
                logging.debug('Key %s has been found as value %s' % (v, self.cache[v]))
                return self.cache[v]
        logging.debug('Key/value %s has not been found' % (v,))
        raise KeyError(v)

    def __len__(self):
        return len(self.cache)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        try:
            (x, y) = key
            for a in self.cache:
                if self.cache[a] == key:
                    logging.debug('Removing value %s as key %s' % (v, a))
                    del self.cache[a]
            raise KeyError(key)
        except:
            logging.debug('Removing value %s as key %s' % (self.cache[key], key))
            del self.cache[key]

    def __contains__(self, v):
        try:
            (x, y) = v
            for a in self.cache:
                if self.cache[a] == v:
                    logging.debug('Value %s is present in the cache' % v)
                    return True
        except:
            if v in self.cache:
                logging.debug('Key %s is present in the cache' % v)
                return True
        logging.debug('Key/value %s has not been found in the cache' % (v,))
        return False

    def __iter__(self):
        return iter(self.cache)


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    c = GCache()
    c.put('Nazdar', ('n1', 'n2'))
    c.put(('a1', 'a2'), 'Ahoj')
    c.get('Nazdar')
    c.get(('n1', 'n2'))

    'Nazdar' in c
    'Nazdar2' in c

    try:
        c.get(('n2', 'n1'))
    except KeyError as e:
        pass
    try:
        c.get('Todlecto')
    except KeyError as e:
        pass
    for x in c:
        c[x]

