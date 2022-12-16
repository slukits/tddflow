# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from context import pyunit


class TestsSuffixSuite:

    def a_passing_suffix_test_in_tests(self, t: pyunit.T):
        t.log("report this test")

    def a_failing_suffix_test_in_tests(self, t: pyunit.T):
        t.truthy(False)


if __name__ == '__main__':
    pyunit.run_tests(TestsSuffixSuite)
