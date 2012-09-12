"""
A Scheme Interpreter in Python with Turtle Graph Functionality. 

Author: Siyuan (Jack) He
        Joseph Moghadam

"""

import re
import sys
import traceback
from io import StringIO
from ucb import main, trace
from scheme_tokens import *
from scheme_utils import *
from scheme_primitives import *
from ucb import interact

# Name of file containing Scheme definitions.
SCHEME_PRELUDE_FILE = "scheme_prelude.scm"

class PrimitiveFunction(SchemeValue):
    """A Scheme function implemented directly in Python."""

    def __init__(self, func):
        """The function that applies Python function FUNC to its operands."""
        self.func = func

    def type_name(self):
        return "primitive procedure"

    def apply_step(self, args, evaluation):
        #Jack 5:00PM.14.April.2012
        try:
            evaluation.set_value(self.func(*args))
        except SystemExit as code:
            raise sys.exit(code)
        except BaseException as err:
            raise SchemeError(err)

    def __repr__(self):
        return "PrimitiveFunction({0})".format(repr(self.func))

class LambdaFunction(SchemeValue):
    """A function defined by lambda expression or the complex define form."""

    def __init__(self, formals, body, env):
        """A function whose formal parameter list is FORMALS (in Scheme format),
        whose body is the single Scheme expression BODY, and whose environment
        is the EnvironFrame ENV.  A lambda expression containing multiple expressions,
        such as (lambda (x) (set! y x) (+ x 1)) can be handled by
        using (begin (set! y x) (+ x 1)) as the body."""
        self.formals = formals
        self.body = body
        self.env = env

    def type_name(self):
        return "closure"

    def apply_step(self, args, evaluation):
        #Jack 5:00PM.14.April.2012
        evaluation.set_expr(self.body, self.env.make_call_frame(self.formals, args))
        
        

    def write(self, out):
        print("<(lambda ", file=out, end='')
        self.formals.write(out)
        print(" ", end='', file=out)
        self.body.write(out)
        print("), {0}>".format(repr(self.env)), file=out, end='')

    def __repr__(self):
        return "LambdaFunction({0}, {1}, {2})" \
               .format(repr(self.formals), repr(self.body), repr(self.env))

class EnvironFrame:

    """An environment frame, representing a mapping from Scheme symbols to
    Scheme values, possibly enclosed within another frame."""

    def __init__(self, enclosing):
        """An empty frame that is attached to the frame ENCLOSING."""
        self.inner = {}
        self.enclosing = enclosing

    def __getitem__(self, sym):
        return self.find(sym).inner[sym]

    def __setitem__(self, sym, val):
        self.find(sym).inner[sym] = val

    def __repr__(self):
        if self.enclosing is None:
            return "<Global frame at {0}>".format(hex(id(self)))
        else: 
            return "<Frame at {0} --> {1}>".format(hex(id(self)),
                                                   repr(self.enclosing))

    def find(self, sym):
        """The environment frame at or enclosing SELF that defined SYM.  It
        is an error if it does not exist."""
        e = self
        while e is not None:
            if sym in e.inner:
                return e
            e = e.enclosing
        raise SchemeError("unknown identifier: {0}".format(str(sym)))

    def make_call_frame(self, formals, vals):
        """A new local frame attached to SELF in which the symbols in
        the Scheme formal parameter list FORMALS are bound to the
        Scheme values in the Python list VALS.  FORMALS has either of the
        formats allowed by the Evaluation.check_formals method.  If
        the last cdr in FORMALS is a null list (that is, if FORMALS is
        an ordinary Scheme list), then the number of formals must be the same
        as the number of VALS, and each symbol in FORMALS is bound to the
        corresponding value in VALS.  If the last cdr in FORMALS is a
        symbol, then the number of values in VALS  must be at least as large as
        the number of preceding ("normal") formal symbols, and the last
        formal symbol is bound to a Scheme list containing the remaining
        values in VALS (which may be 0)."""
        "*** YOUR CODE HERE ***"
        #Jack 6:52PM.14.April.2012
        env = EnvironFrame(self)
        while formals.pairp():
            if len(vals) == 0:
                raise SchemeError('Too few arguments given')
            env.define(formals.car, vals.pop(0))
            formals = formals.cdr
        if formals.nullp():
            if len(vals) != 0:
                raise SchemeError('Too many arguments given')
        else:
            env.define(formals, scm_list(*vals))
        return env

    def define(self, sym, val):
        """Define Scheme symbol SYM to have value VAL in SELF."""
        self.inner[sym] = val

