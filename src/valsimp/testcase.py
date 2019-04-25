###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
import valsimp as vsp

class SimpleTestcase(vsp.Testcase):
    """Simple test case object.

    Created from a preparator, calculator and a tester, it passes the testcase
    calls to the appropriate object respectively.
    """

    def __init__(self, preparator, calculator, tester):
        """Initializes a SimpleTestcase instance.

        Args:
            preparator: Object providing preparator interface.
            calculator: Object providing calculator interface.
            tester: Object providing tester interface.
        """
        self.preparator = preparator
        self.calculator = calculator
        self.tester = tester

    def prepare(self):
        """Calls the preparators prepare() method."""
        self.preparator.prepare()

    def run(self):
        """Calls the calculators run() method."""
        self.calculator.run()

    def runfinished(self):
        """Calls the calculators runfinished() method."""
        return self.calculator.runfinished()

    def test(self):
        """Calls the testers test() method."""
        return self.tester.test()

    def cleanup(self):
        """Calls the preparators cleanup() method."""
        self.preparator.cleanup()
