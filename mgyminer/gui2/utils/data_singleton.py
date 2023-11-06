from mgyminer.proteinTable import proteinTable
class DataSingleton:
    _instance = None
    _data = None

    def __new__(cls, data_path=None):
        if cls._instance is None:
            cls._instance = super(DataSingleton, cls).__new__(cls)
            cls._data_path = data_path
        return cls._instance

    @property
    def data(self):
        if self._data is None and self._data_path is not None:
            self._data = proteinTable(self._data_path)
        return self._data