class Evaluation:
    """An Evaluation represents the information needed to evaluate an
    expression: the expression and the environment in which it is to be
    evaluated.  The step method performs at least part of the evaluation of
    the expression, either leaving behind the final value, or else another
    intermediate expression and environment to be further evaluated."""

    def __init__(self, expr, env):
        """An evaluation of EXPR in the environment ENV."""
        self.expr = expr
        self.env = env
        self.value = None

    def set_value(self, value):
        """Set the value of SELF to VALUE, completing the evaluation."""
        assert value is not None
        self.expr = None
        self.value = value

    def set_expr(self, expr, env = None):
        """Replace SELF's expression with EXPR.  If ENV is non-null, replace
        the environment in which EXPR is being evaluated with ENV."""
        self.expr = expr
        if env is not None:
            self.env = env

    def evaluated(self):
        """True iff this evaluation is finished."""
        return self.value is not None

    def step(self):
        """Either complete SELF's computation, causing all remaining
        side effects and producing a value, or else partially perform the
        remaining computation, leaving SELF with an expression and environment
        that denote the remaining computation."""
        expr = self.expr
        #Jack 04:30PM.14.April.2012
        if expr.symbolp():
            #Joey 11:30PM.13.April.2012
            #Jack 08:00PM.14.April.2012
            self.set_value(self.env.find(expr).inner[expr])
        elif expr.atomp():
            self.set_value(expr)
        elif not scm_listp(expr):
            raise SchemeError("malformed list: {0}".format(str(self)))
        else:
            op = expr.car
            if op.symbolp():
                Evaluation.SPECIAL_FORMS.get(op, Evaluation.do_call_form)(self)
            else:
                self.do_call_form()

    def full_eval(self, expr, env = None):
        """The value of EXPR when evaluated in environment ENV (SELF.env by
        default."""
        return Evaluation(expr, env or self.env).step_to_value()

    def step_to_value(self):
        """Perform evaluation steps on SELF until a value is reached."""
        while not self.evaluated():
            self.step()
        return self.value

    # Special forms.  Each of these methods is called when
    # SELF.expr apparently contains the kind of special form the method
    # handles.  It checks the syntactic validity of the form, and partially 
    # evaluates it, either leaving the final value or an expression
    # that carries out the rest of the computation.

    def do_quote_form(self):
        self.check_form(2, 2)
        self.set_value(self.expr.cdr.car)

    def do_lambda_form(self):
        self.check_form(3)
        self.check_formals(self.expr.cdr.car)
        #Jack 06:00PM.14.April.2012
        formals = self.expr.cdr.car
        body = Pair(Symbol.string_to_symbol('begin'), self.expr.cdr.cdr)
        self.set_value(LambdaFunction(formals, body, self.env))

    def do_if_form(self):
        #Joey 2:30PM.15.April.2012
        self.check_form(3, 4)
        cond = self.full_eval(self.expr.cdr.car)
        if not cond == FALSE:
            self.set_expr(self.expr.cdr.cdr.car)
        else:
            if self.expr.cdr.cdr.cdr.nullp():
                self.set_value(UNSPEC)
            else:
                self.set_expr(self.expr.cdr.cdr.cdr.car)
                        
  
    def do_and_form(self):
        self.check_form(1)
        if self.expr.length() == 1:
            self.set_value(TRUE)
        elif self.expr.length() == 2:
            self.set_expr(self.expr.cdr.car)
        else:
            expression = self.expr.cdr
            veri = self.full_eval(expression.car)
            if veri == FALSE:
                self.set_value(veri)
            else:
                self.set_expr(Pair(Symbol.string_to_symbol('and'),expression.cdr))

    def do_or_form(self):
        self.check_form(1)
        if self.expr.length() == 1:
            self.set_value(FALSE)
        elif self.expr.length() == 2:
            self.set_expr(self.expr.cdr.car)
        else:
            expression = self.expr.cdr
            veri = self.full_eval(expression.car)
            if veri == FALSE:
                self.set_expr(Pair(Symbol.string_to_symbol('or'),expression.cdr))
            else:
                self.set_value(veri)

    def do_cond_form(self):
        self.check_form(1)
        num_clauses = self.expr.length()
        for i in range(1, num_clauses):
            clause = self.expr.nth(i)
            self.check_form(1, expr = clause)
            if clause.car is self._ELSE_SYM and i == num_clauses-1:
                test = TRUE
                if clause.cdr.nullp():
                    raise SchemeError("badly formed else clause")
            else:
                #Jack 06:00PM.14.April.2012
                cond_value = self.full_eval(clause.car)
                if cond_value:
                    test = TRUE
                else:
                    test = FALSE
            if test:
                if clause.length() == 1:
                    self.set_value(test)
                elif clause.cdr.car is self._ARROW_SYM:
                    self.set_expr(Pair(clause.cdr.cdr.car, Pair(cond_value,NULL)))
                else:
                    self.set_expr(Pair(Symbol.string_to_symbol('begin'),clause.cdr))
                return
        self.set_value(UNSPEC)

    def do_set_bang_form(self):
        #Joey 2:10PM.15.April.2012
        self.check_form(3, 3)
        target = self.expr.nth(1)
        self.env.find(target).define(target, self.full_eval(self.expr.nth(2)))
        self.set_value(UNSPEC)
        
    #Joey 11:30PM.13.April.2012    
    def do_define_form(self):
        self.check_form(3)
        target = self.expr.nth(1)
        if target.symbolp():
            self.check_form(3,3)
            self.env.define(target, self.full_eval(self.expr.nth(2)))
            self.set_value(UNSPEC)
        elif not target.pairp():
            raise SchemeError("bad argument to define")
        else:
            self.check_formals(target.cdr)
            #Jack 02:00PM.15.April.2012
            formals = target.cdr
            body = Pair(Symbol.string_to_symbol('begin'), self.expr.cdr.cdr) 
            self.env.define(target.car, LambdaFunction(formals, body, self.env))
            self.set_value(UNSPEC)

    def do_begin_form(self):
        self.check_form(2)
        for k in range(1, self.expr.length()-1):
            self.full_eval(self.expr.nth(k))
        self.set_expr(self.expr.nth(self.expr.length()-1))

    def do_let_form(self):
        self.check_form(3)
        bindings = self.expr.cdr.car
        exprs = self.expr.cdr.cdr
        if not scm_listp(bindings):
            raise SchemeError("bad bindings list in let form")
        symbols = NULL
        vals = []
        #Jack 04:18PM.14.April.2012
        while bindings.pairp():
            symbols = Pair(bindings.car.car, symbols)
            vals.insert(0,self.full_eval(bindings.car.cdr.car))
            bindings = bindings.cdr
        let_frame = self.env.make_call_frame(symbols, vals)
        for i in range(0, exprs.length()-1):
            self.full_eval(exprs.car, let_frame)
            exprs = exprs.cdr
        self.set_expr(exprs.car, let_frame)

    # Extra credit
    def do_let_star_form(self):
        self.check_form(3)
        bindings = self.expr.cdr.car
        exprs = self.expr.cdr.cdr
        if not scm_listp(bindings):
            raise SchemeError("bad bindings list in let form")
        #Jack 04:18PM.14.April.2012
        let_frame = self.env
        while bindings.pairp():
            symbol = bindings.car.car
            value = self.full_eval(bindings.car.cdr.car, let_frame)
            bindings = bindings.cdr
            let_frame = let_frame.make_call_frame(Pair(symbol,NULL), [value])
        for i in range(0, exprs.length()-1):
            self.full_eval(exprs.car, let_frame)
            exprs = exprs.cdr
        self.set_expr(exprs.car, let_frame)

    def do_case_form(self):
        self.check_form(2)
        value = self.full_eval(self.expr.cdr.car)
        clauses = self.expr.cdr.cdr
        result = UNSPEC
        done = False
        #Jack 04:51PM.14.April.2012
        while clauses.pairp() and not done:
            current = clauses.car
            atom = current.car
            if current.car is self._ELSE_SYM:
                expr = Pair(Symbol.string_to_symbol('begin'), current.cdr)
                done = True
                if not clauses.cdr.nullp():
                    raise SchemeError("badly formed else clause")
            else:
                while atom.pairp() and not done:
                    if value.eqvp(atom.car):
                        expr = Pair(Symbol.string_to_symbol('begin'), current.cdr)
                        done = True
                    atom = atom.cdr
            clauses = clauses.cdr
        self.set_expr(expr)

    # Symbols that are used in special forms.

    _AND_SYM = Symbol.string_to_symbol("and")
    _ARROW_SYM = Symbol.string_to_symbol("=>")
    _BEGIN_SYM = Symbol.string_to_symbol("begin")
    _CASE_SYM = Symbol.string_to_symbol("case")
    _COND_SYM = Symbol.string_to_symbol("cond")
    _DEFINE_SYM = Symbol.string_to_symbol("define")
    _ELSE_SYM = Symbol.string_to_symbol("else")
    _IF_SYM = Symbol.string_to_symbol("if")
    _LAMBDA_SYM = Symbol.string_to_symbol("lambda")
    _LET_SYM = Symbol.string_to_symbol("let")
    _LET_STAR_SYM = Symbol.string_to_symbol("let*")
    _OR_SYM = Symbol.string_to_symbol("or")
    _QUOTE_SYM = Symbol.string_to_symbol("quote")
    _SET_BANG_SYM = Symbol.string_to_symbol("set!")

    # Mapping of symbols that introduce special forms to the methods that
    # handle the forms.
    SPECIAL_FORMS = {
        _AND_SYM :     do_and_form,
        _BEGIN_SYM :   do_begin_form,
        _CASE_SYM :    do_case_form,
        _COND_SYM :    do_cond_form,
        _DEFINE_SYM :  do_define_form,
        _IF_SYM :      do_if_form,
        _LAMBDA_SYM :  do_lambda_form,
        _LET_SYM :     do_let_form,
        _LET_STAR_SYM: do_let_star_form,
        _OR_SYM :      do_or_form,
        _QUOTE_SYM  :  do_quote_form,
        _SET_BANG_SYM: do_set_bang_form,
    }

    # Function calls

    def do_call_form(self):
        self.check_form(1)
        op = self.full_eval(self.expr.car)
        #Jack 04:30PM.14.April.2012
        op.apply_step([self.full_eval(self.expr.nth(x)) for x in range(1,self.expr.length())], self)

    # Utility methods for checking the structure of Scheme values that
    # represent programs.

    def check_form(self, min, max = None, expr = None):
        """Check EXPR (default SELF.expr) is a proper list whose length is
        at least MIN and no more than MAX (default: no maximum). Raises
        a SchemeError if this is not the case."""
        if expr is None:
            expr = self.expr
        if not scm_listp(expr):
            raise SchemeError("badly formed expression")
        L = expr.length()
        if L < min:
            raise SchemeError("too few operands in form")
        elif max is not None and L > max:
            raise SchemeError("too many operands in form")

    @staticmethod
    def check_formals(formal_list):
        """Check that FORMAL_LIST is a valid parameter list having either 
        the form (sym1 sym2 ... symn) or else (sym1 sym2 ... symn . symrest),
        where each symx is a distinct symbol."""
        formal_pylist = []
        formals = formal_list
        while formals.pairp():
            if not formals.car.symbolp():
                raise SchemeError("Wrong format of formals")
            if formals.car in formal_pylist:
                raise SchemeError("Duplicated formals")
            formal_pylist.append(formals.car)
            formals = formals.cdr
        if formals.nullp():
            pass
        else:
            if not formals.symbolp():
                raise SchemeError("Wrong format of formals")
            if formals in formal_pylist:
                raise SchemeError("Duplicated formals")

