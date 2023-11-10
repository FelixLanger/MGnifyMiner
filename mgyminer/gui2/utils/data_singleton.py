from mgyminer.proteinTable import proteinTable


class DataSingleton:
    _instance = None
    _data = None
    _query_file = None
    _hit_sequences = None

    def __new__(cls, data_path=None, query_file=None, hit_sequences=None):
        if cls._instance is None:
            cls._instance = super(DataSingleton, cls).__new__(cls)
            cls._data_path = data_path
            cls._query_file = query_file
            cls._hit_sequences = hit_sequences
        return cls._instance

    @property
    def data(self):
        if self._data is None and self._data_path is not None:
            self._data = proteinTable(self._data_path)
            self._data.df.rename(columns={"e-value": "e_value"}, inplace=True)
        return self._data

    @property
    def query_file(self):
        return self._query_file

    @property
    def hit_sequences(self):
        return self._hit_sequences
