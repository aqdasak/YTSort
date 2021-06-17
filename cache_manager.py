import os
import json

from channel_store import ChannelStore


class CacheManager:
    def __init__(self, config) -> None:
        self.__local_cache_path = os.path.join(
            config['renaming_folder_path'], config['local_cache'])
        self.__shared_cache_path = os.path.join(
            config['program_folder_path'], 'cache/', config['shared_cache'])
        self.__indent = config['cache_indent']

        self._local_cache = ChannelStore()
        self._shared_cache = ChannelStore()
        self.load()

    @property
    def local_cache(self):
        return self._local_cache

    @property
    def shared_cache(self):
        return self._shared_cache

    def update_local_cache(self, channel_with_id: dict):
        self._local_cache = ChannelStore()
        self._local_cache.update(
            channel_with_id['title'], channel_with_id['channel_id'])

    def update_shared_cache(self, channel_with_id: dict):
        self._shared_cache.update(
            channel_with_id['title'], channel_with_id['channel_id'])

    def load(self):
        self.load_local_cache()
        self.load_shared_cache()

    def load_local_cache(self):
        r = ChannelStore.retrieve_from_file(self.__local_cache_path)
        if r:
            self._local_cache.load(r)

    def load_shared_cache(self):
        r = ChannelStore.retrieve_from_file(self.__shared_cache_path)
        if r:
            self._shared_cache.load(r)

    def is_local_cache_available(self):
        return True if self._local_cache.len > 0 else False

    def is_shared_cache_available(self):
        return True if self._shared_cache.len > 0 else False

    def update_cache(self, channel_with_id: dict):
        self.update_local_cache(channel_with_id)
        self.update_shared_cache(channel_with_id)

    def _dump(self, path, cache_list: list):
        with open(path, 'w') as f:
            json.dump(cache_list, f, indent=self.__indent)

    def save(self):
        self.save_local_cache()
        self.save_shared_cache()

    def save_local_cache(self):
        if self.is_local_cache_available:
            self._dump(self.__local_cache_path, self.local_cache.list())

    def save_shared_cache(self):
        if self.is_shared_cache_available:
            self._dump(self.__shared_cache_path, self.shared_cache.list())