def scm_eval(sexpr):
    # To begin with, this function simply returns SEXPR unchanged, without
    # doing any evaluation.  This allows you to test your solution to
    # problem 1: the interpreter will just echo all the expressions in your
    # input when you type
    #    python3 scheme.py tests.scm
    # (or other file full of Scheme expressions).  When you are finished
    # with Problem 1, replace the return statement below with 
    #    return Evaluation(sexpr, the_global_environment).step_to_value()
    # which is what evaluation is supposed to do.

    #Joey 11:30PM.13.April.2012
    return Evaluation(sexpr, the_global_environment).step_to_value()
    # return sexpr

def scm_apply(func, arg0, *other_args):
    """If OTHER_ARGS is empty, apply the function value FUNC to the argument 
    list in ARG0 (a Scheme list).  Otherwise, the values of ARG0 and all but
    the last value in OTHER_ARGS are first added (with scm_cons) to
    the beginning of the last argument in OTHER_ARGS (which must be 
    a Scheme list), and then passed to the value of FUNC."""
    if other_args:
        check_type(other_args[-1], scm_listp, len(other_args), 'apply')
        args = [arg0]
        for i in range(len(other_args)-1):
            args.append(other_args[i])
        rest = other_args[-1]
    else:
        check_type(arg0, scm_listp, 0, 'apply')
        args = []
        rest = arg0

    while not rest.nullp():
        args.append(rest.car)
        rest = rest.cdr
    
    evaluation = Evaluation(None, None)
    func.apply_step(args, evaluation)
    return evaluation.step_to_value()


