import json
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
from loguru import logger

from mgyminer.bigquery import BigQueryHelper
from mgyminer.config import load_config
from mgyminer.constants import BIOMES
from mgyminer.utils import (
    NumpyJSONEncoder,
    biome_str_to_ids,
    create_md5_hash,
    dataframe_to_fasta,
)


class ProteinTable(pd.DataFrame):
    SPECIAL_COLUMNS = ["truncation", "biomes", "assemblies", "complete"]

    def __init__(self, results: Union[Path, str, pd.DataFrame]):
        if isinstance(results, pd.DataFrame):
            data = results.copy()
        elif isinstance(results, (Path, str)):
            data = pd.read_csv(results)
            self._convert_special_columns(data)
        else:
            raise ValueError("No valid result data")

        super().__init__(data)
        self._membership_matrix = None

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, pd.DataFrame):
            return ProteinTable(result)
        return result

    def _convert_special_columns(self, data):
        for col in self.SPECIAL_COLUMNS:
            if col in data.columns:
                data[col] = data[col].apply(self._string_to_json)

    def convert_special_columns(self):
        self._convert_special_columns(self)

    @staticmethod
    def _string_to_json(value):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"encountered error parsing faulty json: {value}")
            return value

    @property
    def unique_hits(self):
        return self["target_name"].unique()

    @property
    def n_unique_hits(self):
        return len(self.unique_hits)

    @property
    def membership_matrix(self):
        """
        Property which creates the membership_matrix for the ProteinTable.
        A membership matrix is a pivot table of the MGYP ids as index
        and the query names as the column. The matrix gets a set_id column, which
        has a unique identifier for the combinations of queries a target protein (MGYP)
        is found in.
        """
        if self._membership_matrix is None:
            self._membership_matrix = pd.crosstab(self["target_name"], [self["query_name"]])
            self._membership_matrix = self._membership_matrix.where(self._membership_matrix == 0, 1)
            self._membership_matrix["set_id"] = self._membership_matrix.apply(
                lambda x: "".join([str(y) for y in x]), axis=1
            )
        return self._membership_matrix

    @property
    def membership_set_mapping(self):
        combinations = self.membership_matrix["set_id"].unique()
        names = self.membership_matrix.columns[:-1]

        combinations_dict = {}
        for combination in combinations:
            string_list = [int(num) for num in combination]
            matched_names = [names[i] for i, value in enumerate(string_list) if value == 1]
            readable_name = "∩".join(matched_names)
            combinations_dict[readable_name] = combination
        return combinations_dict

    def get_set(self, set_name):
        """
        Get all proteins which are part of the set of query sequences.
        Args:
            set_name: Name of the query / set of queries
        Returns:
            ProteinTable with all the Proteins which have been hit by the queries in the set_name
        """
        # if the set_name string is given convert it to the set id
        if set_name in self.membership_set_mapping:
            set_name = self.membership_set_mapping[set_name]
        target_names = self.membership_matrix[self.membership_matrix["set_id"] == set_name].index
        return ProteinTable(self[self["target_name"].isin(target_names)])

    def flatten(self, nested_column):
        """
        Return a flattened array of nested_column.
        Will return an array containing all values contained in the nested_column
        Args:
            nested_column: column name of the nested column

        Returns: array of all unique values of nested_column
        """
        return np.concatenate(self[nested_column].dropna().values)

    def value_counts_nested(self, nested_column):
        """
        Count the number of unique values in the nested_column
        Args:
            nested_column: Column name of nested column

        Returns: number of unique entries in nested column

        """
        # most efficient way to count nested unique values
        flattened_array = self.flatten(nested_column)
        return pd.Series(flattened_array).nunique()

    def unique_nested(self, nested_column):
        flattened_array = self.flatten(nested_column)
        return pd.Series(flattened_array).unique()

    def pick(self, filters: Dict[str, Any]):
        """
        Filters the ProteinTable based on specified conditions.

        This method filters the rows of the ProteinTable based on the specified conditions for each column.
        It supports three types of filters:
        1. Numeric range filters (using a dictionary with 'min' and/or 'max' keys).
        2. List-based filters (using a list of strings).
        3. String-based filters (for the "pfam_architecture" column, using a list of strings).

        The filtering is performed in the following order:
        1. Numeric range filters are applied first using the `query` method.
        2. List-based filters are then applied using the `_vectorised_list_filter` method.
        3. If a filter for the "pfam_architecture" column is provided, it is applied last using the `_string_filter` method.

        This order ensures that the most efficient operations are performed first, reducing the size of the DataFrame
        as early as possible for better performance.

        Parameters:
        filters (Dict[str, Any]): A dictionary where each key is a column name, and the value is the condition for
                                  filtering. The condition can be a dictionary (for numeric ranges), a list of
                                  strings (for list-based filtering), or a list of strings (for "pfam_architecture" filtering).

        Returns:
        ProteinTable: A new ProteinTable instance that is filtered based on the specified conditions.

        Example:
        >>> subset_pt = protein_table.pick({
        ...     "tlen": {"min": 200, "max": 300},
        ...     "pfam_architecture": ["PF00155"],
        ...     "biome": [353]
        ... })
        """

        result_table = self
        query_conditions = []

        pfam_filter = filters.pop("pfam_architecture", None)
        numeric_filters = {col: condition for col, condition in filters.items() if isinstance(condition, dict)}
        list_filters = {col: condition for col, condition in filters.items() if isinstance(condition, list)}

        if numeric_filters:
            range_conditions = []
            for column, condition in numeric_filters.items():
                if "min" in condition:
                    range_conditions.append(f'`{column}` >= {condition["min"]}')
                if "max" in condition:
                    range_conditions.append(f'`{column}` <= {condition["max"]}')
                query_conditions.extend(range_conditions)
            query_string = " and ".join(query_conditions)
            result_table = ProteinTable(result_table.query(query_string))

        if list_filters:
            for column, condition in list_filters.items():
                if column == "biomes":
                    if all(isinstance(element, int) for element in condition):
                        condition = [BIOMES[biome_id] for biome_id in condition]
                    condition = biome_str_to_ids(condition, BIOMES)
                result_table = self._vectorised_list_filter(result_table, column, condition)

        if pfam_filter:
            result_table = result_table._string_filter("pfam_architecture", pfam_filter)
        return ProteinTable(result_table)

    @staticmethod
    def _vectorised_list_filter(dataframe, column, values):
        """
        Applies a list-based filter to the DataFrame.

        This method filters rows where the specified column contains any of the values in the provided list.
        It's primarily used internally by the `pick` method for handling list-based filtering conditions.

        Parameters:
        ProteiTable (ProteiTable): The ProteiTable to be filtered.
        column (str): The name of the column to apply the filter to. The column should contain list-like elements.
        values (List[str]): A list of values. Rows where the column contains any of these values will be included in
                            the output.

        Returns:
        ProteiTable: A new ProteiTable containing only the rows that meet the list-based filter condition.

        """
        dataframe = dataframe.reset_index(drop=True)
        exploded_df = dataframe.explode(column)
        filtered_df = exploded_df[exploded_df[column].isin(values)]
        result_df = dataframe.iloc[filtered_df.index.drop_duplicates()]
        return ProteinTable(result_df)

    def _string_filter(self, column, values):
        if isinstance(values, str):
            values = [values]
        mask = self[column].str.contains("|".join(values), na=False, case=False)
        return self[mask]

    def save(self, path, index=False):
        """
        Save a ProteinTable to a csv file while preserving rounded floats and json columns
        Args:
            path: Path to the output csv
            index: Flag to include the index in the csv

        Returns: None
        """

        def format_float(e):
            if isinstance(e, str):
                return e
            if e > 0.0001:
                return e
            else:
                return f"{e:.1e}"

        formatted_df = self.copy()
        for column in ["e-value", "i-value", "c-value"]:
            if column in formatted_df.columns:
                formatted_df[column] = formatted_df[column].apply(format_float)

        for column in self.SPECIAL_COLUMNS:
            if column in formatted_df.columns:
                formatted_df[column] = formatted_df[column].apply(lambda x: json.dumps(x, cls=NumpyJSONEncoder))

        formatted_df.to_csv(path, index=index)

    @staticmethod
    def _setup_bigquery_connection():
        cfg = load_config()
        bigquery_data = {
            "credentials_path": cfg.get("Google service account json"),
            "dataset_id": cfg.get("BigQuery Dataset"),
        }
        return bigquery_data

    def fetch_metadata(self, database: str):
        if database.lower() == "bigquery":
            bq_helper = BigQueryHelper(**self._setup_bigquery_connection())

            columns_to_check = ["complete", "truncation", "assemblies", "biomes"]
            if all(column in self.columns for column in columns_to_check):
                logger.info(
                    f"Skipping fetching of data from BigQuery because {columns_to_check} columns are already present"
                )
                return self

            self["mgyp"] = self[
                "target_name"
            ]  # .apply(lambda x: mgyp_to_id(x)) ##TODO Remove or rename target_name to mgyp /remove mgyp row and use target name in general
            table_name = f"tmp_{create_md5_hash(self['query_name'][0])[:16]}"
            mgyp_ids = self["mgyp"].to_frame()
            temp_table = bq_helper.create_temp_table_from_dataframe(mgyp_ids, table_name, expiration_hours=1)
            # THIS JOIN WILL AUTOMATICALLY REMOVE THE PROTEINS WITHOUT METADATA
            # LEFT JOIN ON protein_metadata AND assembly TABLE WOULD BE NEEDED
            # TO KEEP THE LINES WHERE THESE TABLES DON'T HAVE DATA
            join_query = f"""
            SELECT
                t.mgyp AS mgyp,
                ARRAY_AGG(DISTINCT m.complete) as complete,
                ARRAY_AGG(DISTINCT COALESCE(m.truncation, '11')) as truncation,
                a.architecture as pfam_architecture,
                ARRAY_AGG(DISTINCT asmbly.accession) AS assemblies,
                ARRAY_AGG(DISTINCT asmbly.biome_id) AS biomes
            FROM
                {temp_table.project}.{temp_table.dataset_id}.{table_name} t
            JOIN
                {temp_table.project}.{temp_table.dataset_id}.protein p ON t.mgyp = p.mgyp
            LEFT JOIN
                {temp_table.project}.{temp_table.dataset_id}.architecture a ON p.architecture_hash = a.architecture_hash
            JOIN
                {temp_table.project}.{temp_table.dataset_id}.metadata m ON t.mgyp = m.mgyp
            JOIN
                {temp_table.project}.{temp_table.dataset_id}.assembly asmbly ON m.assembly_id = asmbly.assembly_id
            GROUP BY
                t.mgyp, a.architecture;
            """
            logger.debug(f"run query:\n {join_query}")
            metadata = bq_helper.query_to_dataframe(join_query)
            result = pd.merge(self, metadata, on="mgyp")
            result.drop("mgyp", axis=1, inplace=True)
            return ProteinTable(result)

        elif database.lower() == "mysql":
            # TODO: Implement fetching from MySQL
            pass
        else:
            raise ValueError("Unsupported database")

    def fetch_and_export_sequences(self, output_path: Union[Path, str], database):
        if database.lower() == "bigquery":
            bq_helper = BigQueryHelper(**self._setup_bigquery_connection())

            temp_table_name = f"tmp_{create_md5_hash(self['query_name'][0])[:16]}"

            check_query = (
                f"SELECT table_name FROM {bq_helper.dataset.dataset_id}.INFORMATION_SCHEMA.TABLES "
                f"WHERE table_name = '{temp_table_name}'"
            )
            check_result = bq_helper.query_to_dataframe(check_query)

            if check_result.empty:
                logger.info(f"Creating temporary table {temp_table_name}")
                self["mgyp"] = self[
                    "target_name"
                ]  # .apply(lambda x: mgyp_to_id(x)) ## TODO remove mgyp row and use target name in general
                mgyp_ids = self["mgyp"].to_frame()
                bq_helper.create_temp_table_from_dataframe(mgyp_ids, temp_table_name, expiration_hours=1)

            sequence_query = f"""SELECT p.id AS mgyp, p.sequence
                                 FROM {bq_helper.dataset.dataset_id}.protein p
                                 JOIN {bq_helper.dataset.dataset_id}.{temp_table_name} t ON p.id = t.mgyp"""
            logger.debug(f"run query:\n {sequence_query}")
            sequences = bq_helper.query_to_dataframe(sequence_query)

            if isinstance(output_path, str):
                output_path = Path(output_path)
            dataframe_to_fasta(sequences, output_path)
            logger.info(f"Sequence data exported to {output_path}")

        elif database.lower() == "mysql":
            # TODO: Implement MySQL functionality
            pass
        else:
            raise ValueError("Unsupported database type")

    def fetch_contigs(self):
        """
        Fetches contig information from BigQuery based on the mgyp values in the protein table.

        Returns:
            pandas.DataFrame: A DataFrame containing the contig information.
        """
        bq_helper = BigQueryHelper(**self._setup_bigquery_connection())
        temp_table_name = f"tmp_contigs_{create_md5_hash(self['query_name'][0])[:16]}"
        mgyp_list = self.unique_hits
        bq_helper.create_temp_table_from_dataframe(pd.DataFrame({"mgyp": mgyp_list}), temp_table_name)

        query = f"""
            SELECT
              md.mgyp AS mgyp,
              md.mgyc AS mgyc,
              md.complete AS protein_complete,
              md.start_position AS start,
              md.end_position AS stop,
              md.strand AS strand,
              ct.contig_length AS contig_length,
              ass.accession AS assembly,
              bm.biome_id AS biome_id
            FROM `{bq_helper.dataset.dataset_id}.metadata` md
            JOIN `{bq_helper.dataset.dataset_id}.{temp_table_name}` temp ON md.mgyp = temp.mgyp
            JOIN `{bq_helper.dataset.dataset_id}.contig` ct ON md.mgyc = ct.mgyc
            JOIN `{bq_helper.dataset.dataset_id}.assembly` ass ON ct.assembly_id = ass.assembly_id
            JOIN `{bq_helper.dataset.dataset_id}.biome` bm ON ass.biome_id = bm.biome_id;
        """

        results_df = bq_helper.query_to_dataframe(query)
        bq_helper.delete_table(temp_table_name)
        return results_df
