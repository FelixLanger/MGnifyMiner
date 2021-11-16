import abc
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class Program(abc.ABC):
    def __init__(self, program: str, verbose: bool = False) -> None:
        self.program = program
        self.verbose = verbose

    @property
    def program(self) -> str:
        return self._program

    @program.setter
    def program(self, program: str):
        program_path = shutil.which(program)

        if program_path is None:
            logging.error(
                'Program "%s" could not be found. Please install it and retry', program
            )
            raise ProgramNotFoundError()
        self._program = shutil.which(program)

    def _run(
        self, arguments: list, stdout_file: Optional[Path] = None, **kwargs
    ) -> bool:
        """
        Help function to run program on the command line.
        Outputs stdout to stdout_file if it is defined. Otherwise stdout will be ignored.
        Logg the stderr from program and raise a warning.

        :param arguments: List of command parameters to use for running the program.
                          eg. ["-o", "output_file", "--verbose"]
        :param stdout_file: file to write stdout to
        :param kwargs: other kwargs for subprocess.Popen
        :return: bool
        """

        command = [self.program]
        command.extend(arguments)
        try:
            if stdout_file:
                with open(stdout_file, "w") as fout:
                    process = subprocess.Popen(
                        command,
                        stdout=fout,
                        stderr=subprocess.PIPE,
                        text=True,
                        **kwargs
                    )
                    while True:
                        stderr_message = process.stderr.readline().strip()
                        if not stderr_message:
                            break
                        logging.warning(
                            "%s raised an error while running: %s",
                            self.program,
                            stderr_message,
                        )
                    return True
            else:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    **kwargs
                )
                while True:
                    stderr_message = process.stderr.readline()
                    if not stderr_message:
                        break
                    logging.warning(
                        "%s raised an error while running: %s",
                        self.program,
                        stderr_message,
                    )
                return True

        except subprocess.CalledProcessError as error:
            logging.error("%s failed with message: %s", self.program, error)

    @abc.abstractmethod
    def run(self):
        """
        Run the actual command using the _run function
        """
        return NotImplemented


class ProgramNotFoundError(Exception):
    """
    Exception to raise when program could not be found
    """
