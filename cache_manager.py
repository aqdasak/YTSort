import os
import json

from distinct_channel import DistinctChannel


class CacheManager:
    def __init__(self, config) -> None:
        self._local_cache_path = os.path.join(
            config['renaming_folder_path'], config['local_cache'])
        self._shared_cache_path = os.path.join(
            config['program_folder_path'], 'cache/', config['shared_cache'])

    @property
    def local_cache(self):
        with open(self._local_cache_path) as f:
            channel_with_id = json.load(f)
        return channel_with_id

    @local_cache.setter
    def local_cache(self, channel_with_id: dict):
        with open(self._local_cache_path, 'w') as f:
            json.dump(channel_with_id, f, indent=4)

    @property
    def shared_cache(self):
        with open(self._shared_cache_path, 'r') as f:
            channel_with_id = json.load(f)
        return channel_with_id

    @shared_cache.setter
    def shared_cache(self, channel_with_id):
        def is_channel_id_in_shared_cache(channel_id):
            try:
                with open(self._shared_cache_path, 'r') as f:
                    channel_with_id = json.load(f)
                    for dct in channel_with_id:
                        if dct['channel_id'] == channel_id:
                            return True
            except:
                pass
            return False

        from config import config
        program_folder_path = config['program_folder_path']

        if not self.is_shared_cache_integrated(program_folder_path):
            with open(self.shared_cache, 'w') as f:
                json.dump([channel_with_id], f, indent=4)
        elif not is_channel_id_in_shared_cache(channel_with_id['channel_id']):
            temp_channel_with_id = DistinctChannel()
            with open(self.shared_cache, 'r') as f:
                temp_channel_with_id._value = json.load(f)
                temp_channel_with_id.update(
                    channel_with_id['title'], channel_with_id['channel_id'])
            with open(self.shared_cache, 'w') as f:
                json.dump(temp_channel_with_id.list(), f, indent=4)

    @staticmethod
    def check_integrity(file_fullpath) -> bool:
        def check(channel_with_id) -> bool:
            if type(channel_with_id) == dict:
                try:
                    title, channel_id = channel_with_id.keys()
                    if title != 'title' or channel_id != 'channel_id':
                        return False
                except:
                    return False
                return True

            elif type(channel_with_id) == list:
                for item in channel_with_id:
                    r = check(item)
                    if r is False:
                        return r
                else:
                    return True
            else:
                return False

        try:
            with open(file_fullpath) as f:
                try:
                    channel_with_id = json.load(f)
                    return check(channel_with_id)
                except:
                    return False
        except:
            return False

    def is_local_cache_integrated(self):
        return self.check_integrity(self._local_cache_path)

    def is_shared_cache_integrated(self):
        return self.check_integrity(self._shared_cache_path)
