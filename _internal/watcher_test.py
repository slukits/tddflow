# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import os
import io
import time
import tempfile
from pathlib import Path

from testcontext import testing
import watcher
import tui
from assert_ import T

golden = Path(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'watchergolden')))

golden_tests = golden.joinpath('tests')

testing_path = Path('/home/goedel/python/pyunit/testing.py')

sub_packages = {
    golden,
    golden_tests,
    golden.joinpath('flat'), 
    golden.joinpath('flat/is_better'),
    golden.joinpath('flat/is_better/than_nested'),
    golden.joinpath('failed')
}

golden_test_modules = {
    golden.joinpath('suffix_test.py'),
    golden.joinpath('test_prefix.py'),
    golden.joinpath('failed/compile_test.py'),
    golden_tests.joinpath('suffix_dir_test.py'),
    golden_tests.joinpath('test_prefix_dir.py')
}

golden_tm_dependencies = {
    golden.joinpath('suffix_test.py'): {
        testing_path,
        golden.joinpath('pm1.py'),
        golden.joinpath('pm2.py')
    },
    golden.joinpath('test_prefix.py'): {
        testing_path,
        golden.joinpath('pm1.py'),
    },
    golden_tests.joinpath('suffix_dir_test.py'): {
        testing_path,
        golden.joinpath('pm1.py'),
    },
    golden_tests.joinpath('test_prefix_dir.py'): {
        testing_path,
        golden.joinpath('pm2.py'),
        golden.joinpath('flat/is_better/than_nested/deep.py')
    }
}

golden_pm_dependencies = {
    testing_path: {
        golden.joinpath('suffix_test.py'),
        golden.joinpath('test_prefix.py'),
        golden_tests.joinpath('suffix_dir_test.py'),
        golden_tests.joinpath('test_prefix_dir.py')
    },
    os.path.join(golden, 'pm1.py'): {
        golden.joinpath('suffix_test.py'),
        golden.joinpath('test_prefix.py'),
        golden_tests.joinpath('suffix_dir_test.py')
    },
    os.path.join(golden, 'pm2.py'): {
        golden.joinpath('suffix_test.py'),
        golden_tests.joinpath('test_prefix_dir.py')
    },
    os.path.join(golden, 'flat/is_better/than_nested/deep.py'): {
        golden_tests.joinpath('test_prefix_dir.py')
    }
}

golden_production = {
    golden.joinpath('flat/is_better/than_nested/deep.py'),
    golden.joinpath('flat/is_better/nest.py'),
    golden.joinpath('pm2.py'),
    golden.joinpath('pm1.py'),
    golden.joinpath('context.py'),
    golden.joinpath('context.py'),
    golden.joinpath('tests/context.py')
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
        t.truthy(exp == str(watcher.Dir(str(golden)).root_package))

    def finds_watched_sub_packages_of_initial_dir(self, t: T):
        got = set(d.dir for d in watcher.Dir(str(golden)).sub_packages())
        t.truthy(sub_packages == got)

    def finds_test_modules_in_watched_sub_packages(self, t: T):
        w = watcher.Dir(str(golden))
        got = set(tm.path for tm in w.test_modules())
        t.truthy(golden_test_modules == got)

    def test_module_knows_its_production_dependencies(self, t: T):
        w = watcher.Dir(str(golden))
        for tm in w.test_modules():
            if tm.path not in golden_pm_dependencies:
                continue
            exp = golden_tm_dependencies[tm.path]
            got = set(dep for dep in tm.production_dependencies())
            t.truthy(exp == got)

    def finds_production_modules_in_watched_sub_packages(self, t: T):
        w = watcher.Dir(str(golden))
        got = set(pm for pm in w.production_modules())
        t.truthy(golden_production.issubset(got))

    def runs_initially_all_test_modules(self, t: T):
        w = watcher.Dir(str(golden))
        t.truthy(golden_test_modules 
            == set(tm.path for tm in w.test_modules_to_run()))

    def runs_modified_test(self, t: T):
        w = watcher.Dir(str(golden))
        w.test_modules_to_run()
        tp = golden_test_modules.pop()
        time.sleep(0.01)
        os.utime(str(tp))
        t.truthy(tp == w.test_modules_to_run().pop().path)

    def runs_tests_importing_modified_production_modules(self, t: T):
        w = watcher.Dir(str(golden))
        w.test_modules_to_run()
        time.sleep(0.01)
        for pm, tt in golden_pm_dependencies.items():
            os.utime(str(pm))
            t.truthy(tt == set(tm.path for tm in w.test_modules_to_run()),
                f'{tt} != {set(tm.path for tm in w.test_modules_to_run())}')
        
    def reports_the_number_of_run_and_failed_tests(self, t: T):
        out = io.StringIO()
        w, ss, ee = watcher.Dir(str(golden)), [], dict()
        for tm in w.test_modules_to_run():
            _ss, _ee = w.run_test_module(tm)
            if len(_ss):
                ss.extend(_ss)
            if len(_ee):
                ee.update(_ee)
        w.print(ss, ee, tui.TUI(out))
        t.truthy('8' in out.getvalue())
        t.truthy('4' in out.getvalue())
        t.log(out.getvalue())


    # def test_reporting(self, t: T):
    #     out = io.StringIO()
    #     w = watcher.Dir(str(golden))
    #     w.run_test_modules(out=out)
    #     t.log(out.getvalue())


if __name__ == '__main__':
    testing.run(AWatcher)
