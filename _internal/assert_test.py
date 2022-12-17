# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from types import MethodType
import testfixtures as fx
from testcontext import testing
from assert_ import T


class t:

    def fails_a_test_on_request(self, t: T):
        suite = fx.FailTest()
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy("failed_test" in suite.reportIO.getvalue())

    def stops_and_fails_a_test_on_request(self, t: T):
        suite = fx.FatalTest()
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy(not suite.changed_after_fatal)

    def passes_raises_if_given_lambda_raises_given_exception(self, t: T):
        def passing_raises(self, t: T) -> None:
            def raise_exception(): raise Exception
            t.fatal_if_not(t.raises(raise_exception, Exception))
            self.raises_passed = True
        suite = fx.ReportMockSuite()
        suite.raises_passed = False
        suite.test_passing_raises = MethodType(passing_raises, suite)
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy(suite.raises_passed)

    def raises_fails_test_if_given_lambda_doesnt_raise(self, t: T):
        def failing_raises(self, t: T) -> None:
            def dont_raise_exception(): pass
            t.fatal_if_not(t.raises(dont_raise_exception, Exception))
            self.raises_passed = True
        suite = fx.ReportMockSuite()
        suite.raises_passed = False
        suite.test_failing_raises = MethodType(failing_raises, suite)
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy(not suite.raises_passed)

    def raises_fails_if_not_given_error_type_is_raised(self, t: T):
        def failing_raises(self, t: T) -> None:
            def raise_wrong_exception(): raise ZeroDivisionError
            t.fatal_if_not(t.raises(raise_wrong_exception, Exception))
            self.raises_passed = True
        suite = fx.ReportMockSuite()
        suite.raises_passed = False
        suite.test_failing_raises = MethodType(failing_raises, suite)
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy(not suite.raises_passed)

    def raises_logs_given_message(self, t: T):
        def raises_logs(self, t: T) -> None:
            def dont_raise(): pass
            t.raises(dont_raise, Exception, "42")
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(raises_logs, suite)
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy("42" in suite.reportIO.getvalue())


if __name__ == '__main__':
    testing.run(t)
