import os
import json

from ytsort.data_store import DataStore


class CacheManager:
    """
    Provide functions to easily manage cache.
    Use json to dump data stored in DataStore object as list.
    """

    def __init__(self, config: dict) -> None:
        """
        Parameters
        ----------
        config: dict
            Configurations to change the behaviour of program

        Required keys in config:
        1. 'local_cache'
        2. 'shared_cache'
        """
        self.__local_playlist_cache_path = os.path.join(
            config['local_cache'], 'playlist.json')
        self.__local_channel_cache_path = os.path.join(
            config['local_cache'], 'channel.json')
        self.__shared_channel_cache_path = os.path.join(
            config['shared_cache'], 'channel.json')

        self.__indent = config['cache_indent']

        self._local_playlist_cache = DataStore()
        self._local_channel_cache = DataStore()
        self._shared_channel_cache = DataStore()

        self.create_folder(config['local_cache'])
        self.create_folder(config['shared_cache'])

        self.load()

    @property
    def local_playlist_cache(self):
        """Playlist cache stored in renaming folder"""
        return self._local_playlist_cache

    @property
    def local_channel_cache(self):
        """Channel cache stored in renaming folder"""
        return self._local_channel_cache

    @property
    def shared_channel_cache(self):
        """Channel cache stored in shared cache folder"""
        return self._shared_channel_cache

    @staticmethod
    def _create_cache(cache_unit: dict):
        local_cache = DataStore()
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
        r = DataStore.retrieve_from_file(self.__local_playlist_cache_path)
        if r:
            self._local_playlist_cache.append(r)

    def load_local_channel_cache(self):
        r = DataStore.retrieve_from_file(self.__local_channel_cache_path)
        if r:
            self._local_channel_cache.append(r)

    def load_shared_channel_cache(self):
        r = DataStore.retrieve_from_file(self.__shared_channel_cache_path)
        if r:
            self._shared_channel_cache.append(r)

    @staticmethod
    def create_folder(folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    def is_local_playlist_cache_available(self):
        return True if len(self._local_playlist_cache) > 0 else False

    def is_local_channel_cache_available(self):
        return True if len(self._local_channel_cache) > 0 else False

    def is_shared_channel_cache_available(self):
        return True if len(self._shared_channel_cache) > 0 else False

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

    def delete_local_playlist_cache(self):
        self._local_playlist_cache.purge()
        try:
            os.remove(self.__local_playlist_cache_path)
        except Exception:
            pass

    def delete_local_channel_cache(self):
        self._local_channel_cache.purge()
        try:
            os.remove(self.__local_channel_cache_path)
        except Exception:
            pass
