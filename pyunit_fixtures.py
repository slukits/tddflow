# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

# pyunit fixtures contains test suites used as fixtures for test.

from pyunit import T


class TDDReportJsonFX:

    def passing_test(self, _: T):
        pass

    def failing_test(self, t: T):
        t.truthy(False)
