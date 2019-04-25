###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
import gzip

__all__ = ["zopen", ]




def zopen(fname, mode):
    """Opens a file with gzip if it ends on '.gz', otherwise normal.

    Args:
        fname: Name of the file to open.
        mode: File operation mode string.

    Returns:
        File like object.
    """
    if fname.endswith(".gz"):
        return gzip.open(fname, mode)
    else:
        return open(fname, mode)
