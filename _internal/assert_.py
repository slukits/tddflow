# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import Callable


class FatalError(Exception):
    pass


class T(object):
    """
    A T instance t provides means to communicate with the testing
    framework (e.g. t.breakIfNot) and to assert expected behavior (e.g.
    t.truthy).
    """

    def __init__(self, fail: callable, log: Callable[[str], None]):
        self.__fail = fail
        self.__log = log

    def failed(self, log: str):
        """
        failed flags a test as failed with given log message and
        continues it's execution.
        """
        self.__fail()
        if log:
            self.__log(log)

    def truthy(self, value: any, log: str = "") -> bool:
        """
        truthy fails calling test if given value is not truthy and
        returns False; otherwise True is returned
        """
        if value:
            return True
        self.failed(f'expected \'{value}\' to be truthy')
        if len(log):
            self.__log(log)
        return False

    def fatal(self, log: str = ""):
        """
        fatal reports a tests as failed with given log message and stops
        it's execution immediately.
        """
        if len(log):
            self.failed(log)
        raise FatalError()

    def fatal_if_not(self, b: bool, log: str = ""):
        """
        fatal_if_not stops test execution if given bool b is not truthy
        """
        if b:
            return
        self.fatal(log)

    def log(self, s: str): self.__log(s)
