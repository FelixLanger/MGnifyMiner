def create_dataframe_store():
    class DataFrameStore:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(DataFrameStore, cls).__new__(cls)  # noqa: UP008
                cls.dataframe = None
            return cls._instance

        @property
        def is_filled(self):
            """Check if the stored dataframe is filled (not None and not empty)."""
            return self.dataframe is not None and not self.dataframe.empty

        @classmethod
        def get_dataframe(cls):
            """Return the stored dataframe."""
            return cls._instance.dataframe

        @classmethod
        def set_dataframe(cls, new_dataframe):
            """Set or overwrite the stored dataframe with a new one."""
            cls._instance.dataframe = new_dataframe

        @classmethod
        def clear_dataframe(cls):
            """Clear the stored dataframe (set to None or an empty DataFrame)."""
            cls._instance.dataframe = None

    return DataFrameStore


ProteinStore = create_dataframe_store()

protein_store = ProteinStore()
