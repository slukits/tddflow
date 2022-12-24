# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

# NOTE: In this test module we use testing.run to execute test
# test-suites to evaluate assertions.  If this test-module is executed
# by the watcher it will set the --report=tdd flag at the test
# execution, i.e. run will choose by default the TDD-Report which
# produces json-output.  If we want to assert tested assertion output
# against the simpler Default-Report it must be explicitly set in the
# test's run-configuration, e.g.
#
#     def raises_logs_given_message(self, t: T):
#         def raises_logs(self, t: T) -> None:
#             def dont_raise(): pass
#             t.raises(dont_raise, Exception, "42")
#         suite = fx.ReportMockSuite()
#         suite.raises_logs = MethodType(raises_logs, suite)
#         testing.run(suite, testing.Config(
#             out=suite.reportIO, reporter=reporting.Default()))
#                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#         t.truthy("42" in suite.reportIO.getvalue())


from types import MethodType
import testfixtures as fx
from testcontext import testing
from assert_ import T
from reporting import Default


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

    def _config_dflt(self, suite: object) -> testing.Config:
        return testing.Config(out=suite.reportIO, reporter=Default())

    def raises_logs_given_message(self, t: T):
        def raises_logs(self, t: T) -> None:
            def dont_raise(): pass
            t.raises(dont_raise, Exception, "42")
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(raises_logs, suite)
        testing.run(suite, self._config_dflt(suite))
        t.truthy("42" in suite.reportIO.getvalue())

    def falsy_fails_test_if_given_value_is_truthy(self, t: T):
        def falsy_fails_if_given_truthy(self, t: T) -> None:
            if not t.falsy(True, 'falsy failed'):
                self.falsy_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(falsy_fails_if_given_truthy, suite)
        testing.run(suite, self._config_dflt(suite))
        t.truthy("expected 'True' to be falsy" in suite.reportIO.getvalue())
        t.truthy('falsy failed' in suite.reportIO.getvalue())
        t.truthy(suite.falsy_failed)

    def in_fails_if_given_value_is_not_in_given_iterable(self, t: T):
        def in_fails_if_value_not_in_iterable(self, t: T) -> None:
            if not t.in_(42, [], 'in failed'):
                self.in_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            in_fails_if_value_not_in_iterable, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' in '[]'", suite.reportIO.getvalue())
        t.in_('in failed', suite.reportIO.getvalue())
        t.truthy(suite.in_failed)

    def in_passes_if_given_value_in_given_iterable(self, t: T):
        def in_passes_if_value_in_iterable(self, t: T) -> None:
            if t.in_(42, [42]):
                self.in_failed = False
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(in_passes_if_value_in_iterable, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.in_failed)

    def not_in_fails_if_given_value_in_given_iterable(self, t: T):
        def not_in_fails_if_value_in_iterable(self, t: T) -> None:
            if not t.not_in(42, [42], 'not in failed'):
                self.not_in_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            not_in_fails_if_value_in_iterable, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' not in '[42]'", suite.reportIO.getvalue())
        t.in_('not in failed', suite.reportIO.getvalue())
        t.truthy(suite.not_in_failed)

    def not_in_passes_if_given_value_not_in_given_iterable(self, t: T):
        def not_in_passes_if_value_in_iterable(self, t: T) -> None:
            if t.not_in(42, []):
                self.not_in_failed = False
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            not_in_passes_if_value_in_iterable, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.not_in_failed)

    def is_fails_if_given_arguments_are_not_identical(self, t: T):
        def is_fails_if_args_have_not_same_id(self, t: T) -> None:
            if not t.is_(42, 22, 'is failed'):
                self.is_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            is_fails_if_args_have_not_same_id, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is '22'", suite.reportIO.getvalue())
        t.in_('is failed', suite.reportIO.getvalue())
        t.truthy(suite.is_failed)

    def is_passes_if_given_arguments_are_identical(self, t: T):
        def is_passes_if_args_identical(self, t: T) -> None:
            if t.is_(42, 42):
                self.is_failed = False
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(is_passes_if_args_identical, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.is_failed)

    def is_not_fails_if_given_arguments_identical(self, t: T):
        def is_not_fails_if_args_identical(self, t: T) -> None:
            if not t.is_not(42, 42, 'is not failed'):
                self.is_not_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            is_not_fails_if_args_identical, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is not '42'", suite.reportIO.getvalue())
        t.in_('is not failed', suite.reportIO.getvalue())
        t.truthy(suite.is_not_failed)

    def is_not_passes_if_given_arguments_are_not_identical(self, t: T):
        def is_not_passes_if_args_not_identical(self, t: T) -> None:
            if t.is_not(42, 22):
                self.is_not_failed = False
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            is_not_passes_if_args_not_identical, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.is_not_failed)

    def is_instance_fails_if_given_arg_is_no_instance_of_type(self, t: T):
        def is_instance_fails_if_arg_not_instance_of_type(self, t: T) -> None:
            if not t.is_instance(42, str, 'is instance failed'):
                self.is_instance_failed = True
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            is_instance_fails_if_arg_not_instance_of_type, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is instance of '<class 'str'>'", suite.reportIO.getvalue())
        t.in_('is instance failed', suite.reportIO.getvalue())
        t.truthy(suite.is_instance_failed)

    def is_instance_passes_if_given_arg_is_instance_of_type(self, t: T):
        def is_instance_passes_if_arg_instance_of_type(self, t: T) -> None:
            if t.is_instance(42, int):
                self.is_instance_failed = False
        suite = fx.ReportMockSuite()
        suite.raises_logs = MethodType(
            is_instance_passes_if_arg_instance_of_type, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.is_instance_failed)

    def is_not_instance_fails_if_given_arg_is_instance_of_type(self, t: T):
        def is_not_instance_fails_if_arg_instance_of_type(self, t: T) -> None:
            if not t.is_not_instance(42, int, 'is not instance failed'):
                self.is_not_instance_failed = True
        suite = fx.ReportMockSuite()
        suite.is_not_instance_fails = MethodType(
            is_not_instance_fails_if_arg_instance_of_type, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is not instance of '<class 'int'>'", 
            suite.reportIO.getvalue())
        t.in_('is not instance failed', suite.reportIO.getvalue())
        t.truthy(suite.is_not_instance_failed)

    def is_not_instance_passes_if_given_arg_is_not_instance_of_type(self, t: T):
        def is_not_instance_passes_if_arg_not_instance_of_type(self, t: T) -> None:
            if t.is_not_instance(42, str):
                self.is_not_instance_failed = False
        suite = fx.ReportMockSuite()
        suite.is_not_instance_passes = MethodType(
            is_not_instance_passes_if_arg_not_instance_of_type, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.is_not_instance_failed)

    def eq_fails_if_given_arg_does_not_equal_other(self, t: T):
        def eq_fails_if_arg_not_equals_other(self, t: T) -> None:
            if not t.eq(42, 22, 'equals failed'):
                self.eq_failed = True
        suite = fx.ReportMockSuite()
        suite.equals_fails = MethodType(
            eq_fails_if_arg_not_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' == '22'", suite.reportIO.getvalue())
        t.in_('equals failed', suite.reportIO.getvalue())
        t.truthy(suite.eq_failed)

    def is_eq_passes_if_given_arg_equals_other(self, t: T):
        def eq_passes_if_arg_equals_other(self, t: T) -> None:
            if t.eq(42, 42):
                self.eq_failed = False
        suite = fx.ReportMockSuite()
        suite.equals_passes = MethodType(
            eq_passes_if_arg_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.eq_failed)

    def not_eq_fails_if_given_arg_equals_other(self, t: T):
        def not_eq_fails_if_arg_equals_other(self, t: T) -> None:
            if not t.not_eq(42, 42, 'not equals failed'):
                self.not_eq_failed = True
        suite = fx.ReportMockSuite()
        suite.not_equals_fails = MethodType(
            not_eq_fails_if_arg_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' != '42'", suite.reportIO.getvalue())
        t.in_('not equals failed', suite.reportIO.getvalue())
        t.truthy(suite.not_eq_failed)

    def not_is_eq_passes_if_given_arg_equals_other(self, t: T):
        def not_eq_passes_if_arg_not_equals_other(self, t: T) -> None:
            if t.not_eq(42, 22):
                self.not_eq_failed = False
        suite = fx.ReportMockSuite()
        suite.not_equals_passes = MethodType(
            not_eq_passes_if_arg_not_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.not_eq_failed)

    def eq_str_fails_if_given_arg_str_repr_not_equals_other(self, t: T):
        def eq_str_fails_if_arg_str_repr_not_equals_other(self, t: T) -> None:
            if not t.eq_str(42, 22, 'not equals str repr failed'):
                self.eq_str_failed = True
        suite = fx.ReportMockSuite()
        suite.equals_str_fails = MethodType(
            eq_str_fails_if_arg_str_repr_not_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' == '22'", suite.reportIO.getvalue())
        t.in_('not equals str repr failed', suite.reportIO.getvalue())
        t.truthy(suite.eq_str_failed)

    def eq_str_passes_if_given_arg_str_repr_equals_other(self, t: T):
        def eq_str_passes_if_arg_str_repr__equals_other(self, t: T) -> None:
            if t.eq_str(42, 42):
                self.eq_str_failed = False
        suite = fx.ReportMockSuite()
        suite.not_equals_passes = MethodType(
            eq_str_passes_if_arg_str_repr__equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.eq_str_failed)

    def eq_repr_fails_if_given_arg_cnn_repr_not_equals_other(self, t: T):
        def eq_repr_fails_if_arg_cnn_repr_not_equals_other(self, t: T) -> None:
            if not t.eq_repr(42, 22, 'not equals canonical repr failed'):
                self.eq_repr_failed = True
        suite = fx.ReportMockSuite()
        suite.equals_repr_fails = MethodType(
            eq_repr_fails_if_arg_cnn_repr_not_equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' == '22'", suite.reportIO.getvalue())
        t.in_('not equals canonical repr failed', suite.reportIO.getvalue())
        t.truthy(suite.eq_repr_failed)

    def eq_repr_passes_if_given_arg_cnn_repr_equals_other(self, t: T):
        def eq_repr_passes_if_arg_cnn_repr__equals_other(self, t: T) -> None:
            if t.eq_str(42, 42):
                self.eq_repr_failed = False
        suite = fx.ReportMockSuite()
        suite.equals_repr_passes = MethodType(
            eq_repr_passes_if_arg_cnn_repr__equals_other, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.eq_repr_failed)

    def matched_fails_if_given_str_is_not_matched_by_regex(self, t: T):
        def matched_fails_if_str_not_matched_by_regex(self, t: T) -> None:
            if not t.matched('42', '22', 0, 'not matched'):
                self.matched_failed = True
        suite = fx.ReportMockSuite()
        suite.matched_fails = MethodType(
            matched_fails_if_str_not_matched_by_regex, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is matched by '22'", suite.reportIO.getvalue())
        t.in_('not matched', suite.reportIO.getvalue())
        t.truthy(suite.matched_failed)

    def matched_passes_if_given_str_is_matched_by_regex(self, t: T):
        def matched_passes_if_str_matched_by_regex(self, t: T) -> None:
            if t.matched('42', '42'):
                self.matched_failed = False
        suite = fx.ReportMockSuite()
        suite.matched_passes = MethodType(
            matched_passes_if_str_matched_by_regex, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.matched_failed)

    def space_matched_fails_if_given_str_is_not_matched_by_pattern(self, t: T):
        matched_str_fx = """<td>\n    .*42.*\n</td>"""
        def space_matched_fails_if_str_not_matched_by_ss(self, t: T) -> None:
            if  not t.space_matched(matched_str_fx, '<td>', '.*42', '</td>', 
                    log='not space matched'):
                self.space_matched_failed = True
        suite = fx.ReportMockSuite()
        suite.space_matched_fails = MethodType(
            space_matched_fails_if_str_not_matched_by_ss, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("is space-matched by", suite.reportIO.getvalue())
        t.in_('not space matched', suite.reportIO.getvalue())
        t.truthy(suite.space_matched_failed)

    def space_matched_passes_if_given_str_is_matched_by_pattern(self, t: T):
        matched_str_fx = """<td>\n    .*42.*\n</td>"""
        def space_matched_passes_if_str_not_matched_by_ss(self, t: T) -> None:
            if  t.space_matched(matched_str_fx, '<td>', '.*42.*', '</td>'):
                self.space_matched_failed = False
        suite = fx.ReportMockSuite()
        suite.space_matched_fails = MethodType(
            space_matched_passes_if_str_not_matched_by_ss, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.space_matched_failed)

    def star_matched_fails_if_given_str_is_not_matched_by_pattern(self, t: T):
        matched_str_fx = """<td>\n    .*42.*\n</td>"""
        def star_matched_fails_if_str_not_matched_by_ss(self, t: T) -> None:
            if  not t.star_matched(matched_str_fx, 'td', '.*22.*', 'td', 
                    log='not star matched'):
                self.star_matched_failed = True
        suite = fx.ReportMockSuite()
        suite.star_matched_fails = MethodType(
            star_matched_fails_if_str_not_matched_by_ss, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("is star-matched by", suite.reportIO.getvalue())
        t.in_('not star matched', suite.reportIO.getvalue())
        t.truthy(suite.star_matched_failed)

    def star_matched_passes_if_given_str_is_matched_by_pattern(self, t: T):
        matched_str_fx = """<td>\n    .*42.*\n</td>"""
        def star_matched_passes_if_str_matched_by_pattern(self, t: T) -> None:
            if t.star_matched(matched_str_fx, 'td', '.*42.*', 'td'):
                self.star_matched_failed = False
        suite = fx.ReportMockSuite()
        suite.star_matched_fails = MethodType(
            star_matched_passes_if_str_matched_by_pattern, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.star_matched_failed)

    def not_matched_fails_if_given_str_is_matched_by_regex(self, t: T):
        def not_matched_fails_if_str_matched_by_regex(self, t: T) -> None:
            if not t.not_matched('42', '42', 0, 'matched'):
                self.not_matched_failed = True
        suite = fx.ReportMockSuite()
        suite.matched_fails = MethodType(
            not_matched_fails_if_str_matched_by_regex, suite)
        testing.run(suite, self._config_dflt(suite))
        t.in_("'42' is not matched by '42'", suite.reportIO.getvalue())
        t.in_('matched', suite.reportIO.getvalue())
        t.truthy(suite.not_matched_failed)

    def not_matched_passes_if_given_str_is_not_matched_by_regex(self, t: T):
        def not_matched_passes_if_str_not_matched_by_regex(self, t: T) -> None:
            if t.not_matched('42', '22'):
                self.not_matched_failed = False
        suite = fx.ReportMockSuite()
        suite.matched_passes = MethodType(
            not_matched_passes_if_str_not_matched_by_regex, suite)
        testing.run(suite, self._config_dflt(suite))
        t.falsy(suite.not_matched_failed)


if __name__ == '__main__':
    testing.run(t)
