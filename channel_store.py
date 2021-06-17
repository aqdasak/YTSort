import json


class ChannelStore:
    def __init__(self):
        self._value = []

    def update(self, title, channel_id):
        value = self.channel_dict(title, channel_id)
        if value not in self._value:
            self._value.append(value)

    def list(self) -> list:
        return self._value

    @property
    def len(self):
        return len(self._value)

    def print_channels(self):
        if self.len > 0:
            for i, item in enumerate(self.list()):
                print(i + 1, '-', item['title'])
        else:
            print('Channel list is empty')

    @staticmethod
    def channel_dict(title, channel_id):
        return {'title': title, 'channel_id': channel_id}

    @classmethod
    def retrieve_from_file(cls, file_fullpath):
        new_channel_with_id = []

        def load(channel_with_id) -> bool:
            if type(channel_with_id) == dict:
                try:
                    title, channel_id = channel_with_id.keys()
                    if title == 'title' and channel_id == 'channel_id':
                        new_channel_with_id.append(channel_with_id)
                except:
                    pass
            elif type(channel_with_id) == list:
                for item in channel_with_id:
                    load(item)

        try:
            with open(file_fullpath) as f:
                try:
                    file = json.load(f)
                    load(file)
                except Exception as e:
                    pass
        except:
            pass
        channel_store = cls()
        channel_store._value = new_channel_with_id
        return channel_store

    def load(self, channel_store):
        if type(channel_store) != ChannelStore:
            raise TypeError("Only ChannelStore object can be loaded")
        self._value += channel_store.list()

    def __str__(self):
        return f'{self.__class__.__name__}{self._value}'
