# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import TextIO
from dataclasses import dataclass
from enum import Enum
import sys

from testing import T, FatalError
import reporting


SPECIAL = {}
"""SPECIAL holds all names of test suite methods considered special."""


@dataclass
class Config:
    """configuration for test-runs"""
    reporter: reporting.Report = None
    out: TextIO = sys.stderr
    single: str = ""


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
    s = suite if not isinstance(suite, type) else suite()
    config = config or Config()
    report = config.reporter or reporting.Default()
    def counter(): return None
    try:
        counter = report.increase_test_count
    except AttributeError:
        pass
    if len(config.single):
        _run_single_test(s, report, config, counter)
        return
    tt = _suite_tests(s)
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


def _run_single_test(
    suite: any,
    report: reporting.Report,
    config: Config,
    counter: callable
):
    tt = _suite_tests(suite)
    for t in tt:
        if t != config.single:
            continue
        test = getattr(suite, t)
        try:
            test(T(
                fail=lambda: report.fail(t),
                log=lambda msg: report.log(t, msg)
            ))
            counter()
        except FatalError:
            pass
        break
    report.print(suite.__class__.__name__, config.out)


def _suite_tests(suite) -> list[str]:
    return [t for t in dir(suite)
            if callable(getattr(suite, t, None))
            and t not in SPECIAL
            and not t.startswith('_')
            ]
