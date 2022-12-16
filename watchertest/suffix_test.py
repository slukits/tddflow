# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from context import testing


class SuffixSuite:

    def a_passing_suffix_test(self, t: testing.T):
        t.log("report this test")

    def a_failing_suffix_test(self, t: testing.T):
        t.truthy(False)


if __name__ == '__main__':
    testing.run(SuffixSuite)
