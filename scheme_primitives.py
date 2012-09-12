from operator import *
from math import floor, ceil
from scheme_utils import *
from scheme_tokens import symbol_escaped
from io import StringIO
                              
try:
    import turtle
except:
    print("warning: could not import the turtle module.", file=sys.stderr)

class SchemeValue:
    """A value manipulated by a Scheme program."""

    def __bool__(self):
        """All Scheme values other than #f are considered true in Python as
        well as Scheme."""
        return True

    def type_name(self):
        return "scheme value"

    def __str__(self):
        return "<{0}@{1}>".format(self.type_name(), hex(id(self)))

    def _repr_(self):
        return str(self)

    def write(self, out):
        """Write a string representation of SELF on OUT, as for the write
        procedure in Scheme."""
        print(str(self), file=out, end="")
        return UNSPEC

    def display(self, out):
        """Write a string representation of SELF on OUT, without escapes,
        as for the display procedure in Scheme."""
        return self.write(out)

    def eqvp(self, other):
        return boolify(self is other)

    def equalp(self, other):
        return self.eqvp(other)

    def atomp(self):
        return TRUE

    def numberp(self):
        return FALSE

    def integerp(self):
        return FALSE

    def booleanp(self):
        return FALSE

    def nullp(self):
        return FALSE

    def pairp(self):
        return FALSE

    def symbolp(self):
        return FALSE

    def procedurep(self):
        return FALSE

    def eof_objectp(self):
        return FALSE

    def length(self):
        """The length of SELF as a Python integer, assuming SELF is a list."""
        raise SchemeError("value has no length")

    def nth(self, k):
        """The Kth element of SELF, assuming it is a list."""
        raise SchemeError("attempt to index a non-list")

    def apply_step(self, args, evaluation):
        """Apply SELF to the arguments ARGS (a Python list of SchemeValues),
        modifying EVALUATION to contain either the resulting value, or
        the body of function and the environment in which it is to be
        evaluated."""
        raise SchemeError("attempt to call something other than a function: {0}"
                          .format(repr(self)))


class S_Expr(SchemeValue):
    """An S_Expr is a Scheme value that can be returned by the reader.
    Other Scheme values can only result from the evaluation of functions or
    forms (e.g., the values of lambda expressions)."""
    
class Pair(S_Expr):
    def __init__(self, x, y):
        self.car = x
        self.cdr = y

    def type_name(self):
        return "pair"

    def atomp(self):
        return FALSE

    def pairp(self):
        return TRUE

    def equalp(self, other):
        if not other.pairp():
            return FALSE
        return self.car.equalp(other.car) and self.cdr.equalp(other.cdr)

    def __repr__(self):
        return "cons({0}, {1})".format(repr(self.car), repr(self.cdr))

    def __str__(self):
        out = StringIO()
        self.display(out)
        return out.getvalue()

    def write(self, f):
        print("(", file=f, end="")             
        self.car.write(f)
        p = self.cdr
        while p.pairp():
            print(" ", file=f, end="")
            p.car.write(f)
            p = p.cdr
        if not p.nullp():
            print(" . ", file=f, end="")
            p.write(f)
        print(")", file=f, end="")
        return UNSPEC

    def display(self, f):
        print("(", file=f, end="")             
        self.car.display(f)
        p = self.cdr
        while p.pairp():
            print(" ", file=f, end="")
            p.car.display(f)
            p = p.cdr
        if not p.nullp():
            print(" . ", file=f, end="")
            p.display(f)
        print(")", file=f, end="")
        return UNSPEC

    def length(self):
        n = 0
        while self.pairp():
            n += 1
            self = self.cdr
        if not self.nullp():
            raise SchemeError("length attempted on improper list")
        return n

    def nth(self, k):
        x = self
        if k < 0:
            raise SchemeError("negative index into list")
        while True:
            if x.nullp():
                raise SchemeError("list index out of bounds")
            elif not x.pairp():
                raise SchemeError("ill-formed list")
            if k == 0:
                return x.car
            x = x.cdr
            k -= 1
            
