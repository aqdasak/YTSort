class DistinctChannel():
    def __init__(self, title=None, channel_id=None):
        self._value = []
        if title and channel_id:
            self.update(title, channel_id)
        elif (not title and channel_id) or (title and not channel_id):
            raise Exception(
                'title and channel_id both must be passed or neither of them')

    @staticmethod
    def _channel_dict(title, channel_id):
        return {'title': title, 'channel_id': channel_id}

    def update(self, title, channel_id):
        value = self._channel_dict(title, channel_id)
        if value not in self._value:
            self._value.append(value)

    def list(self) -> list:
        return self._value

    def __str__(self):
        return f'{self.__class__.__name__}{self._value}'
