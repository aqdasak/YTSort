class ProgressBar:
    def __init__(self):
        self.current=None
        self._total = None
        self._counter = 0

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, total):
        if self._counter == 0:
            self._total = total
        else:
            raise Exception('total already set')
        self._counter += 1

    def update(self, current):
        self.current = current
        from math import ceil
        ch = ceil(25 / self.total)
        # print('\b' * (4 + ch * self.total + 2), end='')
        print(str(self.current * 100 // self.total) + '% ', end='')
        progress_str = '[' + '#' * ch * self.current + ' ' * ch * (self.total - self.current) + ']'
        # print(progress_str, end='')
        print(progress_str)
