###############################################################################
# This file is part of the ValSimP package.
# See the packages LICENSE file for copyright and licensing conditions.
###############################################################################
"""This module contains classes for handling files in tagged format.

The tagged format is a very simple format for storing named numeric arrays. It
consists of special taglines followed by a scalar value or the content of an
array. The taglines have the format

@<name>:<dtype>:<rank>:<shape>

where <name> is a unique alphanumeric identifier for the data which
follows. The type of the data is given as <dtype>. This can be 'real',
'complex', 'integer' or 'logical'. <rank> gives the number of indices of the
array (0 for scalar value). <shape> gives the shape of the array as comma
separated list of integers. If rank is zero, <shape> is not specified.

Example: 2 dimensional 2x15 real array named eigenlevels_dn

@eigenlevels_dn:real:2:2,15
 -0.113800118340220E+003 -0.844328239820224E+001 -0.107940079205845E+002
 -0.382220411906585E+000 -0.883247459509101E+000  0.372541641821865E-001
 -0.376423094429580E-002  0.155774023187805E+000  0.128062316330480E+000
  0.424260506305019E+000  0.432450936322496E+000  0.958999472193787E+000
  0.107685549184055E+001  0.199098681475960E+001  0.239787747378676E+001
  0.396348350241529E+001  0.507913876324391E+001  0.773060984307095E+001
  0.105784242675752E+002  0.150210046035295E+002  0.222461401555423E+002
  0.295118991789216E+002  0.485039454693113E+002  0.596375351220563E+002
  0.114396736066691E+003  0.127861086132756E+003  0.323973885778375E+003
  0.312550781039824E+003  0.159919603974785E+004  0.109261160350897E+004
"""
import re
import functools as ft
import numpy as np
import valsimp.io as vspio

############################################################################
# Exceptions
############################################################################

class InvalidEntryError(Exception):
    """Raised if entry can't be initialized or wrong type of entry is passed"""

    def __init__(self, start=0, end=0, msg=""):
        """Initializes InvalidEntryError instance.

        Args:
            start (0): Starting line of block where error occured.
            end (0): First line after block where error occured.
            msg (""): Error message.
        """
        self.start = start
        self.end = end
        self.msg = msg


class ConversionError(Exception):
    """Raised if error occurs during conversion from string"""
    pass


############################################################################
# Conversion functors
############################################################################

class Converter:
    """Base class for string to value converters"""

    def __init__(self, nolist=False):
        """Initializes a Converter instance.

        Args:
            nolist (False): If True, a single value is returned after the
                converstion instead of a list.
        """
        self.nolist = nolist


    def __call__(self, strvalue):
        """Function call interface of Converter.

        Args:
            strvalue: String represenation of the values to convert. It can be
                a string or a list of strings.

        Returns:
            Plain 1D list of the converted values or just one value, if
            appropriate option had been set at initialization time.

        Raises:
            ConversionError: Any failure at conversion.
        """
        if isinstance(strvalue, list):
            values = []
            for line in strvalue:
                values += line.split()
        else:
            values = strvalue.split()

        if self.nolist and len(values) > 1:
            raise ConversionError("Too many values")
        result = self.convert(values)
        if self.nolist:
            return result[0]
        else:
            return result


    def convert(self, values):
        """Abstract routine for conversion.

        Args:
            values: List of strings representing the values to convert.

        Returns:
            List of converted objects.

        Raises:
            ConversionError: Any problems during conversion.
        """
        raise NotImplementedError



class FloatConverter(Converter):
    """String to float converter."""

    def convert(self, values):
        try:
            ll = np.array(values, dtype=float)
        except Exception as ex:
            raise ConversionError("Unable to convert string to float: "
                                  + str(ex))
        return ll



class IntConverter(Converter):
    """String to integer converter."""

    def convert(self, values):
        try:
            ll = np.array(values, dtype=int)
        except Exception as ex:
            raise ConversionError("Unable to convert string to integer: "
                                  + str(ex))
        return ll



class ComplexConverter(Converter):
    """String to complex number converter.

    Complex number is assumed to be represented as two subsequent float numbers
    for the real and the imaginary part (as it would come out from a simple
    write statement in Fortran).
    """

    def __call__(self, strvalue):
        values = strvalue.split()
        if len(values) % 2:
            raise ConversionError("Complex converter needs even strings")
        if self.nolist and len(values) != 2:
            raise ConversionError("Too many values")
        result = self.convert(values)
        if self.nolist:
            return result[0]
        else:
            return result


    def convert(self, values):
        try:
            tmp = np.array(values, dtype=float)
            ll = tmp[0::2] + 1.0j * tmp[1::2]
        except Exception as ex:
            raise ConversionError("Unable to convert string to complex: "
                                  + str(ex))
        return ll



