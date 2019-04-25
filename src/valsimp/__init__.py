###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
"""General structures for the ValSimP package."""

__all__ = [ "STATUS_NOTFINISHED", "STATUS_NOTRUN", "STATUS_OK", "STATUS_FAILED",
            "STATUS_ERROR", "STATUS_INTERRUPTED",
            "DictClass", "Preparator", "Calculator", "Tester", "Testcase",
          ]

# Possible status of an action.
STATUS_UNKNOWN = -3
STATUS_NOTFINISHED = -2
STATUS_NOTRUN = -1
STATUS_OK = 0
STATUS_FAILED = 1
STATUS_ERROR =  2
STATUS_INTERRUPTED = 3


class DictClass:
    """"Dictionary wrapper giving class like access to dictionary items."""

    def __init__(self, initdict):
        """Initializes DictClass instance.

        Args:
            initdict: Dictionary to wrap.
        """
        self.__dict__.update(initdict)


class Preparator:
    """Abstract class defining the interface of a preparator."""

    def prepare(self):
        """Prepares the current test case."""
        raise NotImplementedError

    def cleanup(self):
        """Cleans up the current test case."""
        raise NotImplementedError


class Calculator:
    """Abstract class defining the interface of a calculator."""

    def run(self):
        """Runs or starts a given calculation."""
        raise NotImplementedError

    def runfinished(self):
        """Determines if the calculation had been finished already.

        Returns:
            True if calculation finished already, False otherwise.
        """
        raise NotImplementedError


class Tester:
    """Abstract class defining the interface of a tester.

    Returns:
        True if test was successfull (passed), False otherwise.
    """
    def test(self):
        raise NotImplementedError


class Testcase(Preparator, Calculator, Tester):
    """Abstract class defining the interface of a test case."""
    pass
