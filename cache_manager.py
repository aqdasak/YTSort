import os
import json

from cache_store import CacheStore


class CacheManager:
    def __init__(self, config) -> None:
        self.__local_playlist_cache_path = os.path.join(
            config['local_cache'], 'playlist.json')
        self.__local_channel_cache_path = os.path.join(
            config['local_cache'], 'channel.json')
        self.__shared_channel_cache_path = os.path.join(
            config['shared_cache'], 'channel.json')

        self.__indent = config['cache_indent']

        self._local_playlist_cache = CacheStore()
        self._local_channel_cache = CacheStore()
        self._shared_channel_cache = CacheStore()

        self.create_folder(config['local_cache'])
        self.create_folder(config['shared_cache'])

        self.load()

    @property
    def local_playlist_cache(self):
        return self._local_playlist_cache

    @property
    def local_channel_cache(self):
        return self._local_channel_cache

    @property
    def shared_channel_cache(self):
        return self._shared_channel_cache

    @staticmethod
    def _create_cache(cache_unit: dict):
        local_cache = CacheStore()
        local_cache.update(
            cache_unit['title'], cache_unit['id'])
        return local_cache

    def update_playlist_cache(self, playlist_cache_unit: dict):
        self.update_local_playlist_cache(playlist_cache_unit)

    def update_channel_cache(self, channel_cache_unit: dict):
        self.update_local_channel_cache(channel_cache_unit)
        self.update_shared_channel_cache(channel_cache_unit)

    def update_local_playlist_cache(self, playlist_cache_unit: dict):
        self._local_playlist_cache = self._create_cache(playlist_cache_unit)

    def update_local_channel_cache(self, channel_cache_unit: dict):
        self._local_channel_cache = self._create_cache(channel_cache_unit)

    def update_shared_channel_cache(self, channel_cache_unit: dict):
        self._shared_channel_cache.update(
            channel_cache_unit['title'], channel_cache_unit['id'])

    def load(self):
        self.load_local_playlist_cache()
        self.load_local_channel_cache()
        self.load_shared_channel_cache()

    def load_local_playlist_cache(self):
        r = CacheStore.retrieve_from_file(self.__local_playlist_cache_path)
        if r:
            self._local_playlist_cache.load(r)

    def load_local_channel_cache(self):
        r = CacheStore.retrieve_from_file(self.__local_channel_cache_path)
        if r:
            self._local_channel_cache.load(r)

    def load_shared_channel_cache(self):
        r = CacheStore.retrieve_from_file(self.__shared_channel_cache_path)
        if r:
            self._shared_channel_cache.load(r)

    @staticmethod
    def create_folder(folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    def is_local_playlist_cache_available(self):
        return True if self._local_playlist_cache.len > 0 else False

    def is_local_channel_cache_available(self):
        return True if self._local_channel_cache.len > 0 else False

    def is_shared_channel_cache_available(self):
        return True if self._shared_channel_cache.len > 0 else False

    def _dump(self, path, cache_list: list):
        with open(path, 'w') as f:
            json.dump(cache_list, f, indent=self.__indent)

    def save(self):
        self.save_local_playlist_cache()
        self.save_local_channel_cache()
        self.save_shared_channel_cache()

    def save_local_playlist_cache(self):
        self._dump(self.__local_playlist_cache_path,
                   self.local_playlist_cache.list())

    def save_local_channel_cache(self):
        self._dump(self.__local_channel_cache_path,
                   self.local_channel_cache.list())

    def save_shared_channel_cache(self):
        self._dump(self.__shared_channel_cache_path,
                   self.shared_channel_cache.list())
