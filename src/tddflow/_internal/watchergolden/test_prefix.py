# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


from context import testing
from pm1 import pm1f


class PrefixSuite:

    def a_passing_prefix_test(self, t: testing.T):
        t.log("report this test")

    def a_failing_prefix_test(self, t: testing.T):
        t.truthy(pm1f())


if __name__ == '__main__':
    testing.run(PrefixSuite)
