# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import NamedTuple, List, TextIO
from dataclasses import dataclass
import sys

SPECIAL = {}
"""SPECIAL holds all names of test suite methods considered special."""


@dataclass
class Config:
    """configuration for test-runs"""
    out: TextIO = sys.stderr


def runTests(suite: any, config: Config = None):
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
    config, report = config or Config(), Report()

    tt = [t for t in dir(s)
          if callable(getattr(s, t, None))
          and t not in SPECIAL
          and not t.startswith('_')
          ]
    for t in tt:
        getattr(s, t)(T(
            lambda failed: report.appendTest(t, failed)
        ))
    report.tests(s.__class__.__name__, config.out)


class T(object):
    """
    A T instance t provides means to communicate with the testing
    framework (e.g. t.breakIfNot) and to assert expected behavior (e.g.
    t.truthy).
    """

    def __init__(self, failed: callable):
        self.__failed = failed

    def truthy(self, value) -> bool:
        if value:
            return True
        self.__failed(True)


class Test(NamedTuple):
    name: str
    failed: bool


class Report(object):
    """
    A Report is used by a Suite instance to generate the desired output
    about a test run.
    """

    def __init__(self):
        self._tt = []  # type: List[Test]
        self._fails = 0

    def appendTest(self, name: str, failed: bool):
        if failed:
            self._fails += 1
        self._tt.append(Test(name, failed))

    def tests(self, suite: str, out: TextIO):
        if len(self._tt) == 0:
            return
        print("{} ({}/{})".format(
            suite, len(self._tt), self._fails), file=out)
        for t in self._tt:
            print("  {}".format(t.name), file=out)
