# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import TextIO, Any, Iterable

import os
import sys
import json


from pyunit._internal.reporting import (
    JSN_TESTS_COUNT, JSN_FAILS_COUNT, JSN_TEST_SUITE, JSN_FAILS,
    JSN_TEST_LOGS)


BLACK_FG = "\033[30m"
RED_BG = "\033[41m"
GREEN_BG = "\033[42m"
WHITE_FG = "\033[37m"
RESET = "\033[0m"
RESET_COLORS = "\033[39;49m"


class TUI:
    """
    TUI is an abstraction for the terminal output to provide for the
    watcher an api to report test runs.  It allows to replace the
    default test-io for testing and to add/exchange tui-libraries if
    needed.
    """

    def __init__(self, out: TextIO = sys.stdout):
        self._out = out

    def clear(self) -> None:
        """clears the screen os independent."""
        if not self._out.isatty():
            return
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def failed(self, s: str) -> str:
        """failed colors given string s with the error colors."""
        return f'{RED_BG}{WHITE_FG}{s}{RESET_COLORS}'

    def passed(self, s: str) -> str:
        """passed colors given string s passing (i.e. green)."""
        return f'{GREEN_BG}{BLACK_FG}{s}{RESET_COLORS}'

    def write_line(self, s: str = '', indent: int = 0):
        """
        writes given string s to the screen with indent many spaces
        prefixed and a new line suffix.
        """
        self._out.write(f'{" "*indent}{s}\n')

    def print_summary(self, ss: list[str], failed: bool = False) -> list[Any]:
        """
        print_summary parses give json suit-test-runs outputs ss and
        writes the run's summary of executed and failed tests.  Parsed
        objects are returned.
        """
        self.clear()
        parsed = []  # type: list[Any]
        tests_count, fails_count = 0, 0
        if len(ss):
            for jsn in [json.loads(s) for s in ss]:
                tests_count += jsn[JSN_TESTS_COUNT]
                fails_count += jsn[JSN_FAILS_COUNT]
                parsed.append(jsn)
        summary = (f'pyunit: watcher: run {tests_count} tests of ' +
                   f'witch {fails_count} failed')
        if fails_count or failed:
            self.write_line(self.failed(summary))
        else:
            self.write_line(self.passed(summary))
        return parsed

    def print_analysis(
        self, ttm: Iterable[str], ppm: dict[str, Iterable[str]]
    ) -> None:
        self.write_line('Analysis:')
        self.write_line('modified test-modules:', 2)
        for tm in ttm:
            self.write_line(tm, 4)
        self.write_line('modified production-modules:', 2)
        if not len(ppm):
            return
        for pm, tt in ppm.items():
            self.write_line(f'{pm} triggered:', 4)
            for tm in tt:
                self.write_line(f'{tm}', 6)

    def print_failed_modules(self, ee: dict[str, str]) -> None:
        for m, err in ee.items():
            self.write_line()
            self.write_line(self.failed(f'run failed: .{m}'), 4)
            self.write_line(err, 4)

    def print_suites(self, parsed: list[Any]) -> None:
        for suite in parsed:
            if JSN_TEST_LOGS not in suite or not len(suite[JSN_TEST_LOGS]):
                continue
            tests_count = suite[JSN_TESTS_COUNT]
            fails_count = suite[JSN_FAILS_COUNT]
            self.write_line(
                f'{suite[JSN_TEST_SUITE]} ({tests_count}/{fails_count})', 4)
            fails = suite[JSN_FAILS]
            for t, ll in suite[JSN_TEST_LOGS].items():
                if t in fails:
                    self.write_line(self.failed(f'{t}'), 6)
                else:
                    self.write_line(f'{t}', 6)
                for l in ll:
                    self.write_line(f'{l}', 8)
