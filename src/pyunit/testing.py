# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import traceback
from typing import TextIO as _TextIO, Any, Callable, Tuple
from dataclasses import dataclass as _dataclass
import sys as _sys

from pyunit._internal.assert_ import T, FatalError as _FatalError
from pyunit._internal import reporting
from pyunit._internal.watcher import REPORT_ARG as _REPORT_JSON


_SPECIAL = { 'init', 'setup', 'tear_down', 'finalize' }  # type: set
"""SPECIAL holds all names of test suite methods considered special."""


@_dataclass
class Config:
    """configuration for test-runs"""
    reporter: reporting.Report | None = None
    out: _TextIO = _sys.stdout
    single: str = ""


def run(suite: Any, config: Config | None = None):
    """
    run executes *every* callable c (i.e also static or class methods) of
    given suite iff c is non-special and non-dunder.  Each call gets a T
    instance for controlling the test-flow and assertions.

        class TestedSubject:

            def expected_behavior(self, t: pyunit.T):
                t.breakIfNot(t.truthy(True))


        if __name__ == '__main__':
            pyunit.run(TestedSubject)
    """
    _suite = suite if not isinstance(suite, type) else suite()
    config = config or Config()
    
    report = config.reporter or (reporting.TDD() 
        if _REPORT_JSON in _sys.argv else reporting.Default())
    def counter(): return None
    try:
        counter = report.increase_test_count  # type: ignore
    except AttributeError:
        pass
    if len(config.single):
        _run_single_test(_suite, report, config, counter)
        return
    tt, ss = _suite_methods(_suite)
    if not _run_init(ss, report, _suite, config):
        return
    for name in tt:
        test = getattr(_suite, name)
        t = T(fail=lambda: report.fail(name),
            log=lambda msg: report.log(name, msg))
        if not _run_setup(ss, t):
            _run_tear_down(ss, t)
            continue
        try:
            test(t)
            counter()
        except _FatalError:
            pass
        except Exception:
            t.failed(short_traceback(''))
        _run_tear_down(ss, t)
    _run_finalize(ss, report)
    report.print(_suite.__class__.__name__, config.out)


def _run_init(
    ss: '_Specials', 
    report: reporting.Report,
    s: Any,
    config: Config
) -> bool:
    if ss.init is None:
        return True
    init = 'initialization'
    t = T(fail=lambda: report.fail(init),
        log=lambda msg: report.log(init, msg))
    try:
        ss.init(t)
    except Exception as e:
        report.fail(init)
        indent = '  '
        t.failed(f'initialization failed:\n{indent}' + short_traceback(indent))
        report.print(s.__class__.__name__, config.out)
        return False
    return True


def short_traceback(indent: str) -> str:
    lines = traceback.format_exc().split('\n')[1:-1]
    if len(lines) > 5:
        lines = lines[-5:]
    return f'\n{indent}'.join(reversed(lines))


def _run_setup(ss: '_Specials', t: T) -> bool:
    if ss.setup is None:
        return True
    try:
        ss.setup(t)
    except:
        indent = '  '
        t.failed(f'setup failed:\n{indent}' + short_traceback(indent))
        return False
    return True
    

def _run_tear_down(ss: '_Specials', t: T):
    if ss.tear_down is None:
        return
    try:
        ss.tear_down(t)
    except Exception as e:
        indent = '  '
        t.failed(f'tear down failed:\n{indent}' + short_traceback(indent))


def _run_finalize(ss: '_Specials', report: reporting.Report):
    if ss.finalize is None:
        return
    finalize = 'finalize'
    t = T(fail=lambda: report.fail(finalize), 
        log=lambda msg: report.log(finalize, msg))
    try:
        ss.finalize(t)
    except:
        report.fail(finalize)
        indent = '  '
        t.failed(f'finalize failed:\n{indent}' + short_traceback(indent))



def _run_single_test(
    suite: Any,
    report: reporting.Report,
    config: Config,
    counter: Callable
):
    tt, ss = _suite_methods(suite)
    if not _run_init(ss, report, suite, config):
        return
    for name in tt:
        if name != config.single:
            continue
        t = T(fail=lambda: report.fail(name), 
            log=lambda msg: report.log(name, msg))
        if not _run_setup(ss, t):
            _run_tear_down(ss, t)
            return
        test = getattr(suite, name)
        try:
            test(t)
            counter()
        except _FatalError:
            pass
        _run_tear_down(ss, t)
        break
    _run_finalize(ss, report)
    report.print(suite.__class__.__name__, config.out)


@_dataclass
class _Specials:
    init: Callable[[T], None] | None
    setup: Callable[[T], None] | None
    tear_down: Callable[[T], None] | None
    finalize: Callable[[T], None] | None


def _suite_methods(suite) -> Tuple[list[str], _Specials]:
    tt, ss = [], _Specials(None, None, None, None)
    for m in dir(suite):
        if not callable(getattr(suite, m, None)) or m.startswith('_'):
            continue
        if m in _SPECIAL:
            match m:
                case 'init':
                    ss.init = getattr(suite, m, None)
                case 'setup':
                    ss.setup = getattr(suite, m, None)
                case 'tear_down':
                    ss.tear_down = getattr(suite, m, None)
                case 'finalize':
                    ss.finalize = getattr(suite, m, None)
            continue
        tt.append(m)
    return tt, ss