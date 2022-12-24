# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""
tddflow is a lightweight testing framework for a TDD workflow.  It has
also the capability to watch a python package and it's sub-packages for
modifications automatically rerunning tests of a modified test-module or
of test modules importing a modified production module.

Usage for watching:

    python -m tddflow

See

    python -m tddflow help

for information about its command line arguments.

Usage for testing:

    from tddflow.testing import run, T

    class TestedSubject:

        def init(self, t: T):
            \"""setup fixtures which all tests have in common.\"""
            pass

        def setup(self, t: T):
            \"""setup fixtures for each test individually.\"""
            pass

        def tear_down(self, t: T):
            \"""clear resources obtained by setup.\"""
            pass

        def has_tested_behavior(self, t: T):
            \"""
            implement tests using t for test control flow and
            assertions
            \"""
            t.fatal_if_not(t.truthy(True))

        def finalize(self, t: T):
            \"""clear resources obtained by init\"""
            pass

    if __name__ == '__main__':
        run(TestedSubject)

See also tddflow.testing.Config for how to configure a tests-suite run.

HAPPY TESTING
"""