class LogicalConverter(Converter):
    """String to logical converter."""

    def convert(self, values):
        ll = []
        for val in values:
            if val == 'T' or val == 't':
                ll.append(True)
            elif val == 'F' or val == 'f':
                ll.append(False)
            else:
                raise ConversionError("Unable to convert '%s' to logical: "
                                      % val)
        return np.array(ll, dtype=bool)



############################################################################
# Tagged data related objects
############################################################################

class TaggedEntry:
    """Represents a tagged entry with its data.

    Attributes:
        tagline: The entire tag line as string.
        name: String with the name of the tag label.
        dtype: String with the data type.
        rank: Integer with the rank of the array.
        shape: Tuple of integers, representing the shape of the array.
        data: Converted data belonging to this tag.
    """

    # Converter from string for different types
    _CONVERTERS = { "integer" : IntConverter(),
                    "real" : FloatConverter(),
                    "complex" : ComplexConverter(),
                    "logical" : LogicalConverter()
                    }

    _PAT_TAGLINE = re.compile(r"""^@(?P<name>[^: ]+)\s*:(?P<dtype>[^:]+):"""
                              r"""(?P<rank>\d):(?P<shape>(?:\d+(?:,\d+)*)?)$""")


    def __init__(self, tagline, data):
        """Instantiates an TaggedEntry instance.

        Args:
            tagline: Line containing the tag.
            data: String representation of the data. (Either single string
                or list of strings.)
       """
        self.tagline = tagline.strip()
        match = self._PAT_TAGLINE.match(tagline)
        if not match:
            raise InvalidEntryError(msg="Invalid tag format")
        self.name = match.group("name")
        self.dtype = match.group("dtype")
        self.rank = int(match.group("rank"))
        if self.rank > 0:
            self.shape = tuple([ int(s) for s in
                                 match.group("shape").split(",") ])
        else:
            self.shape = ()

        if not self.dtype in self._CONVERTERS:
            raise InvalidEntryError(msg="Invalid data dtype '%s'" % self.dtype)
        try:
            data = self._CONVERTERS[self.dtype](data)
        except ConversionError as ex:
            raise InvalidEntryError(msg=str(ex))
        if self.shape:
            if len(self.shape) != self.rank:
                raise InvalidEntryError(msg="Incompatible rank and shape")
            if len(data) != ft.reduce(lambda x,y: x*y, self.shape):
                raise InvalidEntryError(msg="Invalid nr. of values")
        elif self.rank != 0:
            raise InvalidEntryError(msg="Incompatible rank and shape")
        self.data = np.reshape(data, self.shape)


    def iscomparable(self, other):
        """Checks if an other instance is comparable to the current one."""

        return (other.name == self.name and other.dtype == self.dtype
                and other.rank == self.rank and other.shape == self.shape)

    def __str__(self):
        return "%s\n%s" % (self.tagline, str(self.data))



class TaggedCollection:
    """Collection of tagged entries.

    Provides interface for appending and removing TaggedEntries from a
    collection and for searching tag names using regular expressions.
    """

    def __init__(self, entries):
        """Initializes a TaggedCollection instance.

        Args:
            entries: Iterable object containing TaggedEntries, which will be
                used as initial content for the collection.
        """
        self._names = {}
        self._entries = []
        self.extend(entries)


    def extend(self, entries):
        """Adds new elements to the collection.

        Args:
            entries: List of TaggedEntries, which should be added.
        """
        for entry in entries:
            self._names[entry.name] = len(self._names)
            self._entries.append(entry)


    def matching_taglines(self, pattern):
        """Returns the entries matching a regular expression.

        The regular expression is matched against the string representation of
        the tagged entry without its data: '<name>:<dtype>:<rank>:<shape>'

        Args:
            pattern: Compiled regular expression.

        Returns:
            List with matching entries.
        """
        result = [ entry for entry in self._entries
                   if pattern.match(entry.tagline) ]
        return result


    def get(self, name):
        """Returns an entry with a given name from the collection.

        Args:
            name: Name of the entry to return.

        Returns:
            The entry with the given name, or None this does not exist.
        """
        ii = self._names.get(name)
        if not ii is None:
            result = self._entries[ii]
        else:
            result = None
        return result


    def remove(self, name):
        """Removes the specified entry from the collection.

        Args:
            name: Name of the entry to delete.
        """
        ii = self._names.pop(name, None)
        if not ii is None:
            del self._entries[ii]
            del self._taglines[ii]

    def __iter__(self):

        class TaggedCollectionIter:

            def __init__(self, tagged):
                self.tagged = tagged
                self.ind = -1

            def __next__(self):
                self.ind += 1
                if self.ind < len(self.tagged._entries):
                    return self.tagged._entries[self.ind]
                else:
                    raise StopIteration

        return TaggedCollectionIter(self)