class Null(S_Expr):
    def __str__(self):
        return "()"

    def type_name(self):
        return "null"

    def nullp(self):
        return TRUE

    def atomp(self):
        return TRUE

    def length(self):
        return 0

NULL = Null()

class Bool(S_Expr):
    """A boolean Scheme value (#t or #f).  For convenience, this class is defined
    so that TRUE (#t) is a true Python value as well and FALSE is a false
    Python value."""

    def __init__(self, is_true):
        self.__truth = bool(is_true)

    def __bool__(self):
        """As a Python value, SELF is True if it is #t and False otherwise."""
        return self.__truth

    def __str__(self):
        return "#t" if self else "#f"

    def type_name(self):
        return "boolean"

    def atomp(self):
        return TRUE

    def booleanp(self):
        return TRUE

TRUE  = Bool(True)
FALSE = Bool(False)

class Number(S_Expr):
    def __init__(self, val):
        self.num_val = val

    def type_name(self):
        return "integer" if type(self.num_val is int) else "real"

    def atomp(self):
        return TRUE

    def numberp(self):
        return TRUE

    def integerp(self):
        return boolify(type(self.num_val) is int)

    def write(self, f):
        print(self.num_val, file=f, end="")
    
    def eqvp(self, other):
        return boolify(other.integerp() and self.num_val == other.num_val)

    def __str__(self):
        return str(self.num_val)

class Symbol(S_Expr):
    def __init__(self, ident):
        self.ident = ident
        self.escaped = symbol_escaped(ident)

    def type_name(self):
        return "symbol"

    def __str__(self):
        return self.ident

    def __repr__(self):
        return "Symbol({0})".format(repr(self.ident))

    def __hash__(self):
        return hash(self.ident)

    @staticmethod
    def string_to_symbol(name):
        """The Symbol whose string value is NAME.  Always returns the same
        Symbol object when given the same string."""
        result = Symbol.symbols.get(name, None)
        if result is None:
            result = Symbol.symbols[name] = Symbol(name)
        return result

    def atomp(self):
        return TRUE

    def symbolp(self):
        return TRUE

    def write(self, f):
        print(self.escaped, file=f, end="")
    
    def display(self, f):
        print(self.ident, file=f, end="")

    # The mapping of names to symbols.
    symbols = {}

class Unspecified(SchemeValue):
    """A class whose sole instance is the "unspecified value", which is 
    returned to represent the value of a Scheme expressions whose value
    is irrelevant and not specified by the Scheme report."""
    def type_name(self):
        return "unspecified value"

UNSPEC = Unspecified()

class Eof(SchemeValue):
    """A class whose sole instance is the "end-of-file object", which is 
    returned to represent an end-of-file condition when reading."""
    def type_name(self):
        return "eof object"

    def eof_objectp(self):
        return TRUE

THE_EOF_OBJECT = Eof()

def check_type(val, predicate, k, name):
    """Returns VAL.  Raises a SchemeError if not PREDICATE(VAL), using
    "argument K of NAME" to describe the offending value in any error message."""
    if not predicate(val):
        raise SchemeError("argument {0} of {1} has wrong type ({2})"
                          .format(k, name, val.type_name()))
    return val

def string_to_atom(s):
    """The number or symbol denoted by S."""
    try:
        return Number(int(s))
    except:
        pass
    try:
        return Number(float(s))
    except:
        pass
    return Symbol.string_to_symbol(s)

##
## Boolean operations 
##

def scm_booleanp(x):
    return x.booleanp()

def scm_not(x):
    return boolify(not x)

def boolify(x):
    """Return the Scheme boolean value that corresponds to the "truthfulness"
    of X in Python."""
    return TRUE if x else FALSE

##
## Equivalence operations
##

def scm_eqp(x, y):
    return boolify(x is y)

def scm_eqvp(x, y):
    return x.eqvp(y)

def scm_equalp(x, y):
    return x.equalp(y)

##
## Operations on lists and pairs.
##

def scm_pairp(x):
    return x.pairp()

