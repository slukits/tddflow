# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from context import testing

import tddflow._internal.watchergolden.pm1


class TestsSuffixSuite:

    def a_passing_suffix_test_in_tests(self, t: testing.T):
        t.log("report this test")

    def a_failing_suffix_test_in_tests(self, t: testing.T):
        t.truthy(tddflow._internal.watchergolden.pm1.pm1f())


if __name__ == '__main__':
    testing.run(TestsSuffixSuite)