############################################################################
# Parses the file containing the data and returns TaggedEntries
############################################################################

class TaggedReader:
    """Iterator over the tagged entries in a file."""

    # Pattern for lines containing the description of a tag
    PAT_TAGLINE = re.compile(r"""^(?P<name>[^: ]+)\s*:
                                 (?P<dtype>[^:]+):
                                 (?P<rank>\d):
                                 (?P<shape>(?:\d+(?:,\d+)*)?)$""",
                             re.VERBOSE | re.MULTILINE)


    def __init__(self, source):
        """Initializes a TaggedReader.

        Args:
            source: File name or file like object with tagged data.
        """
        if hasattr(source, "read"):
            self._fp = source
        else:
            self._fp = vspio.zopen(source, "r")
        dummy, self._lasttagline = self._readnext_tagline()
        self._lasttagline_ind = len(dummy)


    def _readnext_tagline(self):
        """Read until next tag line.

        Return:
           Tuple (lines, tagline) with lines being a list of lines read before
           tagline had been found, and tagline being the next tagline.
        """
        lines = []
        line = self._fp.readline()

        while line:
            if type(line) is bytes:
                line = str(line, encoding="ascii")
            if line.startswith("@"):
                break
            lines.append(line)
            line = self._fp.readline()
        return (lines, line)


    def __iter__(self):
        """Iterator over tagged entries."""
        return self


    def __next__(self):
        """Next tagged entry."""
        if not self._lasttagline:
            raise StopIteration

        datalines, tagline = self._readnext_tagline()
        tagline_ind = self._lasttagline_ind + len(datalines)
        try:
            result = TaggedEntry(self._lasttagline, datalines)
        except InvalidEntryError as ee:
            raise InvalidEntryError(self._lasttagline_ind + 1, tagline_ind,
                                    msg=ee.msg)

        self._lasttagline = tagline
        self._lastagline_ind = tagline_ind

        return result



if __name__ == "__main__":
    import io

    txt = """zora                :logical:0:
 F
@kinetic_energy:real:0:
  0.524967175993157E+003
@nuclear_energy:real:0:
 -0.125312452831053E+004
@coulomb_energy:real:0:
  0.231452951325734E+003
@xc_energy:real:0:
 -0.292353792272788E+002
@confinement_energy:real:0:
  0.000000000000000E+000
@total_energy:real:0:
 -0.525939780218915E+003
@eigenlevels_up:real:2:2,15
 -0.113800118340220E+003 -0.844328239820224E+001 -0.107940079205845E+002
 -0.382220411906585E+000 -0.883247459509101E+000  0.372541641821865E-001
 -0.376423094429580E-002  0.155774023187805E+000  0.128062316330480E+000
  0.424260506305019E+000  0.432450936322496E+000  0.958999472193787E+000
  0.107685549184055E+001  0.199098681475960E+001  0.239787747378676E+001
  0.396348350241529E+001  0.507913876324391E+001  0.773060984307095E+001
  0.105784242675752E+002  0.150210046035295E+002  0.222461401555423E+002
  0.295118991789216E+002  0.485039454693113E+002  0.596375351220563E+002
  0.114396736066691E+003  0.127861086132756E+003  0.323973885778375E+003
  0.312550781039824E+003  0.159919603974785E+004  0.109261160350897E+004
@eigenlevels_dn:real:2:2,15
 -0.113800118340220E+003 -0.844328239820224E+001 -0.107940079205845E+002
 -0.382220411906585E+000 -0.883247459509101E+000  0.372541641821865E-001
 -0.376423094429580E-002  0.155774023187805E+000  0.128062316330480E+000
  0.424260506305019E+000  0.432450936322496E+000  0.958999472193787E+000
  0.107685549184055E+001  0.199098681475960E+001  0.239787747378676E+001
  0.396348350241529E+001  0.507913876324391E+001  0.773060984307095E+001
  0.105784242675752E+002  0.150210046035295E+002  0.222461401555423E+002
  0.295118991789216E+002  0.485039454693113E+002  0.596375351220563E+002
  0.114396736066691E+003  0.127861086132756E+003  0.323973885778375E+003
  0.312550781039824E+003  0.159919603974785E+004  0.109261160350897E+004
"""

    fp = io.StringIO(txt)
    tagged = TaggedCollection(TaggedReader(fp))
    res = tagged.get("kinetic_energy")
    print(res)
    res = tagged.get("eigenlevels_up")
    print(res)
    pattern = re.compile("@eigenlevels_.*:.*:.*:.*")
    for match in tagged.matching_taglines(pattern):
        print(match)
