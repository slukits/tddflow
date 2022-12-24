# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


help = """
NAME

tddflow - a simple lightweight testing framework that can used as command
         watch a directory for modifications and run related tests
         automatically.

SYNOPSIS
    tddflow [--dbg] [--ignore-pkg] [--ignore-mdl] [--frequency]
           [--run-timeout] [--map]

DESCRIPTION
    tddflow as a command watches test-modules and production-modules in
    the directory it was started and nested packages for modifications.
    If a test-module is modified it is executed.  Is a production module
    modified all test modules which can be mapped to this module due to
    a static import analysis are executed.  Note you can add mappings as
    arguments as well.  It then reports the number of run tests and how
    many of those have failed.  Failed tests and logging tests are
    reported verbosely with their loggings.

    The typical use cases of tddflow are:
        - write a failing test, i.e. tddflow shows you the red bar, make
          the test "green", refactor and write a failing test again ...
        - if one quickly wants to examine a return/variable value it can
          be logged in a test and tddflow will report the logged value.

COMMAND LINE OPTIONS
    --dbg    tddflow runs all tests-modules it thinks it should
             run and reports test-modules which were modified and test
             modules which were triggered by an production module
             modification.  I.e. one can check which tests are run at
             which module-modification.

    --ignore-pkg=dirname
            takes a directory name and tddflow will ignore all packages
            having this directory name (Note paths are not handled).

    --ignore-mdl=module.py 
            takes a file name and tddflow will ignore modules with given
            file name (Note paths are not handled).

    --frequency=0.3 
            takes a float determining the frequency with which tddflow
            checks the watched directory.

    --run-timeout=20.0
            takes a float determining for how long tddflow waits for a
            test module to execute before a timeout is reported.

    --map='production/module.py->tests/test_module.py'
            takes two '->' separated paths which represent a production
            module and a test module in the watched package.  It may be
            an absolute path or a path relative to the watched
            directory's root-package.  Adding such a mapping has the
            consequence that a modification of module.py triggers a run
            of test_module.py.

HAPPY TESTING
"""

from typing import Callable, Any, Tuple
import signal
import os
import sys
from multiprocessing import Queue

from tddflow._internal.watcher import Dir, watcher, DirNoPackage

def quitClosure(q: Queue) -> Callable[[Any, Any], None]:
    return lambda sig, frame: q.put(True)


ARG_IGNORE_PKG = '--ignore-pkg='
ARG_IGNORE_MDL = '--ignore-mdl='
ARG_DBG = '--dbg'
ARG_FREQUENCY = '--frequency='
ARG_RUN_TIMEOUT = '--run-timeout='
ARG_MAP = '--map='
ARG_HELP = '--help'


class HelpRequest(Exception): pass


def process_args(dir: Dir) -> Tuple[float, bool]:
    dbg, frq, tm_out = False, 0.5, 20.0
    for arg in sys.argv[1:]:
        if arg.startswith(ARG_IGNORE_PKG):
            dir._ignore_packages.append(arg.split("=")[1])
        if arg.startswith(ARG_IGNORE_MDL):
            dir._ignore_modules.append(arg.split("=")[1])
        if arg.startswith(ARG_FREQUENCY):
            try:
                frq = float(arg.split("=")[1])
            except ValueError:
                print("couldn't convert frequency", file=sys.stderr)
        if arg.startswith(ARG_RUN_TIMEOUT):
            try:
                tm_out = float(arg.split('=')[1])
            except ValueError:
                print("couldn't convert timeout", file=sys.stderr)
        if arg.startswith(ARG_HELP) or arg.startswith('help'):
            raise HelpRequest()
        if arg == ARG_DBG:
            dbg = True
    dir.timeout = tm_out
    return frq, dbg

try:
    dir = Dir(os.getcwd())
except DirNoPackage:
    print('can only watch packages (dir with __init__.py file)' +
            f'\n  {os.getcwd()}\nis no package.')
    sys.exit(1)
else:
    quitQueue = Queue()  # type: Queue
    signal.signal(signal.SIGINT, quitClosure(quitQueue))
    try:
        frq, dbg = process_args(dir)
    except HelpRequest:
        print(help)
        sys.exit(0)
    else:
        watcher(dir, quitQueue, frq, dbg)
