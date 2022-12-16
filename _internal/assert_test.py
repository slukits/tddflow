# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import testfixtures as fx
from testcontext import testing


class t:

    def fails_a_test_on_request(self, t: testing.T):
        suite = fx.FailTest()
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy("failed_test" in suite.reportIO.getvalue())

    def stops_and_fails_a_test_on_request(self, t: testing.T):
        suite = fx.FatalTest()
        testing.run(suite, testing.Config(out=suite.reportIO))
        t.truthy(not suite.changed_after_fatal)


if __name__ == '__main__':
    testing.run(t)
