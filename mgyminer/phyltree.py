import logging
import os
import subprocess


class runner:
    """
    Class to run commandline software
    """

    def __init__(self, program):
        self.program = program

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, program):
        def which(program):
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


class esl_sfetch(runner):
    def __init__(self):
        super().__init__("esl-sfetch")

    def run(self, input_file, sequence, outfile):
        args = [self.program, input_file, sequence]
        try:
            with open(outfile, "w") as fout:
                subprocess.run(args, stdout=fout, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"an error occurred while executing {self.program}")
            print(e.output)
            return False