def call_with_input_file(filename, proc):
    """Temporarily set the current input port to the file named by FILENAME,
    (a string) and call PROC.  Always restores the input port when done."""
    with scheme_open(filename) as inp:
        call_with_input_source(inp, proc)

def call_with_input_source(source, proc):
    """Temporarily set the current input port to read lines from the
    SOURCE (an iterator returning lines or a string).  Always restores
    the input port when done."""
    global input_port
    input_port0 = input_port
    try:
        input_port = Buffer(tokenize_lines(source))
        proc()
    finally:
        input_port = input_port0
    
def read_eval_print(prompt = None):
    """Read and evaluate from the current input port until the end of file.
    If PROMPT is not None, use it to prompt for input and print values of
    each expression."""
    while True:
        try:
            if prompt is not None:
                print(prompt, end = "")
            sys.stdout.flush()
            expr = scm_read()
            if expr is THE_EOF_OBJECT:
                return
            val = scm_eval(expr)
            if prompt is not None and val is not UNSPEC:
                scm_write(val)
                scm_newline()
        except SchemeError as exc:
            if not exc.args[0]:
                print("Error", file=sys.stderr)
            else:
                print("Error: {0}".format(exc.args[0]), file=sys.stderr)
            sys.stderr.flush()

def scm_read():
    def read_tail():
        """Assuming that input is positioned inside a Scheme list or pair,
        immediately before a final parenthesis or another item in the list,
        return the remainder of the list from that point.  Thus, returns
        (2 3) when positioned at the carat in "(1 ^ 2 3)", returns
        () when positioned at the carat in "(1 2 3 ^ )", and returns
        the pair (2 . 3) when positioned at the carat in (1 ^ 2 . 3)."""
        if input_port.current is None:
            raise SchemeError("unexpected EOF")
        syntax, val = input_port.current
        "*** YOUR CODE HERE ***"
        #Jack 04:30PM.09.April.2012
        if syntax == ')':
            input_port.pop()
            return NULL
        elif syntax == '.':
            input_port.pop()
            result = scm_read()
            input_port.pop()
            return result
        else:
            first = scm_read()
            rest = read_tail()
            return Pair(first, rest)

    if input_port.current is None:
        return THE_EOF_OBJECT

    syntax, val = input_port.pop()

    if syntax == NUMERAL:
        return Number(val)
    elif syntax == BOOLEAN:
        return boolify(val)
    elif syntax == SYMBOL:
        return Symbol.string_to_symbol(val)
    elif syntax == "'":
        #Jack 04:30PM.09.April.2012
        return Pair(Symbol.string_to_symbol('quote'),Pair(scm_read(),NULL))
    elif syntax == "(":
        return read_tail()
    else:
        raise SchemeError("unexpected token: {0}".format(repr(val)))

