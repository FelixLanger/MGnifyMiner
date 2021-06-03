import pandas as pd


class hmmerResults:
    """Class to hold HMMER search results in a pandas dataframe"""

    def __init__(self, results):
        self.df = results

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, results) -> pd.DataFrame:
        """read the HMMER Domain Table file into a Pandas dataframe"""
        if results.suffix == ".csv":
            self._df = pd.read_csv(results)
        else:
            self._df = pd.read_csv(
                results,
                sep=r"\s+",
                comment="#",
                index_col=False,
                names=[
                    "target_name",
                    "target_accession",
                    "tlen",
                    "query_name",
                    "query_accession",
                    "qlen",
                    "e-value",
                    "score",
                    "bias",
                    "ndom",
                    "ndom_of",
                    "c-value",
                    "i-value",
                    "dom_score",
                    "dom_bias",
                    "hmm_from",
                    "hmm_to",
                    "ali_from",
                    "ali_to",
                    "env_from",
                    "env_to",
                    "acc",
                    "PL",
                    "UP",
                    "biome",
                    "LEN",
                    "CR",
                ],
                dtype={
                    "target_name": str,
                    "target_accession": str,
                    "tlen": int,
                    "query_name": str,
                    "query_accession": str,
                    "qlen": int,
                    "e-value": float,
                    "score": float,
                    "bias": float,
                    "ndom": int,
                    "ndom_of": int,
                    "c-value": float,
                    "i-value": float,
                    "dom_score": float,
                    "dom_bias": float,
                    "hmm_from": int,
                    "hmm_to": int,
                    "ali_from": int,
                    "ali_to": int,
                    "env_from": int,
                    "env_to": int,
                    "acc": float,
                    "description": str,
                },
            )

            def split_description():
                self._df.drop("LEN", axis=1, inplace=True)
                for column in ["PL", "UP", "biome", "CR"]:
                    self._df[column] = self._df[column].apply(lambda x: x.split("=")[1])

            split_description()

            def calculate_coverage():
                self._df["coverage_hit"] = round(
                    (self._df["ali_to"] - self._df["ali_from"])
                    / self._df["tlen"]
                    * 100,
                    2,
                )
                self._df["coverage_query"] = round(
                    (self._df["ali_to"] - self._df["ali_from"])
                    / self._df["qlen"]
                    * 100,
                    2,
                )

            calculate_coverage()

    def save(self, outfile, sep=";", index=False, **kwargs):
        self.df.to_csv(outfile, sep=sep, index=index, **kwargs)
