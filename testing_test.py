# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from testing import T

import testfixtures as fx
import testmocks as mck
import exec


class t:

    def fails_a_test_on_request(self, t: T):
        suite = fx.FailTest()
        exec.run_tests(suite, exec.Config(out=suite.reportIO))
        t.truthy("failed_test" in suite.reportIO.getvalue())

    def stops_and_fails_a_test_on_request(self, t: T):
        suite = fx.FatalTest()
        exec.run_tests(suite, exec.Config(out=suite.reportIO))
        t.truthy(not suite.changed_after_fatal)


if __name__ == '__main__':
    exec.run_tests(t)
