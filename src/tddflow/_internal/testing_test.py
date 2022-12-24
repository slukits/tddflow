# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""
Module suite_test provides the tests for tddflow's behavior.  To use
tddflow in production we need at least three features: A suite runner
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

>>> from testcontext import testing
>>> s = TestTestRun()
>>> s.suiteTestHasRun
False
>>> testing.run(s)
>>> s.suiteTestHasRun
True

A suite test has an Testing instance provided on execution:

>>> s = TestTestingTInstance()
>>> s.gotTestingTInstance
False
>>> testing.run(s)
>>> s.gotTestingTInstance
True

A suite test fails if truthy assertion fails:

>>> s = TestTrueAssertion()
>>> s.failedTrueAssertion
False
>>> s.passedTrueAssertion
False
>>> testing.run(s, testing.Config(out=s.reportIO))
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
used for further tests of tddflow.
"""

import os

from testmocks import Out
import testfixtures as fx
from testcontext import testing
from assert_ import T
from reporting import Default


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
        self.gotTestingTInstance = isinstance(t, testing.T)


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
        testing.run(suite, testing.Config(
            out=suite.reportIO, single='single_test'))
        t.truthy(suite.single_executed)
        t.truthy(not suite.other_executed)

    def _config_dflt(self, suite: object) -> testing.Config:
        return testing.Config(out=suite.reportIO, reporter=Default())

    def executes_special_methods_at_the_right_time(self, t: T):
        suite = fx.SpecialMethods()
        testing.run(suite, self._config_dflt(suite))
        t.star_matched(
            suite.reportIO.getvalue(),
            fx.SPC_INIT, fx.SPC_SETUP, fx.SPC_ONE, fx.SPC_TEAR_DOWN,
            fx.SPC_SETUP, fx.SPC_TWO, fx.SPC_TEAR_DOWN, fx.SPC_FINALIZE
        )
    
    def executes_nothing_more_if_init_fails(self, t: T):
        suite = fx.SpecialInitFails()
        testing.run(suite, self._config_dflt(suite))
        got = suite.reportIO.getvalue()
        t.in_(fx.SPC_INIT_FAILED, got)
        t.not_in(fx.SPC_SETUP, got)
        t.not_in(fx.SPC_ONE, got)
        t.not_in(fx.SPC_TEAR_DOWN, got)
        t.not_in(fx.SPC_FINALIZE, got)

    def doesnt_execute_test_but_tear_down_if_setup_failed(self, t: T):
        suite = fx.SpecialSetupFails()
        testing.run(suite, self._config_dflt(suite))
        got = suite.reportIO.getvalue()
        t.in_(fx.SPC_INIT, got)
        t.in_(fx.SPC_SETUP_FAILED, got)
        t.not_in(fx.SPC_ONE, got)
        t.in_(fx.SPC_TEAR_DOWN, got)
        t.in_(fx.SPC_FINALIZE, got)

    def reports_failing_tear_down(self, t: T):
        suite = fx.SpecialTearDownFails()
        testing.run(suite, self._config_dflt(suite))
        got = suite.reportIO.getvalue()
        t.in_(fx.SPC_TEAR_DOWN_FAILED, got)

    def reports_failing_finalize(self, t: T):
        suite = fx.SpecialFinalizeFails()
        testing.run(suite, self._config_dflt(suite))
        got = suite.reportIO.getvalue()
        t.in_(fx.SPC_FINALIZE_FAILED, got)

    def reports_failing_assertion_s_file_and_line_number(self, t: T):
        suite = fx.FailingTestFileLine()
        testing.run(suite, self._config_dflt(suite))
        got = suite.reportIO.getvalue()
        t.in_('Line 178', got)
        file = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'testfixtures.py'))        
        t.in_(file, got)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    testing.run(Runner)