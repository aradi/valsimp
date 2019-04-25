###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################

__all__ = [ "NonCommentLines" ]


class NonCommentLines:
    """Iterator over nonempty lines of a file with removed comments."""

    def __init__(self, fp, comment):
        """Initializes NonCommentLines instance.

        Args:
            fp: File like object to be read.
            comment: Comment character.
        """
        self.fp = fp
        self.comment = comment

    def __iter__(self):
        return self

    def __next__(self):
        words = [ '', ]
        while not words[0].strip():
            line = self.fp.readline()
            # If file object returns bytes (e.g.GZipFile), convert to str.
            if type(line) is bytes:
                line = str(line, encoding="ascii")
            if not line:
                raise StopIteration
            words = line.split(self.comment, 1)
        return words[0]


if __name__ == "__main__":
    import io
    myfile = io.StringIO("line1 # comment1\n"
                         "# comment2\n"
                         "line3 # comment3\n")
    for line in NonCommentLines(myfile, "#"):
        print("Line: '%s'" % line)
