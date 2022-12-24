# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import os  # should be ignore for production dependencies
_ = os

from context import testing
from pm1 import pm1f
import pm2 as pm


class SuffixSuite:

    def a_passing_suffix_test(self, t: testing.T):
        t.truthy(pm.pm2f())
        t.log("report this test")

    def a_failing_suffix_test(self, t: testing.T):
        t.truthy(pm1f())


if __name__ == '__main__':
    testing.run(SuffixSuite)
