import pandas as pd
import json
from pathlib import Path
from typing import Union, Dict, Any


class ProteinTable(pd.DataFrame):
    SPECIAL_COLUMNS = ["truncation", "biomes", "assemblies"]

    def __init__(self, results: Union[Path, str, pd.DataFrame], **kwargs):
        if isinstance(results, pd.DataFrame):
            data = results.copy()
        else:
            data = pd.read_csv(results)

        super().__init__(data)

        for col in self.SPECIAL_COLUMNS:
            if col in self.columns:
                self[col] = self[col].apply(self._string_to_json)

    @staticmethod
    def _string_to_json(value):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    @property
    def unique_hits(self):
        return self["target_name"].unique()

    @property
    def n_unique_hits(self):
        return len(self.unique_hits)

    def filter(self, filters: Dict[str, Any]):
        """
        Filters the DataFrame based on specified conditions.

        This method allows filtering of the DataFrame's rows based on specified conditions for each column. It supports two types of filters:
        1. Numeric range filters (using a dictionary with 'min' and/or 'max' keys).
        2. List-based filters (using a list of strings).

        Parameters:
        filters (Dict[str, Any]): A dictionary where each key is a column name and each value is the condition for filtering.
                                  The condition can be a dictionary (for numeric ranges) or a list of strings (for list-based filtering).

        Returns:
        ProteinTable: A new ProteinTable that is filtered based on the specified conditions.
        """
        result_table = self
        query_conditions = []

        for column, condition in filters.items():
            if column in result_table.columns:
                if isinstance(condition, dict):
                    if "min" in condition:
                        query_conditions.append(f'`{column}` >= {condition["min"]}')
                    if "max" in condition:
                        query_conditions.append(f'`{column}` <= {condition["max"]}')
                elif isinstance(condition, list):
                    result_table = self._apply_list_filter(
                        result_table, column, condition
                    )

        query_string = " and ".join(query_conditions)
        return ProteinTable(
            result_table.query(query_string) if query_conditions else result_table
        )

    @staticmethod
    def _apply_list_filter(dataframe, column, values):
        """
        Applies a list-based filter to the DataFrame.

        This method filters rows where the specified column contains any of the values in the provided list. It's primarily used
        internally by the `filter_table` method for handling list-based filtering conditions.

        Parameters:
        dataframe (DataFrame): The DataFrame to be filtered.
        column (str): The name of the column to apply the filter to. The column should contain list-like elements.
        values (List[str]): A list of strings. Rows where the column contains any of these strings will be included in the output.

        Returns:
        DataFrame: A new DataFrame containing only the rows that meet the list-based filter condition.

        """
        mask = dataframe[column].apply(lambda x: any(item in x for item in values))
        filtered_df = dataframe[mask]
        return ProteinTable(filtered_df)

    def save(self):
        """
        save ProteinTable
        Returns:
        """
        ...

    def