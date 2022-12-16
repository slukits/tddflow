# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""
Module suite_test provides the tests for pyunit's behavior.  To use
pyunit in production we need at least three features: A suite runner
executes (1) all test-methods of a test suite, and a failed assertion
fails (2) a test which is then reported (3) as having failed.  To test
these features python's built in doctest feature is used.

A called suite test has been run:

>>> s = TestTestRun()
>>> s.suiteTestHasRun
False
>>> s.suite_test(None)
>>> s.suiteTestHasRun
True

A suite test is executed on a (suite) test run:

>>> from pyunit import run_tests, Config
>>> s = TestTestRun()
>>> s.suiteTestHasRun
False
>>> run_tests(s)
>>> s.suiteTestHasRun
True

A suite test has an Testing instance provided on execution:

>>> s = TestTestingTInstance()
>>> s.gotTestingTInstance
False
>>> run_tests(s)
>>> s.gotTestingTInstance
True

A suite test fails if truthy assertion fails:

>>> s = TestTrueAssertion()
>>> s.failedTrueAssertion
False
>>> s.passedTrueAssertion
False
>>> run_tests(s, Config(out=s.reportIO))
>>> s.failedTrueAssertion
True
>>> s.passedTrueAssertion
False

A failing suite test is reported:

>>> 'TrueAssertion' in s.reportIO.getvalue()
True
>>> 'fails_if_false' in s.reportIO.getvalue()
True
>>> 'passes_if_true' in s.reportIO.getvalue()
False
>>> s.reportIO.close()

Now we have a minimal implementation of a testing framework which can be
used for further tests of pyunit.
"""

import io

from testing import T
from pyunit_mocks import Out
import pyunit_fixtures as fx
import pyunit


class TestTestRun:

    def __init__(self):
        super().__init__()
        self.suiteTestHasRun = False

    def suite_test(self, a): self.suiteTestHasRun = True


class TestTestingTInstance:

    def __init__(self):
        super().__init__()
        self.gotTestingTInstance = False

    def got_testing_T_instance(self, t: T):
        self.gotTestingTInstance = isinstance(t, T)


class TestTrueAssertion:

    def __init__(self):
        self.reportIO = Out(self._io_callback)
        self.failedTrueAssertion = False
        self.passedTrueAssertion = False

    def _io_callback(self, s: str):
        if 'fails_if_false' in s:
            self.failedTrueAssertion = True
        if 'passes_if_true' in s:
            self.passedTrueAssertion = True

    def fails_if_false(self, t: T):
        t.truthy(False)

    def passes_if_true(self, t: T):
        t.truthy(True)


class Runner:

    def executes_given_single_test(self, t: T):
        suite = fx.RunSingle()
        pyunit.run_tests(suite, pyunit.Config(
            out=suite.reportIO, single='single_test'))
        t.truthy(suite.single_executed)
        t.truthy(not suite.other_executed)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    pyunit.run_tests(Runner)
