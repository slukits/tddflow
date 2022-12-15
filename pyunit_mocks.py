# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import io


class OutMock(io.StringIO):

    def __init__(self, io_callback: callable):
        super().__init__()
        self.__io_callback = io_callback

    def write(self, s: str) -> int:
        self.__io_callback(s)
        return super().write(s)
