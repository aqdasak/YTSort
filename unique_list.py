class UniqList:
    def __init__(self, value=None):
        self._value = []
        if value:
            self.update(value)

    def update(self, value):
        if type(value) == dict:
            self._unique_update(value)
        elif type(value) == list:
            for item in value:
                self._unique_update(item)
        else:
            raise TypeError('Value must be of type list or dict')

    def _unique_update(self, value: dict):
        if type(value) != dict:
            raise TypeError('Inner values must be of type dict')
        if value not in self._value:
            self._value.append(value)

    def list(self)->list:
        return self._value

    def __str__(self):
        return f'{self.__class__.__name__}{self._value}'