def scm_nullp(x):
    return x.nullp()

def scm_listp(x):
    p1 = x
    while not x.nullp():
        if not x.pairp():
            return FALSE
        if x.cdr.nullp():
            return TRUE
        if not x.cdr.pairp():
            return FALSE
        if p1 is x.cdr or p1 is x.cdr.cdr:
            return FALSE
        p1 = x.cdr
        x = p1.cdr
    return TRUE

def scm_length(x):
    check_type(x, scm_listp, 0, 'length')
    return Number(x.length())

def scm_cons(x, y):
    return Pair(x, y)

def scm_car(x):
    check_type(x, scm_pairp, 0, 'car')
    return x.car

def scm_cdr(x):
    check_type(x, scm_pairp, 0, 'cdr')
    return x.cdr

def scm_set_car(x, y):
    check_type(x, scm_pairp, 0, "set-car")
    x.car = y
    return UNSPEC

def scm_set_cdr(x, y):
    check_type(x, scm_pairp, 0, "set-cdr")
    x.cdr = y
    return UNSPEC

def scm_list(*members):
    result = NULL
    for i in range(len(members)-1, -1, -1):
        result = scm_cons(members[i], result)
    return result

def scm_append(*vals):
    if len(vals) == 0:
        return NULL
    result = vals[-1]
    for i in range(len(vals)-2, -1, -1):
        v = vals[i]
        check_type(v, scm_listp, i, "append")
        if not v.nullp():
            r = p = scm_cons(v.car, result)
            v = v.cdr
            while v.pairp():
                p.cdr = scm_cons(v.car, result)
                p = p.cdr
                v = v.cdr
            result = r
    return result

##
## Operations on symbols
##

def scm_symbolp(x):
    return x.symbolp()

##
## Operations on integers
##

def scm_numberp(x):
    return x.numberp()

def scm_integerp(x):
    return x.integerp()

def _check_nums(*vals, pred = scm_numberp):
    """Check that all arguments in VALS satisfy PRED. TYPE_NAME is used
    for error messages."""
    for i in range(len(vals)):
        if not vals[i].numberp():
            msg = "an integer" if pred is scm_integerp else "a number"
            raise SchemeError("operand #{0} is not {1}.".format(i, msg))

def _arith(op, init, vals):
    """Perform the OP operation on the integer values of VALS, with INIT as
    the value when VALS is empty. Returns the result as a Scheme value."""
    _check_nums(*vals)
    s = init
    for i in range(len(vals)):
        s = op(s, vals[i].num_val)
    return Number(s)

def scm_add(*vals):
    return _arith(add, 0, vals)

def scm_sub(val0, *vals):
    if len(vals) == 0:
        return Number(-val0.num_val)
    return _arith(sub, val0.num_val, vals)

def scm_mul(*vals):
    return _arith(mul, 1, vals)

def scm_div(val0, val1):
    _check_nums(val0, val1)
    return Number(val0.num_val / val1.num_val)

