# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2023-02-27"
# Created: 2017-07-07 10:00

import abc
import logging
import threading
from typing import Any, Dict, Optional, Protocol, TypeVar

from flotils import Loadable, StartStopable
from nameko.rpc import rpc
from nameko.timer import timer
import seta

from ..__version__ import __version__ as pkg_version


logger = logging.getLogger(__name__)
T = TypeVar("T")


class Store(Protocol):
    """ Interface for storing information in keystore"""

    def cache_save(self) -> None:
        """ Persist stored data """

    def get(self, key: str, default: Optional[T] = None) -> T:
        """
        Get a value from the store

        :param key: Identifier to retrieve
        :param default: Value to return if key not found, defaults to None
        :returns: Stored value or default
        """

    def set(self, key: str, value: T, ttl: float = 0.0) -> None:  # noqa: A003
        """
        Save a value on the store

        :param key: Key to store value at
        :param value: Value to store
        :param ttl: Duration the value is valid (if implemented)
        """

    def delete(self, key: str) -> None:
        """
        Remove key from store

        :param key: Identifier to delete
        """


class ThreadSafeStore(Loadable, StartStopable):
    """ Thread safe local key store (dict backed) """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)
        self.lock = threading.RLock()
        """ Lock controlling access """
        self._store: Dict[str, Any] = {}
        """ Internal storage """
        self._cache_path: Optional[str] = self.join_path_prefix(
            settings.get("cache_path")
        )
        """ Path where to store data """

    def cache_load(self) -> None:
        """ Load internal data from cache """
        if not self._cache_path:
            return

        try:
            cache = self.load_settings(self._cache_path)

            if cache:
                self.info("Loaded {} keys from cache".format(len(cache)))

                with self.lock:
                    self._store = cache
        except Exception:
            self.exception("Failed to load cache ({})".format(self._cache_path))

    def cache_save(self) -> None:
        """ Save internal data to cache """
        if not self._cache_path:
            return

        try:
            with self.lock:
                self.save_settings(self._cache_path, self._store)

            self.info("Saved {} keys to cache".format(len(self._store)))
        except Exception:
            self.exception("Failed to save cache ({})".format(self._cache_path))

    def start(self, blocking: bool = False) -> None:
        """ Start instance """
        self.cache_load()
        super().start(blocking)

    def stop(self) -> Any:
        """ Stop instance """
        super().stop()
        self.cache_save()

    def get(self, key: str, default: Optional[T] = None) -> T:
        """
        Get value from store

        :param key: Which value to get
        :param default: Value to return if key not in store
        :returns: Value in store or default
        """
        with self.lock:
            return self._store.get(key, default)

    def set(self, key: str, value: T) -> None:  # noqa: A003
        """
        Store value in store

        :param key: Key to identify
        :param value: Value to store
        """
        with self.lock:
            self._store[key] = value

    def set_default(self, key: str, default: T) -> T:
        """
        Set default value and return value or current value

        :param key: Key to identify
        :param default: Default value to use
        :returns: Default or previous stored value
        """
        with self.lock:
            return self._store.setdefault(key, default)

    def delete(self, key: str) -> None:
        """
        Remove entry from store

        :param key: Key to identify
        :raises KeyError: Key not in store
        """
        with self.lock:
            del self._store[key]


class KeystoreDependency(seta.BaseDependency):
    """ Dependency for thread safe store """

    def setup(self) -> None:
        """ Setup instance """
        super().setup()
        self.instance = ThreadSafeStore(self.instance_config)
        super(KeystoreDependency, self).setup()


class KeystoreService(seta.BaseService, abc.ABC):
    """ Base class for keystore service"""

    __metaclass__ = abc.ABCMeta

    store: Optional[Store] = None
    """ Store backing this service """

    @timer(interval=15 * 60 * 60)
    def save_store(self) -> None:
        """
        Save cache periodically in case of failures
        :raises ValueError: No store set
        """
        if self.store is None:
            raise ValueError("No store set")

        logger.debug("Saving cache")

        try:
            self.store.cache_save()
        except Exception:
            logger.exception("Failed to save cache of store")

    @rpc
    def get(self, key: str, default: Optional[T] = None) -> T:
        """
        Get value from store

        :param key: Which value to get
        :param default: Value to return if key not in store
        :returns: Value in store or default
        :raises ValueError: No store set
        """
        if self.store is None:
            raise ValueError("No store set")

        return self.store.get(key, default)

    @rpc
    def set(self, key: str, value: Any) -> None:  # noqa: A003
        """
        Store value in store

        :param key: Key to identify
        :param value: Value to store
        :raises ValueError: No store set
        """
        if self.store is None:
            raise ValueError("No store set")

        self.store.set(key, value)

    @rpc
    def delete(self, key: str) -> None:
        """
        Remove entry from store

        :param key: Key to identify
        :raises KeyError: Key not in store
        :raises ValueError: No store set
        """
        if self.store is None:
            raise ValueError("No store set")

        self.store.delete(key)


class LocalKeystoreService(KeystoreService):
    """ Keystore service for python dict based store """

    name = "service_keystore"
    __version__ = pkg_version

    store: ThreadSafeStore = KeystoreDependency()
    """ Store backend """
