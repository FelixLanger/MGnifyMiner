import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd


class runner:
    """
    Class to run commandline software
    """

    def __init__(self, program: Union[Path, str], verbose: bool = False) -> None:
        self.program = program
        self.verbose = verbose

    @property
    def program(self) -> str:
        return self._program

    @program.setter
    def program(self, program: Union[Path, str]):
        def which(program: Union[Path, str]):
            """Function that mimics the which shell command. Returns the path to a program,
            or None if no executable is found.
            stackoverflow.com/questions/377017/test-if-executable-exists-in-python
            """

            def is_exe(fpath):
                return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

            fpath, fname = os.path.split(program)
            if fpath:
                if is_exe(program):
                    return program
            else:
                for path in os.environ["PATH"].split(os.pathsep):
                    exe_file = os.path.join(path, program)
                    if is_exe(exe_file):
                        return exe_file

            return None

        if which(program) is not None:
            self._program = program
        else:
            logging.warning(f"{program} is not installed!")

    def _run(self, command: List, stdout_file: Optional[Path] = None, **kwargs) -> bool:
        """Help function for run(). Distinguishes between tools that natively give output to stdout and
        tools that give output piles per default
        """
        if stdout_file:
            try:
                with open(stdout_file, "w") as fout:
                    subprocess.run(command, stdout=fout, check=True, **kwargs)
                return True
            except subprocess.CalledProcessError as e:
                print(f"an error occurred while executing {self.program}")
                print(e.output)
                return False
        else:
            # Capture program stdout in debug mode, else discard
            print_stdout = subprocess.DEVNULL if self.verbose is False else None
            try:
                subprocess.run(command, check=True, stdout=print_stdout, **kwargs)
                return True
            except subprocess.CalledProcessError as e:
                print(f"an error occurred while executing {self.program}")
                print(e.output)
                return False


class esl_sfetcher(runner):
    def __init__(self) -> None:
        super().__init__("esl-sfetch")

    def run(
        self,
        input_file: Union[Path, str],
        namefile: Union[Path, str],
        outfile: Union[Path, str],
        args: Optional[List] = None,
    ) -> bool:
        """
        Run ESL sfetch command to retrieve (sub)-sequences from a sequence file
        :param input_file: Path to input sequence file
        :param namefile: Path to namefile with sequence ID to be fetched. One ID per line
        :param outfile: Path to output file location
        :param args: additional esl-sfetch arguments
        :return:
        """
        command = [self.program]
        if args is not None:
            command.extend(args)
        command.extend([input_file, namefile])
        return self._run(command, stdout_file=outfile)


class hmmbuilder(runner):
    def __init__(self, verbose: bool = False) -> None:
        super().__init__("hmmbuild", verbose=verbose)

    def run(
        self,
        hmmfile: Union[Path, str],
        msafile: Union[Path, str],
        args: Optional[List] = None,
        single_seq: bool = True,
    ):
        """
        Run HMMER hmmbuild command, single seqence mode per default.
        :param hmmfile: Path to desirec hmm file location
        :param msafile: Path to sequence or MSA used to build hmm
        :param args: optional hmmbuild commands
        :param single_seq: flag to activate single sequence mode, default=True
        :return:
        """
        args = args.append("--singlemx") if args is not None else ["--singlemx"]
        command = [self.program]
        if args is not None:
            command.extend(args)
        command.extend([hmmfile, msafile])
        return self._run(command)


class hmmaligner(runner):
    def __init__(self, verbose: bool = False) -> None:
        super().__init__("hmmalign", verbose=verbose)

    def run(
        self,
        hmmfile: Union[Path, str],
        output_file: Union[Path, str],
        seqfile: Union[Path, str],
        outformat: str = "clustal",
        args: Optional[List] = None,
    ) -> bool:
        """
        Run HMMER hmmalign command.
        :param hmmfile: path to single profile
        :param output_file: path to output file location
        :param seqfile: path to sequences fasta that should be aligned
        :param outformat: format of output alignment (stockholm,a2m,afa,psiblast,clustal,phylip)
        :param args: additional hmmalign arguments
        :return:
        """

        format_types = ["stockholm", "a2m", "afa", "psiblast", "clustal", "phylip"]
        if outformat not in format_types:
            raise ValueError(f"Invalid format. Expected one of: {format_types}")

        command = [self.program] + ["-o", output_file, "--outformat", outformat]
        if args is not None:
            command.extend(args)
        command.extend([hmmfile, seqfile])
        self._run(command)


