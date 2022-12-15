# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import NamedTuple, List, TextIO


class Test(NamedTuple):
    name: str
    failed: bool


class Report:
    def __init__(self):
        self._tt = []  # type: List[Test]
        self._fails = 0

    def appendTest(self, name: str, failed: bool):
        if failed:
            self._fails += 1
        self._tt.append(Test(name, failed))

    def print(self, suite: str, out: TextIO):
        raise NotImplementedError(
            "pyunit: report: print not implemented")


class Default(Report):
    """
    A Report is used by a Suite instance to generate the desired output
    about a test run.
    """

    def print(self, suite: str, out: TextIO):
        if len(self._tt) == 0:
            return
        print("pyunit: failed suite-tests:", file=out)
        print("{} ({}/{})".format(
            suite, len(self._tt), self._fails), file=out)
        for t in self._tt:
            print("  {}".format(t.name), file=out)


class TDD(Report):
    pass
