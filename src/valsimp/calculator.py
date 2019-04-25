###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
import os.path
import subprocess as sp
import valsimp as vsp

class SimpleCalculator(vsp.Calculator):
    """A very simple calculator executing a given binary."""

    def __init__(self, workdir, cmdline):
        """Initialies SimpleCalculator.

        Args:
            workdir: Working directory, where the program should be exectuded.
            cmdline: List of command line parameters (with program name as
                first entry in the list).
        """
        self.workdir = workdir
        self.cmdline = cmdline
        self.finishfile = os.path.join(self.workdir, ".runfinished")

    def run(self):
        """Runs the specified command line.

        If a file 'STDIN' exits in the working directory, its content will be
        piped to the command as standard input. Standard output will be stored
        in the file 'STDOUT', standard error in 'STDERR'. When the command
        line execution finished, a special file will be created to signalise
        finished run.
        """
        self._setunfinished()
        cmdline = self.cmdline
        stdin = os.path.join(self.workdir, "STDIN")
        stdout = os.path.join(self.workdir, "STDOUT")
        stderr = os.path.join(self.workdir, "STDERR")
        if os.path.isfile(stdin):
            fin = open(stdin, "r")
        else:
            fin = None
        fout = open(stdout, "w")
        ferr = open(stderr, "w")
        process = sp.Popen(cmdline, stdin=fin, stdout=fout,
                           stderr=ferr, close_fds=True, cwd=self.workdir)
        process.wait()
        self._setfinished()

    def runfinished(self):
        """Checks whether the special file signalising finished run exists."""
        return os.path.isfile(self.finishfile)

    def _setfinished(self):
        """Create the signal file for finished run."""
        open(self.finishfile, "w").close()

    def _setunfinished(self):
        """Remove the signal file for finished run."""
        if os.path.isfile(self.finishfile):
            os.remove(self.finishfile)
