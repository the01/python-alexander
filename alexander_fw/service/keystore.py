# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2017-07-07"
# Created: 2017-07-07 10:00

import abc
import threading

from nameko.extensions import DependencyProvider
from nameko.rpc import rpc
from flotils import get_logger, Loadable, StartStopable


logger = get_logger()


class ThreadSafeStore(Loadable, StartStopable):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(ThreadSafeStore, self).__init__(settings)
        self.lock = threading.RLock()
        """ Lock controlling access """
        self._store = {}
        """ Internal storage """
        self._cache_path = self.join_path_prefix(settings.get("cache_path"))
        """ Path where to store data
            :type : str | unicode | None """

    def cache_load(self):
        if not self._cache_path:
            return
        try:
            cache = self.load_settings(self._cache_path)
            if cache:
                self.info("Loaded {} keys from cache".format(len(cache)))
                with self.lock:
                    self._store = cache
        except:
            self.exception("Failed to load cache ({})".format(self._cache_path))

    def cache_save(self):
        if not self._cache_path:
            return
        try:
            with self.lock:
                self.save_settings(self._cache_path, self._store)
            self.info("Saved {} keys to cache".format(len(self._store)))
        except:
            self.exception("Failed to save cache ({])".format(self._cache_path))

    def start(self, blocking=False):
        self.cache_load()
        super(ThreadSafeStore, self).start(blocking)

    def stop(self):
        super(ThreadSafeStore, self).stop()
        self.cache_save()

    def get(self, key, default=None):
        with self.lock:
            return self._store.get(key, default)

    def set(self, key, value):
        with self.lock:
            self._store[key] = value

    def set_default(self, key, default):
        with self.lock:
            self._store.setdefault(key, default)

    def delete(self, key):
        with self.lock:
            del self._store[key]


class KeystoreDependency(DependencyProvider):

    def setup(self):
        settings = self.container.config.get('keystore')
        self.instance = ThreadSafeStore(settings)
        super(KeystoreDependency, self).setup()

    def start(self):
        logger.debug("Keystore starting..")
        self.instance.start(False)
        super(KeystoreDependency, self).start()

    def stop(self):
        logger.debug("Keystore stopping..")
        super(KeystoreDependency, self).stop()
        self.instance.stop()

    def get_dependency(self, worker_ctx):
        return self.instance


class KeystoreService(object):
    __metaclass__ = abc.ABCMeta

    store = None

    @rpc
    def status(self):
        return "ok"

    @rpc
    def get(self, key, default=None):
        return self.store.get(key, default)

    @rpc
    def set(self, key, value):
        self.store.set(key, value)

    @rpc
    def delete(self, key):
        self.store.delete(key)


class LocalKeystoreService(KeystoreService):
    name = "service_keystore"

    store = KeystoreDependency()
    """ :type : ThreadSafeStore """
