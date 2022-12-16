# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from context import testing


class TestsPrefixSuite:

    def a_passing_prefix_test_tests(self, t: testing.T):
        t.log("report this test")

    def a_failing_prefix_test_in_tests(self, t: testing.T):
        t.truthy(False)


if __name__ == '__main__':
    testing.run(TestsPrefixSuite)
