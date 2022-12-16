# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

# pyunit fixtures contains test suites used as fixtures for test.

from testing import T
import testmocks as mck


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
