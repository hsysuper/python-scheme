"""Utilities used in various modules of the Scheme interpreter."""

import sys

class SchemeError(BaseException):
    """General-purpose exception indicating an anticipated error in a
    Scheme program."""

def char_set(start, end):
    """The set of characters whose codes are >= START and <= END."""
    return set(map(chr, range(ord(start), ord(end)+1)))

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise IOError."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))


class Buffer(object):
    """A Buffer provides a way of accessing a sequence of items concatenated
    together from lists of items.  Its constructor takes an iterator,
    called "the source", that returns a list of items each time it is 
    called, or None to indicate the end of data.  The Buffer in 
    effect concatenates the sequences returned from its source and then
    supplies the items from them one at a time through its pop() 
    method, calling the source for more sequences of items only when
    needed.  In addition, Buffer provides a .current property to look at the
    next item to be supplied, without sequencing past it.  The constructor
    will also accept a list as source, which it treats as an iterator that
    returns just that list as its single value.

    The motivation is to allow us to conveniently tokenize a line of input at
    a time, while allowing most of the program to ignore the line boundaries.

    >>> buf = Buffer(['(', 'newline', ')'])
    >>> buf.current
    '('
    >>> buf.pop()
    '('
    >>> buf.pop()
    'newline'
    >>> buf.current
    ')'
    >>> buf.pop()
    ')'
    >>> buf.current  # value is now None
    >>> buf = Buffer(iter( [['15'], ['(', ')']] ))
    >>> buf.pop()
    '15'
    >>> buf.pop()
    '('
    >>> buf.pop()
    ')'
    >>> buf.pop()  # returns None
    """
    __EMPTY = iter(())

    def __init__(self, source):
        self.sequence_number = 0
        self.index = 0
        if type(source) is list or type(source) is tuple:
            self.list = source
            self.source = Buffer.__EMPTY
        else:
            self.source = source
            self.list = ()
        
    def pop(self):
        """Remove the next item from self and return it. If self has
        exhausted its source, returns None."""
        current = self.current
        self.index += 1
        return current

    @property
    def current(self):
        """Return the current element, or None if none exists."""
        while self.index >= len(self.list):
            self.index = 0
            for self.list in self.source:
                self.sequence_number += 1
                break
            else:
                self.list = ()
                return None
        return self.list[self.index]

    @property
    def source_location(self):
        """The number of times SELF's source has been called."""
        return self.sequence_number

    def __repr__(self):
        return 'Buffer({0}, {1})'.format(repr(self.contents), repr(self.index))
