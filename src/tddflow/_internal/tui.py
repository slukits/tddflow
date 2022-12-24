# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import TextIO, Any, Iterable, NamedTuple

import os
import sys
import json
import time

from pathlib import Path
from queue import Queue
from threading import Thread

about = """
Copyright (c) 2022 Stephan Lukits.  All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import atexit
    from select import select


def non_blocking_kb(q: Queue):
    while True:
        if os.name == 'nt' and msvcrt.kbhit():
            q.put(msvcrt.getch().decode('utf-8'))
            continue
        dr, _, _ = select([sys.stdin], [], [], 0)
        if dr != []:
            q.put(sys.stdin.read(1))
        time.sleep(0.2)


from tddflow._internal.reporting import (
    JSN_TESTS_COUNT, JSN_FAILS_COUNT, JSN_TEST_SUITE, JSN_FAILS,
    JSN_TEST_LOGS)


BLACK_FG = "\033[30m"
RED_BG = "\033[41m"
GREEN_BG = "\033[42m"
WHITE_FG = "\033[37m"
RESET = "\033[0m"
RESET_COLORS = "\033[39;49m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


class Args(NamedTuple):
    frq: float
    tm_out: float
    mappings: dict[Path, Path]
    ignore_pkg: list[str]
    ignore_mdl: list[str]


class TUI:
    """
    TUI is an abstraction for the terminal output to provide for the
    watcher an api to report test runs.  It allows to replace the
    default test-io for testing and to add/exchange tui-libraries if
    needed.  TUI also provides a non-blocking keyboard input at the
    Queue self.inp, e.g.:
        try:
            char = self.inp.get()
        except Empty:
            pass
    """

    def __init__(self, out: TextIO = sys.stdout, inp: Queue|None=None):
        self._out = out
        self.inp = Queue()
        if self._out.isatty():
            self._out.write(HIDE_CURSOR)
            if os.name != 'nt':
                self.fd = sys.stdin.fileno()
                self.new_term = termios.tcgetattr(self.fd)
                self.old_term = termios.tcgetattr(self.fd)
                self.new_term[3] = (
                    self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
                termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
                atexit.register(lambda: termios.tcsetattr(
                    self.fd, termios.TCSAFLUSH, self.old_term))
            self.kb = Thread(target=non_blocking_kb, args=(self.inp,), daemon=True)
            self.kb.start()

    def restore(self):
        if self._out.isatty():
            self._out.write(SHOW_CURSOR)
            if os.name != 'nt':
                termios.tcsetattr(
                    self.fd, termios.TCSAFLUSH, self.old_term)

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

    def print_summary(
        self, ss: list[str], elapsed: float, failed: bool = False
    ) -> list[Any]:
        """
        print_summary parses give json suit-test-runs outputs ss and
        writes the run's summary of executed and failed tests.  Parsed
        objects are returned.
        """
        self.clear()
        parsed = []  # type: list[Any]
        tests_count, fails_count = 0, 0
        if len(ss):
            for s in ss:
                try:
                    jsn = json.loads(s)
                except json.JSONDecodeError as e:
                    tests_count += 1
                    fails_count += 1
                    parsed.append({
                        JSN_TEST_SUITE: 'internal error',
                        JSN_FAILS: ['json_decoding_error'],
                        JSN_TEST_LOGS: {'json_decoding_error': [
                            str(e), s]},
                        JSN_TESTS_COUNT: 0,
                        JSN_FAILS_COUNT: 1
                    })
                else:
                    tests_count += jsn[JSN_TESTS_COUNT]
                    fails_count += jsn[JSN_FAILS_COUNT]
                    parsed.append(jsn)
            
        summary = (f'tddflow: watcher: run {tests_count} tests of ' +
                   f'witch {fails_count} failed in {elapsed}s')
        if fails_count or failed:
            self.write_line(self.failed(summary))
        else:
            self.write_line(self.passed(summary))
        return parsed

    def print_args(self, args: Args):
        self.write_line(f'analysis frequency: {args.frq}s, ' +
            f'test-run timeout: {args.tm_out}s')
        self.write_line('ignored packages:')
        self.write_line('    '+'\n    '.join(args.ignore_pkg))
        self.write_line('ignored modules:')
        self.write_line('    '+'\n    '.join(args.ignore_mdl))
        if not len(args.mappings):
            self.write_line()
            return
        self.write_line('production-test mappings:')
        self.write_line('    '+'\n    '.join(
            f'{p}->{t}' for p, t in args.mappings.items()))
        self.write_line()

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
                for LL in ll:
                    first = True
                    for L in LL.split("\n"):
                        if first:
                            first = False
                            self.write_line(f'{L}', 8)
                            continue
                        self.write_line(f'{L}', 10)

    def about(self):
        self.clear()
        self._out.write(about[1:])

    def print_buttons(self):
        self.write_line()
        self._out.write('[r]un all test modules   [a]bout   [q]uit')
        self._out.flush()