class esl_reformater(runner):
    def __init__(self) -> None:
        super().__init__("esl-reformat")

    def run(
        self,
        seqfile: Union[Path, str],
        output_file: Union[Path, str],
        format: str,
        args: Optional[List] = None,
    ) -> bool:
        """
        Run esl-reformat command
        :param seqfile: Path to input sequence or aligmnent file
        :param output_file: Path to output file location
        :param format: Desired output format. One of ("stockholm", "a2m", "afa", "psiblast","clustal", "phylip")
        :param args: additional arguments for esl-reformat
        :return:
        """
        format_types = ["stockholm", "a2m", "afa", "psiblast", "clustal", "phylip"]
        if format not in format_types:
            raise ValueError(f"Invalid format. Expected one of: {format_types}")
        command = [self.program] + ["-o", output_file]
        if args is not None:
            command.extend(args)
        command.extend([format, seqfile])
        self._run(command)


class fastTree(runner):
    def __init__(self, verbose: bool = True) -> None:
        super().__init__("fasttree", verbose=verbose)

    def run(
        self,
        alignment: Union[Path, str],
        outfile: Union[Path, str],
        args: Optional[List] = None,
        threads: int = 3,
    ):
        env_vars = os.environ
        env_vars["OMP_NUM_THREADS"] = str(threads)

        command = [self.program, "-out", outfile]
        if args is not None:
            command.extend(args)
        command.append(alignment)
        return self._run(command, env=env_vars)


class treebuilder:
    def __init__(self, args) -> None:
        self.inputfile = args.input
        self.fetcher = esl_sfetcher()
        self.aligner = hmmaligner()
        self.hmmbuilder = hmmbuilder()
        self.query = args.query
        self.tree = (
            args.output
            if args.output
            else Path(str(args.input).replace(args.input.suffix, ".tree"))
        )
        self.alignment = (
            args.alignment
            if args.alignment
            else Path(str(args.input).replace(args.input.suffix, ".afa"))
        )

    def make_alignment(self: Union[Path, str]) -> Path:
        with tempfile.TemporaryDirectory() as tmpdir:
            keyfile = Path(tmpdir) / "keyfile"
            sequences = Path(tmpdir) / "sequences"
            hmm = Path(tmpdir) / "hmm"
            seq_df = pd.read_csv(self.inputfile)

            def _idpluscoords(row):
                if row["ndom"] > 1:
                    domain = "_" + str(row["ndom"])
                else:
                    domain = ""
                return f"{row['target_name']}{domain}/{row['env_from']}-{row['env_to']}"

            seq_df["dom_acc"] = seq_df.apply(lambda row: _idpluscoords(row), axis=1)
            seq_df[["dom_acc", "env_from", "env_to", "target_name"]].to_csv(
                keyfile, index=False, header=False, sep=" "
            )
            self.fetcher.run("test_seqDB.fa", keyfile, sequences, args=["-Cf"])
            self.hmmbuilder.run(hmm, self.query)
            # Append query sequence to the alignment to add it to the tree
            with open(sequences, "at") as fout, open(self.query, "rt") as fin:
                fout.write(fin.read())
            self.aligner.run(hmm, self.alignment, sequences, outformat="afa")

    def build_tree(self) -> Path:
        ft = fastTree()
        print(self.alignment, self.tree)
        ft.run(self.alignment, self.tree)


def tree(args):
    t = treebuilder(args)
    t.make_alignment()
    t.build_tree()
