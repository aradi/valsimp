###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################

class SimpleTester:
    """Abstract tester class for testers with the same initialization."""

    def __init__(self, *, log, abstol):
        """Initializes a SimpleTester instance.

        Keywords:
           log: Logger object for messages during testing.
           abstol: Maximal allowed tolerance for float differences.
        """
        self.log = log
        self.abstol = abstol

    def test(self):
        raise NotImplementedError
