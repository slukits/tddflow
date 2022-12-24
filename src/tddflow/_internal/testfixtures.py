# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

# tddflow fixtures contains test suites used as fixtures for test.

import testmocks as mck
from testcontext import testing
from assert_ import T


class ReportMockSuite:

    def __init__(self):
        self.reportIO = mck.Out()


class TDDReport(ReportMockSuite):
    """test suite for TDD-cycle reporting"""

    def passing_test(self, _: T):
        pass

    def failing_test(self, t: T):
        t.truthy(False)

    def logging_test(self, t: T):
        t.log("42")


class RunSingle(ReportMockSuite):
    """tests single test execution"""

    def __init__(self):
        super().__init__()
        self.single_executed = False
        self.other_executed = False

    def single_test(self, _: T):
        self.single_executed = True

    def other_executed(self, _: T):
        self.other_executed = True


class LoggingTest(ReportMockSuite):
    """test suit for testing a logging test"""

    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def logging_test(self, t: T): t.log(self.msg)


class FailTest(ReportMockSuite):
    """test suit for testing failing a test"""

    def failed_test(self, t: T):
        t.failed("test has failed")


class FatalTest(ReportMockSuite):
    """suit testing failing and stopping of test execution"""

    def __init__(self):
        super().__init__()
        self.changed_after_fatal = False

    def fatal_test(self, t: T):
        t.fatal("test run is stopped and has failed")
        self.changed_after_fatal = True

    def fatal_if_not_test(self, t: T):
        t.fatal_if_not(False)
        self.changed_after_fatal = True

SPC_INIT = 'init'
SPC_SETUP = 'setup'
SPC_TEAR_DOWN = 'tear_down'
SPC_ONE = 'test one'
SPC_TWO = 'test two'
SPC_FINALIZE = 'finalize'


class SpecialMethods(ReportMockSuite):
    """
    SpecialMethods logs the calls of special methods to test if they are
    executed by the test runner in the right order.
    """

    def init(self, t: T): t.log(SPC_INIT)

    def setup(self, t: T): t.log(SPC_SETUP)

    def tear_down(self, t: T): t.log(SPC_TEAR_DOWN)

    def test_one(self, t: T): t.log(SPC_ONE)

    def test_two(self, t: T): t.log(SPC_TWO)

    def finalize(self, t: T): t.log(SPC_FINALIZE)


SPC_INIT_FAILED = 'init failed'


class SpecialInitFails(ReportMockSuite):
    """
    SpecialInitFails is to test if no other suite method is executed if
    init fails.
    """

    def init(self, _: T): raise Exception(SPC_INIT_FAILED)

    def setup(self, t: T): t.log(SPC_SETUP)

    def tear_down(self, t: T): t.log(SPC_TEAR_DOWN)

    def test_one(self, t: T): t.log(SPC_ONE)

    def finalize(self, t: T): t.log(SPC_FINALIZE)


SPC_SETUP_FAILED = 'setup exception'


class SpecialSetupFails(ReportMockSuite):
    """
    SpecialSetupFails is to test if the test run is omitted if its setup
    fails while tear_down is still executed.
    """

    def init(self, t: T): t.log(SPC_INIT)

    def setup(self, t: T): raise Exception(SPC_SETUP_FAILED)

    def tear_down(self, t: T): t.log(SPC_TEAR_DOWN)

    def test_one(self, t: T): t.log(SPC_ONE)

    def finalize(self, t: T): t.log(SPC_FINALIZE)


SPC_TEAR_DOWN_FAILED = 'tear down exception'


class SpecialTearDownFails(ReportMockSuite):
    """
    SpecialTearDownFails is to test if failing tear down is reported.
    """

    def tear_down(self, t: T): raise Exception(SPC_TEAR_DOWN_FAILED)

    def test_one(self, t: T): pass


SPC_FINALIZE_FAILED = 'finalize exception'


class SpecialFinalizeFails(ReportMockSuite):
    """
    SpecialFinalizeFails is to test if failing finalize is reported.
    """

    def finalize(self, t: T): raise Exception(SPC_FINALIZE_FAILED)


class FailingTestFileLine(ReportMockSuite):
    """
    FailingTestFileLine tests if the fail message of a failing assertion
    provides the file and line number of the failing test assertion.
    """

    def failing_test(self, t: T):
        t.truthy(False)