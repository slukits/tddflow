# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import TextIO
import json

import exec
import testfixtures as fx
from reporting import (TDD, JSN_TESTS_COUNT, JSN_FAILS_COUNT, JSN_FAILS,
                       JSN_TEST_LOGS, JSN_TEST_SUITE)

from testing import T


class DefaultReport:

    def reports_a_test_s_log_message(self, t: T):
        exp = "42"
        suite = fx.LoggingTest(exp)
        exec.run_tests(suite, exec.Config(out=suite.reportIO))
        t.truthy(exp in suite.reportIO.getvalue())


class TDDReport:

    def _config(self, reportIO: TextIO) -> exec.Config:
        """_config returns a tests-run configuration for TDD-cycle reporting"""
        return exec.Config(out=reportIO, reporter=TDD())

    def is_provided_as_json(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        try:
            json.loads(suite.reportIO.getvalue())
        except json.JSONDecodeError:
            t.failed("report couldn't be json-decoded")

    def provides_the_suite_name(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_TEST_SUITE in report),
                       f"missing '{JSN_TEST_SUITE}' property")
        t.truthy('TDDReport', report[JSN_TEST_SUITE])

    def provides_the_number_of_ran_tests(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_TESTS_COUNT in report))
        t.truthy(3 == report[JSN_TESTS_COUNT])

    def provides_the_number_of_failed_tests(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_FAILS_COUNT in report))
        t.truthy(1 == report[JSN_FAILS_COUNT])

    def provides_the_failed_tests_names(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_FAILS in report))
        t.truthy(['failing_test'] == report[JSN_FAILS])

    def provides_failed_tests_logs(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_TEST_LOGS in report))
        t.truthy(report[JSN_TEST_LOGS]['failing_test']
                 == ["expected 'False' to be truthy"])

    def provides_a_logging_test_s_log_message(self, t: T):
        suite = fx.TDDReport()
        exec.run_tests(suite, self._config(suite.reportIO))
        report = json.loads(suite.reportIO.getvalue())
        t.fatal_if_not(t.truthy(JSN_TEST_LOGS in report))
        t.truthy(report[JSN_TEST_LOGS]['logging_test'] == ["42"])


if __name__ == '__main__':
    exec.run_tests(DefaultReport)
    exec.run_tests(TDDReport)
