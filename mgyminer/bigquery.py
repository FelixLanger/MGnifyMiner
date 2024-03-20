from google.cloud import bigquery
from datetime import datetime, timedelta


class BigQueryHelper:
    def __init__(self, credentials_path, dataset_id):
        self._dataset_id = dataset_id
        self.client = bigquery.Client.from_service_account_json(credentials_path)

    @property
    def project(self):
        return self.client.project

    @property
    def dataset(self):
        try:
            dataset_ref = self.client.dataset(self._dataset_id, project=self.project)
            dataset = self.client.get_dataset(dataset_ref)
            if dataset:
                return dataset_ref
            else:
                raise ValueError(f"Dataset {self._dataset_id} does not exist in project {self.project}.")
        except Exception as e:
            raise ValueError(f"Failed to get dataset {self._dataset_id}.") from e

    @dataset.setter
    def dataset(self, dataset_id):
        try:
            dataset_ref = self.client.dataset(dataset_id, project=self.project)
            dataset = self.client.get_dataset(dataset_ref)
            if dataset:
                self._dataset_id = dataset_id
            else:
                raise ValueError(f"Dataset {dataset_id} does not exist in project {self.project}.")
        except Exception as e:
            raise ValueError(f"Failed to set dataset to {dataset_id}.") from e

    def create_temp_table_from_dataframe(self, df, table_name, expiration_hours=1):
        """
        Creates a temporary table from a pandas DataFrame.
        The table will expire after the specified number of hours.
        """
        temp_table_reference = self.dataset.table(table_name)
        job = self.client.load_table_from_dataframe(df, temp_table_reference)
        job.result()  # Wait for the load job to finish
        expiration_time = datetime.now() + timedelta(hours=expiration_hours)
        table = self.client.get_table(temp_table_reference)
        table.expires = expiration_time
        return self.client.update_table(table, ["expires"])

    def query_to_dataframe(self, query):
        """
        Executes a SQL query and returns the results as a pandas DataFrame.
        """
        query_job = self.client.query(query)  # Start the query job
        results = query_job.result()  # Wait for the query to finish
        return results.to_dataframe()
