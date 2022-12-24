# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from typing import Callable, Any, Type, Optional, Iterable
from inspect import getframeinfo, stack
import re


class FatalError(Exception):
    pass


class T(object):
    """
    A T instance t provides means to communicate with the testing
    framework (e.g. t.fatal_if_not) and to assert expected behavior (e.g.
    t.truthy).
    """

    def __init__(self, fail: Callable, log: Callable[[Any], None]) -> None:
        self.__fail = fail
        self.__log = log

    def failed(self, log: Any, caller: int = 2):
        """
        failed flags a test as failed with given log message and
        continues it's execution.
        """
        self.__fail()
        cllr = getframeinfo(stack()[caller][0])
        self.__log(f'File "{cllr.filename}", Line {cllr.lineno}')
        if log:
            self.__log(log)

    def truthy(self, value: Any, log: str = '') -> bool:
        """
        truthy fails calling test if given value is not truthy and
        returns False; otherwise True is returned
        """
        if value:
            return True
        self.failed(f"expected '{value}' to be truthy")
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

    def raises(
        self, c: Callable, ErrType: Type,
        msg: Optional[str] = None
    ) -> bool:
        try:
            c()
        except Exception as e:
            if type(e) is ErrType:
                return True
            self.failed(f"callable raised {type(e)} instead of {ErrType}")
        else:
            self.failed(f"callable didn't raise {ErrType}")
        if msg:
            self.__log(msg)
        return False

    def log(self, s: Any): 
        self.__log(s)

    def falsy(self, value: bool, log: str = '') -> bool: 
        """
        falsy fails calling test, logs log and returns False if given
        value is not falsy; otherwise True is returned.
        """
        if not value:
            return True
        self.failed(f"expected '{value}' to be falsy")
        if len(log):
            self.__log(log)
        return False

    def _fail_cmp(self, v1: Any, v2: Any, msg: str, log: str) -> None:
        """_fail_cmp fails the comparison of two values."""
        sv1, sv2 = repr(v1).strip('"\''), repr(v2).strip('"\'')
        self.failed(f"expected '{sv1}' {msg} '{sv2}'", 3)
        if len(log):
            self.__log(log)

    def in_(self, value: Any, itr: Iterable[Any], log: str = '') -> bool:
        """
        in_ fails calling test, logs log and returns False if given
        value is not in given iterable itr; otherwise True is returned.
        """
        if value in itr:
            return True
        self._fail_cmp(value, itr, 'in', log)
        return False

    def not_in(self, value: Any, itr: Iterable[Any], log: str = '') -> bool:
        """
        not_in fails calling test, logs log and returns False if given
        value is in given iterable itr; otherwise True is returned.
        """
        if value not in itr:
            return True
        self._fail_cmp(value, itr, 'not in', log)
        return False

    def is_(self, value: Any, other: Any, log: str='') -> bool:
        """
        is_ fails calling test, logs log and return False if given value
        is not identical to other value; otherwise True is returned.
        """
        if value is other:
            return True  # TODO: uncommenting this line crashes watcher
        self._fail_cmp(value, other, 'is', log)
        return False

    def is_not(self, value: Any, other: Any, log: str='') -> bool:
        """
        is_not fails calling test, logs log and return False if given
        value is identical with other value; otherwise True is returned.
        """
        if value is not other:
            return True
        self._fail_cmp(value, other, 'is not', log)
        return False

    def is_instance(self, value: Any, type_: Any, log: str='')-> bool:
        """
        is_instance fails calling test, logs log and returns False if
        given value is not an instance of given type; otherwise True is
        returned.
        """
        if isinstance(value, type_):
            return True
        self._fail_cmp(value, type_, 'is instance of', log)
        return False

    def is_not_instance(self, value: Any, type_: Any, log: str='')-> bool:
        """
        is_not_instance fails calling test, logs log and returns False
        if given value is an instance of given type; otherwise True is
        returned.
        """
        if not isinstance(value, type_):
            return True
        self._fail_cmp(value, type_, 'is not instance of', log)
        return False

    def eq(self, value: Any, other: Any, log: str = '') -> bool:
        """
        eq fails calling test, logs log and returns False if given value
        is not equal to other; otherwise True is returned.
        """
        if value == other:
            return True
        self._fail_cmp(value, other, '==', log)
        return False

    def not_eq(self, value: Any, other: Any, log: str = '') -> bool:
        """
        not_eq fails calling test, logs log and returns False if given
        value is equal to other; otherwise True is returned.
        """
        if value != other:
            return True
        self._fail_cmp(value, other, '!=', log)
        return False

    def eq_str(self, value: Any, other: Any, log: str = '') -> bool:
        """
        eq_str fails calling test, logs log and returns False if given
        value's string representation is not equal to other's; otherwise
        True is returned.
        """
        if str(value) == str(other):
            return True
        self._fail_cmp(
            str(value),
            str(other),
            '==', log
        )
        return False

    def not_eq_str(self, value: Any, other: Any, log: str = '') -> bool:
        """
        not_eq_str fails calling test, logs log and returns False if
        given value's string representation is equal to other's;
        otherwise True is returned.
        """
        if str(value) != str(other):
            return True
        self._fail_cmp(
            str(value).strip('"'),
            str(other).strip('"'),
            '!=', log
        )
        return False

    def eq_repr(self, value: Any, other: Any, log: str = '') -> bool:
        """
        eq_repr fails calling test, logs log and returns False if given
        value's canonical string representation is not equal to other's;
        otherwise True is returned.
        """
        if repr(value) == repr(other):
            return True
        self._fail_cmp(
            repr(value).strip('"'),
            repr(other).strip('"'),
            '==', log
        )
        return False

    def not_eq_repr(self, value: Any, other: Any, log: str = '') -> bool:
        """
        not_eq_repr fails calling test, logs log and returns False if
        given value's canonical string representation is equal to
        other's; otherwise True is returned.
        """
        if repr(value) != repr(other):
            return True
        self._fail_cmp(
            repr(value).strip('"'),
            repr(other).strip('"'),
            '!=', log
        )
        return False

    def matched(
        self, s: str, pattern: str, flags: int = 0, log: str = ''
    ) -> bool:
        """
        matched fails calling test, logs log and returns False if given
        string s is not matched by given pattern; otherwise True is
        returned.
        """
        if re.match(pattern, s, flags) is not None:
            return True
        self._fail_cmp(s, pattern, 'is matched by', log)
        return False

    def space_matched(self, s: str, *ss: str, log: str = '') -> bool:
        """
        space_matched fails calling test, logs log and returns False if
        given string s is not matched by the pattern calculated from
        strings ss; otherwise True is returned.  Note all regex special
        characters in each string s' in ss are escaped before they are
        joined together with \s* as separator. e.g. let s be
        <td>
            42
        </td>
        then t.space_matched(s, '<td>', '42', '</td>') evaluates to True.
        """
        ptt = '\s*' + '\\s*'.join([re.escape(s) for s in ss]) + '\s*'
        if re.match(ptt, s) is not None:
            return True
        self._fail_cmp(s, ptt, 'is space-matched by', log)
        return False

    def star_matched(self, s: str, *ss: str, log: str = '') -> bool:
        """
        star_matched fails calling test, logs log and returns False if
        given string s is not matched by the pattern calculated from
        strings ss; otherwise True is returned.  Note all regex special
        character in each string s' in ss are escaped before they are
        joined together with .* as separator. e.g. let s be
        <td>
            42
        </td>
        then t.star_matched(s, 'td', '42', 'td') evaluates to True.
        """
        ptt = '.*' + '.*'.join([re.escape(s) for s in ss]) + '.*'
        if re.match(ptt, s, re.DOTALL) is not None:
            return True
        self._fail_cmp(s, ptt, 'is star-matched by', log)
        return False

    def not_matched(
        self, s: str, pattern: str, flags: int = 0, log: str = ''
    ) -> bool:
        """
        not_matched fails calling test, logs log and returns False if
        given string s is matched by given pattern; otherwise True is
        returned.
        """
        if re.match(pattern, s, flags) is None:
            return True
        self._fail_cmp(s, pattern, 'is not matched by', log)
        return False