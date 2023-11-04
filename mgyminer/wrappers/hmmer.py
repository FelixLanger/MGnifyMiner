import logging
import tempfile
from pathlib import Path
from typing import Union

from mgyminer.wrappers._base import Program


class esl_sfetch(Program):
    def __init__(self) -> None:
        super().__init__("esl-sfetch")

    @staticmethod
    def _is_indexed(seq_file: Path):
        """
        Check if sequence file has an esl-sfetch index
        :return: bool depending on if file has an index
        """
        index_file = seq_file.parent / (seq_file.name + ".ssi")
        return index_file.is_file()

    def index(self, sequence_file):
        """
        Index a sequence file for esl-sfetch
        :param sequence_file: File to index
        :return: bool
        """
        arguments = ["--index", sequence_file]
        return self._run(arguments)

    def run(
        self,
        sequence_file: Union[Path, str],
        sequence_ids: Union[str, list],
        out_file: Union[Path, str],
        *args: str,
    ) -> bool:
        """
        Run ESL sfetch command to retrieve (sub)-sequences from a sequence file
        :param sequence_file: Path to input sequence file
        :param sequence_ids: Path to namefile with sequence ID to be fetched. One ID per line
        :param out_file: Path to output file location
        :param args: additional esl-sfetch arguments
        :return:
        """

        if isinstance(sequence_ids, str):
            sequence_ids = [sequence_ids]

        if isinstance(sequence_file, str):
            sequence_file = Path(sequence_file)

        if not self._is_indexed(sequence_file):
            logging.info(
                "%s is not indexed \n Indexing %s", sequence_file, sequence_file
            )
            self.index(sequence_file)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            with open(temp_dir / "key_file", "wt") as name_file:
                for sequence_id in sequence_ids:
                    name_file.write(f"{sequence_id} \n")
            arguments = ["-o", out_file, "-f", sequence_file, name_file.name]
            if args:
                arguments.extend(args)
            logging.info("Fetching sequences from %s", sequence_file)
            return self._run(arguments)


class PHmmer(Program):
    def __init__(self, cores: int = 4) -> None:
        super().__init__("phmmer")
        self.cores = cores

    def run(
        self,
        seqfile: Union[str, Path],
        seqdb: Union[str, Path],
        output_file: Union[str, Path],
        notextw: bool = True,
        heuristic: bool = True,
        **kwargs,
    ) -> bool:
        if isinstance(seqfile, str):
            seqfile = Path(seqfile)
        if isinstance(seqdb, str):
            seqdb = Path(seqdb)
        if isinstance(output_file, str):
            output_file = Path(output_file)
        if "tblout" in kwargs:
            tblout = kwargs["tblout"]
        else:
            tblout = output_file.parent / (output_file.stem + ".tbl")
        if "domtblout" in kwargs:
            domtblout = kwargs["domtblout"]
        else:
            domtblout = output_file.parent / (output_file.stem + ".domtbl")
        if "alignment" in kwargs:
            alignment = kwargs["alignment"]
        else:
            alignment = output_file.parent / (output_file.stem + ".sto")

        arguments = [
            "-o",
            str(output_file),
            "--tblout",
            str(tblout),
            "--domtblout",
            str(domtblout),
            "-A",
            str(alignment),
        ]

        if not heuristic:
            arguments.append("--max")
        if notextw:
            arguments.append("--notextw")

        arguments.extend(["--cpu", str(self.cores)])
        arguments.extend([str(seqfile), str(seqdb)])
        logging.info("Running phmmer with %s as query and %s as DB.", seqfile, seqdb)
        return self._run(arguments)


class Hmmbuild(Program):
    def __init__(self, cores: int = 2) -> None:
        super().__init__("hmmbuild")
        self.cores = cores

    def run(
        self,
        hmmfile: Union[str, Path],
        msafile: Union[str, Path],
        single_seq: bool = False,
    ) -> bool:
        arguments = ["--cpu", str(self.cores)]
        if single_seq:
            arguments.append("--singlemx")
        arguments.extend([hmmfile, msafile])
        logging.info("Running hmmbuild to build HMM from %s", msafile)
        return self._run(arguments)


class Hmmsearch(Program):
    def __init__(self, cores: int = 2) -> None:
        super().__init__("hmmsearch")
        self.cores = cores

    def run(
        self,
        hmmfile: Union[str, Path],
        seqdb: Union[str, Path],
        output_file: Union[str, Path],
        tblout: Union[str, Path] = None,
        domtblout: Union[str, Path] = None,
        alignment: Union[str, Path] = None,
        cut_ga: bool = False,
        notextw: bool = True,
        heuristic: bool = True,
        **kwargs,
    ) -> bool:
        arguments = []

        if output_file:
            arguments.extend(["-o", output_file])
        if tblout:
            arguments.extend(["--tblout", tblout])
        if domtblout:
            arguments.extend(["--domtblout", domtblout])
        if alignment:
            arguments.extend(["-A", alignment])
        if cut_ga:
            arguments.append("--cut_ga")
        if not heuristic:
            arguments.append("--max")
        if notextw:
            arguments.append("--notextw")

        arguments.extend(["--cpu", str(self.cores)])
        arguments.extend([str(hmmfile), str(seqdb)])
        logging.info(
            "Running hmmsearch with %s as query hmm and %s as DB.", hmmfile, seqdb
        )
        return self._run(arguments)


class EslAlimanip(Program):
    def __init__(self, cores: int = 1) -> None:
        super().__init__("esl-alimanip")
        self.cores = cores

    def run(
        self,
        msafile: Union[str, Path],
        output_file: Union[str, Path],
        exclude_ids: Union[str, Path] = None,
    ) -> bool:
        arguments = []

        if output_file:
            arguments.extend(["-o", output_file])
        if exclude_ids:
            arguments.extend(["--seq-r", exclude_ids])
        arguments.append(msafile)
        logging.info("Running esl-alimanip with %s", arguments)
        return self._run(arguments)
