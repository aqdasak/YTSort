import json


class CacheStore:
    def __init__(self):
        self._value = []

    @staticmethod
    def cache_unit(title, id):
        return {'title': title, 'id': id}

    def update(self, title, id):
        value = self.cache_unit(title, id)
        if value not in self._value:
            self._value.append(value)

    def list(self) -> list:
        return self._value

    @property
    def len(self):
        return len(self._value)

    def print(self):
        if self.len > 0:
            for i, item in enumerate(self.list()):
                print(i + 1, '-', item['title'])
        else:
            print('List is empty')

    @classmethod
    def retrieve_from_file(cls, file_fullpath):
        new_cache_units = []

        def retrieve(cache_units) -> bool:
            if type(cache_units) == dict:
                try:
                    title, id = cache_units.keys()
                    if title == 'title' and id == 'id':
                        new_cache_units.append(cache_units)
                except:
                    pass
            elif type(cache_units) == list:
                for cache_unit in cache_units:
                    retrieve(cache_unit)

        try:
            with open(file_fullpath) as f:
                try:
                    file = json.load(f)
                    retrieve(file)
                except Exception as e:
                    pass
        except:
            pass
        cache_store = cls()
        cache_store._value = new_cache_units
        return cache_store

    def load(self, cache_store):
        """
        Used to load another CacheStore into this CacheStore.
        Used with caution, value added by load() can cause duplication.
        """
        if type(cache_store) != CacheStore:
            raise TypeError(
                f"Only {self.__class__.__name__} object can be loaded")
        self._value += cache_store.list()

    def __str__(self):
        return f'{self.__class__.__name__}{self.list()}'
