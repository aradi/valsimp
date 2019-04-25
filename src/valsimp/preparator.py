###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
import os.path
import shutil
import valsimp as vsp

class SimplePreparator(vsp.Preparator):
    """Simple preparator, copying files and directories between directories."""

    INPDIR = "input"

    def __init__(self, inputdir, workdir):
        """Initializes SimpePreparator instance.

        Args:
            inputdir: Directory, where the input files/directories can be found.
            workdir: Target directory, where all entries in inputdir should be
                copied to.
        """
        self.inpdir = inputdir
        self.workdir = workdir

    def prepare(self):
        """Copies all files/directories from input to working directory."""
        for relname in os.listdir(self.inpdir):
            absname = os.path.join(self.inpdir, relname)
            if os.path.isdir(absname):
                shutil.copytree(absname, self.workdir)
            else:
                shutil.copy(absname, self.workdir)

    def cleanup(self):
        """Does not do any special cleanup action."""
        pass
