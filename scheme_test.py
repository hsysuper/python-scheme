#!/usr/bin/env python3

"""Unit testing framework for the Logo interpreter.

Usage: python3 scheme_test.py FILE

Interprets FILE as interactive Scheme source code, and compares each line
of printed output from the read-eval-print loop and from any output functions
to an expected output described in a comment.  For example,

(display (+ 2 3))
; expect 5

Differences between printed and expected outputs are printed with line numbers.
"""

import io
import sys
from ucb import main
from scheme import call_with_input_source, create_global_environment, \
                   read_eval_print

def summarize(output, expected_output):
    """Summarize results of running tests."""
    num_failed, num_expected = 0, len(expected_output)
    for (actual, (expected, line_number)) in zip(output, expected_output):
        if expected.startswith("Error"):
            if not actual.startswith("Error"):
                num_failed += 1
                print('test failed at line {0}'.format(line_number))
                print('  expected an error indication')
                print('   printed: {0}'.format(actual))
        elif actual != expected:
            num_failed += 1
            print('test failed at line {0}'.format(line_number))
            print('  expected: {0}'.format(expected))
            print('   printed: {0}'.format(actual))
    print('{0} tested; {1} failed.'.format(num_expected, num_failed))

EXPECT_STRING = '; expect'

@main
def run_tests(src_file = 'tests.scm'):
    """Run a read-eval loop that reads from src_file and collects outputs."""
    expected_output = []
    line_number = 0

    def read_lines(src):
        """Creates a generator that returns the lines of src, filtering out
        '; expect' strings and collecting them into expected_output with their
        line numbers.  The variable line_number gives the number of the last
        line returned for diagnostic purposes."""
        nonlocal line_number
        while True:
            line_number += 1
            line = src.readline()
            if line.lstrip().startswith(EXPECT_STRING):
                expected = line.split(EXPECT_STRING, 1)[1][1:-1]
                expected_output.append((expected, line_number))
                continue
            if not line:
                return
            yield line

    sys.stderr = sys.stdout = io.StringIO() # Collect output to stdout and stderr
    create_global_environment()
    try:
        call_with_input_source(read_lines(open(src_file)),
                               lambda: read_eval_print(""))
    except BaseException as exc:
        sys.stderr = sys.__stderr__
        print("Tests terminated due to unhandled exception "
              "after line {0}:\n>>>".format(line_number),
              file=sys.stderr)
        raise
    output = sys.stdout.getvalue().split('\n')
    sys.stdout = sys.__stdout__  # Revert stdout
    summarize(output, expected_output)
