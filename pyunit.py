# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import NamedTuple, List, TextIO
from dataclasses import dataclass
from enum import Enum
import sys

from testing import T, FatalError
import reporting


class ReportType(Enum):
    Default = 0
    TDD = 1


SPECIAL = {}
"""SPECIAL holds all names of test suite methods considered special."""


@dataclass
class Config:
    """configuration for test-runs"""
    reporter: reporting.Report = None
    out: TextIO = sys.stderr


def run_tests(suite: any, config: Config = None):
    """
    run executes *every* callable c (i.e also static or class methods) of
    given suite iff c is non-special and non-dunder.  Each call gets a T
    instance for controlling the test-flow and assertions.

        class TestedSubject():

            def expected_behavior(self, t: pyunit.T):
                t.breakIfNot(t.truthy(True))


        if __name__ == '__main__':
            pyunit.run(TestedSubject)
    """

    s = None
    try:
        s = suite()
    except TypeError:
        s = suite
    config = config or Config()
    report = config.reporter or reporting.Default()
    def counter(): return None
    try:
        counter = report.increase_test_count
    except AttributeError:
        pass

    tt = [t for t in dir(s)
          if callable(getattr(s, t, None))
          and t not in SPECIAL
          and not t.startswith('_')
          ]
    for t in tt:
        test = getattr(s, t)
        try:
            test(T(
                fail=lambda: report.fail(t),
                log=lambda msg: report.log(t, msg)
            ))
            counter()
        except FatalError:
            pass
    report.print(s.__class__.__name__, config.out)