def scm_quo(val0, val1):
    _check_nums(val0, val1, pred = scm_integerp)
    if (val0.num_val < 0) == (val1.num_val < 0):
        return Number(val0.num_val // val1.num_val)
    else:
        return Number(-(abs(val0.num_val) // abs(val1.num_val)))

def scm_modulo(val0, val1):
    _check_nums(val0, val1, pred = scm_integerp)
    return Number(val0.num_val % val1.num_val)

def scm_remainder(val0, val1):
    _check_nums(val0, val1, pred = scm_integerp)
    x = val0.num_val
    y = val1.num_val
    return Number(x - (1 if (x<0) == (y<0) else -1) * (abs(x)//abs(y)) * y)

def scm_floor(val):
    _check_nums(val)
    return Number(floor(val.num_val))

def scm_ceil(val):
    _check_nums(val)
    return Number(floor(val.num_val))

def _numcomp(op, x, y):
    _check_nums(x, y)
    return boolify(op(x.num_val, y.num_val))

def scm_eq(x, y):
    return _numcomp(eq, x, y)

def scm_lt(x, y):
    return _numcomp(lt, x, y)

def scm_gt(x, y):
    return _numcomp(gt, x, y)

def scm_le(x, y):
    return _numcomp(le, x, y)

def scm_ge(x, y):
    return _numcomp(ge, x, y)

def scm_max(*args):
    if len(args) == 0:
        return UNSPEC
    _check_nums(*args)
    return _arith(max,args[0].num_val,args) 

def scm_min(*args):
    if len(args) == 0:
        return UNSPEC
    _check_nums(*args)
    return _arith(min,args[0].num_val,args)

##
## Other type tests
##

def scm_atomp(x):
    return x.atomp()

def scm_procedurep(x):
    return x.procedurep()

def scm_eof_objectp(x):
    return x.eof_objectp()

##
## Output
##

def scm_display(val):
    val.display(sys.stdout)
    return UNSPEC

def scm_newline():
    print()
    sys.stdout.flush()
    return UNSPEC

def scm_write(val):
    val.write(sys.stdout)
    return UNSPEC


##
## Other operations
##

def scm_error(msg = None):
    if msg is None:
        msg = ""
    else:
        check_type(msg, scm_symbolp, 0, "error")
        msg = str(msg)
    raise SchemeError(msg)

def scm_exit(code = None):
    if code is None:
        code = 0
    else:
        check_type(code, scm_integerp, 0, "exit")
        code = code.num_val
    sys.exit(code)

##
## Simply Scheme definitions (non-standard)
## 

def sscm_word(*words):
    """The atom resulting from concatenating the representations of the atoms
    in WORDS."""
    result = ""
    for w in words:
        if scm_symbolp(w) or scm_numberp(w):
            result += str(w)
        else:
            raise SchemeError("bad argument type to word: {0}"
                              .format(w.type_name()))
    return string_to_atom(result)


def sscm_first(x):
    """If X is a list, its car.  If X is an integer of symbol, the Scheme
    value denoted by the first character of its printed representation."""
    if x.symbolp() or x.numberp():
        return string_to_atom(str(x)[0])
    elif x.pairp():
        return x.car
    else:
        raise SchemeError("bad argument to first")

def sscm_butfirst(x):
    """If X is a list, its cdr.  If X is a symbol or integer, the Scheme
    value denoted by all but the first character of its printed representation."""
    if x.pairp():
        return x.cdr
    elif x.symbolp() or x.numberp():
        return string_to_atom(str(x)[1:])
    else:
        raise SchemeError("bad argument to butfirst")
    
def sscm_last(x):
    """If X is a list, its last element.  If it is a symbol or number, the
    symbol or number denoted by the last character in its string value."""
    if x.pairp():
        while x.pairp() and not x.cdr.nullp():
            x = x.cdr
        if x.pairp():
            return x.car
    elif x.symbolp() or x.numberp():
        return string_to_atom(str(x)[-1])
    raise SchemeError("bad argument to last")
        
def sscm_butlast(x):
    """If X is a list, the list consisting of all but its last element.
    If it is a symbol or number, the symbol or number denoted by all but
    the last character in its string denotation."""
    if x.pairp():
        result = NULL
        while x.pairp() and not x.cdr.nullp():
            if result.nullp():
                result = last = scm_cons(x.car, NULL)
            else:
                last.cdr = scm_cons(x.car, NULL)
                last = last.cdr
            x = x.cdr
        if x.pairp():
            return result
    elif x.symbolp() or x.numberp():
        return string_to_atom(str(x)[0:-1])
    raise SchemeError("bad argument to butlast")

def sscm_sentence(*vals):
    """Creates a list out of the integers, symbols, and lists in VALS, treating
    the atoms as single-element lists and concatenating the values together."""
    result = NULL
    for i in range(len(vals)-1, -1, -1):
        v = vals[i]
        if scm_listp(v):
            result = scm_append(v, result)
        elif v.integerp() or v.symbolp():
            result = scm_cons(v, result)
        else:
            raise SchemeError("bad argument to sentence")
    return result

##
## Turtle graphics (non-standard)
##

_turtle_screen_on = False

def _tscm_prep():
    global _turtle_screen_on
    if not _turtle_screen_on:
        _turtle_screen_on = True
        turtle.title("Scheme Turtles")
        turtle.mode('logo')

def tscm_forward(n):
    """Move the turtle forward a distance N units on the current heading."""
    _check_nums(n)
    _tscm_prep()
    turtle.forward(n.num_val)
    return UNSPEC

def tscm_backward(n):
    """Move the turtle backward a distance N units on the current heading,
    without changing direction."""
    _check_nums(n)
    _tscm_prep()
    turtle.backward(n.num_val)
    return UNSPEC

def tscm_left(n):
    """Rotate the turtle's heading N degrees counterclockwise."""
    _check_nums(n)
    _tscm_prep()
    turtle.left(n.num_val)
    return UNSPEC

def tscm_right(n):
    """Rotate the turtle's heading N degrees clockwise."""
    _check_nums(n)
    _tscm_prep()
    turtle.right(n.num_val)
    return UNSPEC
    
def tscm_circle(r, extent = None):
    """Draw a circle with center R units to the left of the turtle (i.e.,
    right if N is negative.  If EXTENT is not None, then draw EXTENT degrees
    of the circle only.  Draws in the clockwise direction if R is negative,
    and otherwise counterclockwise, leaving the turtle facing along the
    arc at its end."""
    if extent is None:
        _check_nums(r)
    else:
        _check_nums(r, extent)
    _tscm_prep()
    turtle.circle(r.num_val, extent and extent.num_val)
    return UNSPEC
    
def tscm_setposition(x, y):
    """Set turtle's position to (X,Y), heading unchanged."""
    _check_nums(x, y)
    _tscm_prep()
    turtle.setposition(x.num_val, y.num_val)
    return UNSPEC

def tscm_setheading(h):
    """Set the turtle's heading H degrees clockwise from north (up)."""
    _check_nums(h)
    _tscm_prep()
    turtle.setheading(h.num_val)
    return UNSPEC

def tscm_penup():
    """Raise the pen, so that the turtle does not draw."""
    _tscm_prep()
    turtle.penup()
    return UNSPEC

def tscm_pendown():
    """Lower the pen, so that the turtle starts drawing."""
    _tscm_prep()
    turtle.pendown()
    return UNSPEC

def tscm_showturtle():
    """Make turtle visible."""
    _tscm_prep()
    turtle.showturtle()
    return UNSPEC

def tscm_hideturtle():
    """Make turtle visible."""
    _tscm_prep()
    turtle.hideturtle()
    return UNSPEC

def tscm_clear():
    """Clear the drawing, leaving the turtle unchanged."""
    _tscm_prep()
    turtle.clear()
    return UNSPEC

def tscm_color(c):
    """Set the color to C, a symbol such as red or '#ffc0c0' (representing
    hexadecimal red, green, and blue values."""
    _tscm_prep()
    check_type(c, scm_symbolp, 0, "color")
    turtle.color(str(c))
    return UNSPEC

def tscm_begin_fill():
    """Start a sequence of moves that outline a shape to be filled."""
    _tscm_prep()
    turtle.begin_fill()
    return UNSPEC

def tscm_end_fill():
    """Fill in shape drawn since last begin_fill."""
    _tscm_prep()
    turtle.end_fill()
    return UNSPEC

def tscm_exitonclick():
    """Wait for a click on the turtle window, and then close it."""
    global _turtle_screen_on
    if _turtle_screen_on:
        turtle.exitonclick()
        _turtle_screen_on = False
    return UNSPEC

def tscm_speed(s):
    """Set the turtle's animation speed as indicated by S (an integer in
    0-10, with 0 indicating no animation (lines draw instantly), and 1-10
    indicating faster and faster movement."""
    check_type(s, scm_integerp, 0, "speed")
    _tscm_prep()
    turtle.speed(s.num_val)
    return UNSPEC
