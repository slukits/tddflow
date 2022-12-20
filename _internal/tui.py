# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import TextIO

import os
import sys

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

    def __init__(self, out: TextIO=sys.stdout):
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