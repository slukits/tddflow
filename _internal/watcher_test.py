# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import os
import sys
from modulefinder import ModuleFinder

import tempfile
import watcher
from testcontext import testing
from assert_ import T

golden = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'watchergolden'))

golden_tests = os.path.join(golden, 'tests')

sub_packages = {
    golden,
    golden_tests,
    '/home/goedel/python/pyunit/_internal/watchergolden/flat', 
    '/home/goedel/python/pyunit/_internal/watchergolden/flat/is_better',
    '/home/goedel/python/pyunit/_internal/watchergolden/flat/is_better/than_nested'
}

golden_test_modules = {
    os.path.join(golden, 'suffix_test.py'),
    os.path.join(golden, 'test_prefix.py'),
    os.path.join(golden_tests, 'suffix_dir_test.py'),
    os.path.join(golden_tests, 'test_prefix_dir.py')
}

golden_tm_dependencies = {
    os.path.join(golden, 'suffix_test.py'): {
        '/home/goedel/python/pyunit/testing.py',
        os.path.join(golden, 'pm1.py'),
        os.path.join(golden, 'pm2.py'),
    },
    os.path.join(golden, 'test_prefix.py'): {
        '/home/goedel/python/pyunit/testing.py',
        os.path.join(golden, 'pm1.py'),
    },
    os.path.join(golden_tests, 'suffix_dir_test.py'): {
        '/home/goedel/python/pyunit/testing.py',
        os.path.join(golden, 'pm1.py'),
    },
    os.path.join(golden_tests, 'test_prefix_dir.py'): {
        '/home/goedel/python/pyunit/testing.py',
        os.path.join(golden, 'pm2.py'),
        os.path.join(golden, 'flat/is_better/than_nested/deep.py')
    }
}


class AWatcher:

    def initialization_fails_if_not_in_package(self, t: T):
        t.raises(lambda: watcher.Dir(
            tempfile.gettempdir()), watcher.DirNoPackage)

    def initialization_fails_if_given_dir_not_found(self, t: T):
        t.raises(lambda: watcher.Dir('/hurz_42'), FileNotFoundError)

    def finds_the_root_package_of_initial_dir(self, t: T):
        exp = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        t.truthy(exp == str(watcher.Dir(golden).root_package))

    def finds_watched_sub_packages_of_initial_dir(self, t: T):
        got = set(str(d) for d in watcher.Dir(golden).sub_packages())
        t.truthy(sub_packages == got)

    def finds_test_modules_in_watched_sub_packages(self, t: T):
        w = watcher.Dir(golden)
        t.fatal_if_not(t.truthy(
            4 == len([tm for tm in w.test_modules()])))
        for tm in w.test_modules():
            t.truthy(str(tm) in golden_test_modules)

    def test_module_knows_its_production_dependencies(self, t: T):
        w = watcher.Dir(golden)
        for tm in w.test_modules():
            exp = golden_tm_dependencies[tm.path.as_posix()]
            got = set(dep.as_posix() for dep in tm.production_dependencies())
            t.truthy(exp == got)


if __name__ == '__main__':
    testing.run(AWatcher)
