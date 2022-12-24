import json


class DataStore:
    def __init__(self):
        self._value: list[dict[str, str]] = []

    @staticmethod
    def data_unit(title: str, id: str) -> dict[str, str]:
        return {'title': title, 'id': id}

    def update(self, title: str, id: str):
        value = self.data_unit(title, id)
        if value not in self._value:
            self._value.append(value)

    def list(self) -> list[dict[str, str]]:
        return self._value

    def purge(self) -> None:
        self._value = []

    def print(self) -> None:
        if len(self) > 0:
            for i, item in enumerate(self.list(), start=1):
                print(i, '-', item['title'])
        else:
            raise Exception('Datastore is empty')

    @classmethod
    def retrieve_from_file(cls, file_fullpath):
        new_data_units = []

        def retrieve(data_units) -> None:
            if type(data_units) == dict:
                try:
                    title, id = data_units.keys()
                    if title == 'title' and id == 'id':
                        new_data_units.append(data_units)
                except Exception:
                    pass
            elif type(data_units) == list:
                for data_unit in data_units:
                    retrieve(data_unit)

        try:
            with open(file_fullpath) as f:
                try:
                    file = json.load(f)
                    retrieve(file)
                except Exception:
                    pass
        except Exception:
            pass
        data_store = cls()
        data_store._value = new_data_units
        return data_store

    def append(self, data_store) -> None:
        """
        Append another DataStore into this DataStore.
        Use with caution, value added by load() can cause duplication.
        """
        if type(data_store) != DataStore:
            raise TypeError(
                f"Only {self.__class__.__name__} object can be loaded")
        self._value += data_store.list()

    def __getitem__(self, index: int) -> dict[str, str]:
        return self._value[index]

    def __len__(self) -> int:
        return len(self._value)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}{self.list()}'
