# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from context import testing

class ASuiteWithCompileError:

    def compile_error(self, t: testing.T):
        t.log('missing brace'

if __name__ == '__main__':
    testing.run(ASuiteWithCompileError)