def scm_load(sym):
    check_type(sym, scm_symbolp, 0, "load")
    call_with_input_file(str(sym), read_eval_print)
    return UNSPEC

##
## Initialization
##

_PRIMITIVES = (
    ("eqv?", scm_eqvp),
    ("eq?", scm_eqp),
    ("equal?", scm_equalp),
    ("atom?", scm_atomp),

    ("pair?", scm_pairp),
    ("null?", scm_nullp),
    ("list?", scm_listp),
    ("cons", scm_cons),
    ("car", scm_car),
    ("cdr", scm_cdr),
    ("length", scm_length),
    ("set-car!", scm_set_car),
    ("set-cdr!", scm_set_cdr),
    ("list", scm_list),
    ("append", scm_append),

    ("integer?", scm_integerp),
    ("+", scm_add),
    ("-", scm_sub),
    ("*", scm_mul),
    ("/", scm_div),
    ("quotient", scm_quo),
    ("modulo", scm_modulo),
    ("remainder", scm_remainder),
    ("floor", scm_floor),
    ("ceil", scm_ceil),
    ("<", scm_lt),
    (">", scm_gt),
    ("=", scm_eq),
    ("<=", scm_le),
    (">=", scm_ge),

    ("boolean?", scm_booleanp),
    ("not", scm_not),
    ("symbol?", scm_symbolp),

    ("write", scm_write),
    ("display", scm_display),
    ("newline", scm_newline),
    ("read", scm_read),
    ("load", scm_load),

    ("eval", scm_eval),
    ("apply", scm_apply),

    ("error", scm_error),
    (["exit", "bye"], scm_exit),

    ("word", sscm_word),
    ("first", sscm_first),
    (["bf", "butfirst"], sscm_butfirst),
    ("last", sscm_last),
    (["bl", "butlast"], sscm_butlast),
    (["sentence", "se"], sscm_sentence),

    (['forward', 'fd'], tscm_forward),
    (['backward', 'back', 'bk'], tscm_backward),
    (['right', 'rt'], tscm_right),
    (['left', 'lt'], tscm_left),
    ('circle', tscm_circle),
    (['setpos', 'setposition', 'goto'], tscm_setposition),
    (['seth', 'setheading'], tscm_setheading),
    (['penup', 'pu'], tscm_penup),
    (['pendown', 'pd'], tscm_pendown),
    (['showturtle', 'st'], tscm_showturtle),
    (['hideturtle', 'ht'], tscm_hideturtle),
    ('clear', tscm_clear),
    ('color', tscm_color),
    ('begin_fill', tscm_begin_fill),
    ('end_fill', tscm_end_fill),
    ('exitonclick', tscm_exitonclick),
    ('speed', tscm_speed),

    #Primitives forgotten by the coder
    ('max', scm_max),
    ('min', scm_min),

)

def define_primitives(frame, bindings):
    """Enter each of the (name, function) bindings in BINDINGS into FRAME,
    an environment frame."""
    for names, func in bindings:
        if type(names) is str:
            names = (names,)
        for name in names:
            frame.define(Symbol.string_to_symbol(name),
                         PrimitiveFunction(func))

def create_global_environment():
    """Initialize the_global_environment to a fresh environment defining the
    predefined names."""
    global the_global_environment

    the_global_environment = EnvironFrame(None)
    
    # Uncomment the following line after you finish with Problem 4.
    scm_load(Symbol.string_to_symbol(SCHEME_PRELUDE_FILE))
    define_primitives(the_global_environment, _PRIMITIVES)

input_port = None

@main
def run(*argv):
    global input_port

    if argv:
        try:
            input_file = open(argv[0])
        except IOError as exc:
            print("could not open {0}: {1}".format(argv[0], exc.args[0]),
                  file=sys.stderr)
            sys.exit(1)
    else:
        input_file = sys.stdin
    #Jack 04:30PM.14.April.2012
    #interact()    
    input_port = Buffer(tokenize_lines(input_file))
    create_global_environment()
    read_eval_print("scm> ")
