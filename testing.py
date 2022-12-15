# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

class FatalError(Exception):
    pass


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

    def failed(self, log: str):
        self.__failed(log)

    def fatal(self, log: str = ""):
        self.failed(log)
        raise FatalError()

    def fatal_if_not(self, b: bool):
        if b:
            return
        # don't call fatal to not report test as failed
        raise FatalError()
