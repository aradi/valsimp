###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
import sys
import valsimp as vsp

REPORT_SEPARATOR = "-"*79
REPORT_HEADER = ("%s\n%-40s %-12s %-12s %-12s\n%s"
                 % (REPORT_SEPARATOR, "testcase", "prepare", "run", "test",
                    REPORT_SEPARATOR))

class TestLogger:
    """Simple class for logging test related events"""

    INDENTWIDTH = 2
    LINEWIDTH = 80
    RESULT_STR = { vsp.STATUS_OK: "OK",
                   vsp.STATUS_FAILED: "FAILED",
                   vsp.STATUS_ERROR: "Error",
                   vsp.STATUS_INTERRUPTED: "Interrupted",
                   vsp.STATUS_NOTRUN: "Not run",
                   vsp.STATUS_NOTFINISHED: "Not finished",
                 }

    def __init__(self, fp=None):
        """Initializes TestLogger instance.

        Args:
            fp: Optional, file object in which log should be written
                (def.: stdout)
        """
        if fp:
            self.fp = fp
        else:
            self.fp = sys.stdout
        self._indentlevel = 0
        self._setindent()

    def write(self, txt, breakline=False):
        """Writes the given string (line by line) into the log.

        Args:
            txt: Text to write.
            breakline: Optional, if set to True, lines are broken to fit
                to the line width with current indentation taken into account.
        """
        self.writelines(txt.split("\n"), breakline)

    def writeline(self, line, breakline=False):
        """Writes the given line into the log.

        Args:
            line: Line to write.
            breakline: Optional, if set to True, lines are broken to fit
                to the line width with current indentation taken into account.
        """
        if breakline:
            lines = self._breakline(line)
        else:
            lines = [ line, ]
        for curline in lines:
            self.fp.write(self._indent)
            self.fp.write(curline)
            self.fp.write("\n")

    def writelines(self, lines, breakline=False):
        """Writes given lines into the log.

        Args:
            lines: List of lines to write.
            breakline: Optional, if set to True, lines are broken to fit
                to the line width with current indentation taken into account.
        """
        for line in lines:
            self.writeline(line, breakline)

    def teststart(self, testcase, action):
        """Indicates the start of a given test action in the log.

        This should be followed by a correpsonding testresult() call.

        Args:
            testcase: Name of the test case.
            action: Name of the action being performed.
        """
        self.writeline("%s:\t%s:\tstarted..." % (testcase, action))
        self.increaseindent()

    def testresult(self, testcase, action, result, msg=""):
        """Writes the result of a test action into the log.

        This should follow a corresponding teststart() call.

        Args:
            testcase: Name of the test case.
            action: Name of the action being performed.
            result: Result flag of the action.
            msg: Optional message to print as well (e.g. error message)
        """
        self.decreaseindent()
        resultstr = self.RESULT_STR.get(result, "UNKNOWN")
        self.writeline("%s:\t%s:\t%s" % (testcase, action, resultstr))
        if msg:
            self.increaseindent()
            self.write(msg, breakline=True)
            self.decreaseindent()


    def testsummary(self, testcase, status_prepare, status_run, status_test):
        """Prints a summary of a given test case (as a line of a table).

        Args:
            testcase: Name of the testcase.
            status_prepare: Status of the preparation.
            status_run: Status of the run.
            status_test: Status of the test.
        """
        self.writeline("%-40s %-12s %-12s %-12s"
                   % (testcase, self.RESULT_STR[status_prepare],
                      self.RESULT_STR[status_run],
                      self.RESULT_STR[status_test]))

    def testheader(self, testcase):
        """Prints a header for a given testcase

        Args:
            testcase: Test for which the header should be printed.
        """
        self.writeline("=" * self.LINEWIDTH)
        self.writeline("==  " + testcase)
        self.writeline("=" * self.LINEWIDTH)

    def testblock_open(self, line=""):
        """Opens a subblock in the test log (increase indentation).

        Args:
            line: Optional, line to print before indentation is increased.
        """
        if line:
            self.writeline(line, self.LINEWIDTH)
        self.increaseindent()

    def testblock_close(self, line=""):
        """Closes a subblock in the test log (decrease indentation).

        Args:
            line: Optinal, line to print after indentation had been decreased.
        """
        self.decreaseindent()
        if line:
            self.writeline(line, self.LINEWIDTH)

    def testsuccess(self, msg):
        """Indicates success of a given testing action.

        Args:
            msg: Message to print together with the success indication.
        """
        lines = self._breakline(msg, 72)
        lines[-1] = (lines[-1]
                     + " " * (72 - len(lines[-1]) - self._indentwidth)
                     + "[Ok]")
        self.writelines(lines)

    def testfailure(self, msg):
        """Indicates failure of a given testing action.

        Args:
            msg: Message to print together with the failure indication.
        """
        lines = self._breakline(msg, 72)
        lines[-1] = (lines[-1]
                     + " " * (72 - len(lines[-1]) - self._indentwidth)
                     + "[FAILED]")
        self.writelines(lines)

    def increaseindent(self):
        """Increases indentation level by one."""
        self._indentlevel += 1
        self._setindent()

    def decreaseindent(self):
        """Decreases indentation level by one."""
        if self._indentlevel:
            self._indentlevel -= 1
            self._setindent()

    def _setindent(self):
        """Updates variables depending on the indentation level."""
        self._indentwidth = self._indentlevel * self.INDENTWIDTH
        self._indent = " " * self._indentwidth

    def _breakline(self, line, width=None):
        """Breaks a line into peaces to fit onto the screen.

        Args:
            line: Line to split.
            width: Optional, width of the screen. If not specified default
                screen line width is taken.

        Return:
            List of lines, with lenghts shorter than the screen line width
            minus the length of the current indentation string.
        """
        if width:
            ll = width - self._indentwidth
        else:
            ll = self.LINEWIDTH - self._indentwidth
        return [ line[ii:ii+ll] for ii in range(0, len(line), ll) ]
