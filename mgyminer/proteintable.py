import json
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
from loguru import logger

from mgyminer.config import load_config
from mgyminer.constants import BIOMES
from mgyminer.utils import (
    NumpyJSONEncoder,
    biome_str_to_ids,
    create_md5_hash,
    dataframe_to_fasta,
    mgyp_to_id,
    proteinID_to_mgyp,
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

    def _convert_special_columns(self, data):
        for col in self.SPECIAL_COLUMNS:
            if col in data.columns:
                data[col] = data[col].apply(self._string_to_json)

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
        # By far the most efficient way to count nested unique values
        flattened_array = self.flatten(nested_column)
        return pd.Series(flattened_array).nunique()

    def unique_nested(self, nested_column):
        flattened_array = self.flatten(nested_column)
        return pd.Series(flattened_array).unique()

    def pick(self, filters: Dict[str, Any]):
        """
        Filters the DataFrame based on specified conditions.

        This method allows filtering of the DataFrame's rows based on specified conditions for each column.
        It supports two types of filters:
        1. Numeric range filters (using a dictionary with 'min' and/or 'max' keys).
        2. List-based filters (using a list of strings).

        Parameters:
        filters (Dict[str, Any]): A dictionary where each key is a column name and each value is the condition for
                                  filtering. The condition can be a dictionary (for numeric ranges) or a list of
                                  strings (for list-based filtering).

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
                    if column in ["biome", "biomes"]:
                        if all(isinstance(element, int) for element in condition):
                            condition = [BIOMES[biome_id] for biome_id in condition]
                        condition = biome_str_to_ids(condition, BIOMES)
                    result_table = self._apply_list_filter(result_table, column, condition)

        query_string = " and ".join(query_conditions)
        return ProteinTable(result_table.query(query_string) if query_conditions else result_table)

    @staticmethod
    def _apply_list_filter(dataframe, column, values):
        """
        Applies a list-based filter to the DataFrame.

        This method filters rows where the specified column contains any of the values in the provided list.
        It's primarily used internally by the `filter_table` method for handling list-based filtering conditions.

        Parameters:
        dataframe (DataFrame): The DataFrame to be filtered.
        column (str): The name of the column to apply the filter to. The column should contain list-like elements.
        values (List[str]): A list of strings. Rows where the column contains any of these strings will be included in
                            the output.

        Returns:
        DataFrame: A new DataFrame containing only the rows that meet the list-based filter condition.

        """
        mask = dataframe[column].apply(lambda x: any(item in x for item in values))
        filtered_df = dataframe[mask]
        return ProteinTable(filtered_df)

    def save(self, path, index=False):
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
        """
        Set up the connection to Google BigQuery.
        This method loads credentials and configuration settings.
        """
        cfg = load_config()

        try:
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(cfg["Google service account json"])
            logger.info("Loaded Google service account credentials")
        except Exception as e:
            logger.error("Invalid Google service account JSON key file: " + str(e))
            raise Exception("Invalid Google service account JSON key file") from e

        bigquery_dataset = cfg.get("BigQuery Dataset")
        bigquery_project = cfg.get("BigQuery project")
        if not bigquery_dataset or not bigquery_project:
            error_message = "BigQuery Dataset and/or BigQuery Project not set in the configuration."
            logger.error(error_message)
            raise ValueError(error_message)

        return credentials, bigquery_dataset, bigquery_project

    def fetch_metadata(self, database: str):
        if database.lower() == "bigquery":
            (
                credentials,
                bigquery_dataset,
                bigquery_project,
            ) = self._setup_bigquery_connection()

            columns_to_check = ["complete", "truncation", "assemblies", "biomes"]
            if all(column in self.columns for column in columns_to_check):
                logger.info(
                    f"Skipping fetching of data from BigQuery because {columns_to_check} columns are already present"
                )
                return

            self["mgyp"] = self["target_name"].apply(lambda x: mgyp_to_id(x))
            table_name = create_md5_hash(self["query_name"][0])[:16]
            mgyp_ids = self["mgyp"].to_frame()
            mgyp_ids.to_gbq(
                f"{bigquery_dataset}.{table_name}",
                project_id=bigquery_project,
                if_exists="replace",
                credentials=credentials,
            )
            # THIS JOIN WILL AUTOMATICALLY REMOVE THE PROTEINS WITHOUT METADATA
            # LEFT JOIN ON protein_metadata AND assembly TABLE WOULD BE NEEDED
            # TO KEEP THE LINES WHERE THESE TABLES DON'T HAVE DATA
            join_query = f"""
            SELECT
                t.mgyp AS mgyp,
                ARRAY_AGG(DISTINCT m.complete) as complete,
                ARRAY_AGG(DISTINCT COALESCE(m.truncation, '11')) as truncation,
                a.pfam_architecture as pfam_architecture,
                ARRAY_AGG(DISTINCT asmbly.accession) AS assemblies,
                ARRAY_AGG(DISTINCT asmbly.biome) AS biomes
            FROM 
                {bigquery_dataset}.{table_name} t
            JOIN 
                {bigquery_dataset}.protein p ON t.mgyp = p.id
            LEFT JOIN 
                {bigquery_dataset}.architecture a ON p.architecture = a.id
            JOIN 
                {bigquery_dataset}.protein_metadata m ON t.mgyp = m.mgyp
            JOIN 
                {bigquery_dataset}.assembly asmbly ON m.assembly = asmbly.id
            GROUP BY 
                t.mgyp, a.pfam_architecture;
            """
            logger.debug(f"run query:\n {join_query}")
            metadata = pd.read_gbq(join_query, project_id=bigquery_project, credentials=credentials)
            result = pd.merge(self, metadata, on="mgyp")
            result.drop("mgyp", axis=1, inplace=True)
            return ProteinTable(result)

        elif database.lower() == "mysql":
            # TODO: Implement fetching from MySQL
            pass
        else:
            raise ValueError("Unsupported database type")

    def fetch_and_export_sequences(self, output_path: Union[Path, str], database):
        if database.lower() == "bigquery":
            (
                credentials,
                BIGQUERY_DATASET,
                BIGQUERY_PROJECT,
            ) = self._setup_bigquery_connection()

            temp_table_name = create_md5_hash(self["query_name"][0])[:16]

            check_query = f"SELECT table_name FROM {BIGQUERY_DATASET}.INFORMATION_SCHEMA.TABLES WHERE table_name = '{temp_table_name}'"
            check_result = pd.read_gbq(check_query, project_id=BIGQUERY_PROJECT, credentials=credentials)

            if check_result.empty:
                logger.info(f"Creating temporary table {temp_table_name}")
                self["mgyp"] = self["target_name"].apply(lambda x: mgyp_to_id(x))
                mgyp_ids = self["mgyp"].to_frame()
                mgyp_ids.to_gbq(
                    f"{BIGQUERY_DATASET}.{temp_table_name}",
                    project_id=BIGQUERY_PROJECT,
                    if_exists="replace",
                    credentials=credentials,
                )

            sequence_query = f"""SELECT p.id AS mgyp, p.sequence
                                 FROM {BIGQUERY_DATASET}.protein p
                                 JOIN {BIGQUERY_DATASET}.{temp_table_name} t ON p.id = t.mgyp"""
            logger.debug(f"run query:\n {sequence_query}")
            sequences = pd.read_gbq(sequence_query, project_id=BIGQUERY_PROJECT, credentials=credentials)

            if isinstance(output_path, str):
                output_path = Path(output_path)
            sequences["mgyp"] = sequences["mgyp"].apply(lambda x: proteinID_to_mgyp(x))
            dataframe_to_fasta(sequences, output_path)
            logger.info(f"Sequence data exported to {output_path}")

        elif database.lower() == "mysql":
            # TODO: Implement MySQL functionality
            pass
        else:
            raise ValueError("Unsupported database type")
