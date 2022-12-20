# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


from typing import Generator, Tuple, FrozenSet, TextIO
import ast
import os
import sys
import json
import time
from pathlib import Path
from multiprocessing.pool import Pool
import subprocess
from queue import Queue, Empty

pyunit_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if pyunit_path not in sys.path:
    sys.path.insert(0, pyunit_path)

from pyunit._internal.reporting import (
    JSN_TESTS_COUNT, JSN_FAILS_COUNT, JSN_TEST_SUITE, JSN_FAILS,
    JSN_TEST_LOGS)

from pyunit._internal.tui import TUI

REPORT_ARG = '--report=json'


class DirNoPackage(Exception):
    pass


class Dir:
    """
    Dir represents a directory from pyunit's points of and may be
    passed to the watcher-modules main function in order to be watched
    for changes and executing test-runs appropriately.
    """

    def __init__(self, dir: str) -> None:
        """
        init initializes a watched directory and fails if directory is
        not a package.  In case the watched package's root package is
        not in python's search-paths it is added.  Note a watched dir
        will in its operations ignore the '__pycache__'-package and
        '__init__.py'-module.
        """
        self.dir = Path(dir)  # type: Path
        if not self.is_package(self.dir):
            raise DirNoPackage(f"'{dir}' is not a package")
        self._ignore_packages = ['__pycache__']
        self._ignore_modules = ['__init__.py']
        root = self.root_package
        if str(root.parent) not in sys.path:
            sys.path.insert(0, str(root.parent))
        self._last_snapshot = Snapshot(frozenset(), frozenset())
        self.timeout = 2.0  # type: float

    def is_package(self, dir: Path) -> bool:
        """
        is package returns true if given Path dir is a package; false
        otherwise.
        """
        for f in dir.iterdir():
            if not f.is_dir() and f.name == '__init__.py':
                return True
        return False

    @property
    def root_package(self) -> Path:
        """
        returns the last ancestor of the watched package that is a
        package.
        """
        try:
            return self._root_package
        except AttributeError:
            dir = self.dir.absolute()
            while self.is_package(dir.parent):
                dir = dir.parent
            self._root_package = dir  # type: Path
        return self._root_package

    def sub_packages(self) -> Generator['Pkg', None, None]:
        """
        sub_packages provides all packages inside the directory and the
        watched package itself.
        """
        dd = [self.dir]
        while len(dd):
            dir = dd.pop()
            for d in dir.iterdir():
                if not d.is_dir() or d.name in self._ignore_packages:
                    continue
                dd.append(d)
            yield Pkg(dir)

    def test_modules(self) -> Generator['TM', None, None]:
        """
        test_modules provides a generator of all test-modules in
        given Dir self and its sub-modules.
        """
        for p in self.sub_packages():
            for path in p.dir.iterdir():
                if path.is_dir() or not self.is_test_module(path):
                    continue
                yield TM(self, path)

    def is_test_module(self, p: Path) -> bool:
        """
        is_test_module returns True if given Path p is identified as a
        test-module by either having a test_ prefix or a "_test.py"
        suffix. It returns False otherwise.
        """
        return (p.name.startswith("test_")
                or p.name.endswith("_test.py"))

    def production_modules(self) -> Generator[Path, None, None]:
        for p in self.sub_packages():
            for path in p.dir.iterdir():
                if not self.is_production(path):
                    continue
                yield path
        if self.root_package != self.dir:
            for path in self.root_package.iterdir():
                if not self.is_production(path):
                    continue
                yield path

    def is_production(self, p: Path) -> bool:
        return (not p.is_dir() and p.name.endswith(".py")
                and not self.is_test_module(p))

    def test_modules_to_run(self) -> set['TM']:
        """
        test_modules_to_run returns the test-modules which have been
        updated or import an updated production module since its last
        call.  Hence test_modules_to_run must be called only once per
        run-request. 
        """
        now = Snapshot(
            frozenset(tm for tm in self.test_modules()),
            frozenset(pm for pm in self.production_modules())
        )
        tt = self._last_snapshot.updated(now)
        self._last_snapshot = now
        return tt

    def run_test_module(self, tm: 'TM') -> Tuple[list[str], dict[str, str]]:
        ss = []  # type: list[str]
        ee = dict()
        result = subprocess.run([
            "python", str(tm.path), REPORT_ARG],
            capture_output=True,
            text=True,
            cwd=str(tm.path.parent),
            timeout=self.timeout
        )
        if result.stderr:
            rel_tm = str(tm).removeprefix(str(self.root_package))
            ee[rel_tm] = '    ' + '\n    '.join(
                result.stderr.strip().split('\n'))
            return ss, ee
        if not result.stdout:
            return ss, ee
        for i, s in enumerate(result.stdout.split('\n{')):
            if not i:
                ss.append(s)
                continue
            ss.append('{' + s)
        return ss, ee

    def print(self, ss: list[str], ee: dict[str, str], out: TUI):
        out.clear()
        tests_count, fails_count, parsed = 0, 0, []
        for jsn in [json.loads(s) for s in ss]:
            tests_count += jsn[JSN_TESTS_COUNT]
            fails_count += jsn[JSN_FAILS_COUNT]
            parsed.append(jsn)
        summary = (f'pyunit: watcher: run {tests_count} tests of ' +
                   f'witch {fails_count} failed')
        if fails_count:
            out.write_line(out.failed(summary))
        else:
            out.write_line(out.passed(summary))
        for m, err in ee.items():
            out.write_line()
            out.write_line(out.failed(f'run failed: .{m}'), 4)
            out.write_line(err, 4)
        for jsn in parsed:
            out.write_line()
            out.write_line(f'{jsn[JSN_TEST_SUITE]}', 4)
            fails = jsn[JSN_FAILS]
            for t, ll in jsn[JSN_TEST_LOGS].items():
                if t in fails:
                    out.write_line(out.failed(f'{t}'), 6)
                else:
                    out.write_line(f'{t}', 6)
                for l in ll:
                    out.write_line(f'{l}', 8)


class Pkg:
    """
    Pkg represents a subpackage in a watched package's root package.
    """

    def __init__(self, d: Path) -> None:
        self.dir = d

    def __str__(self) -> str:
        return str(self.dir)


class Snapshot:

    def __init__(self, tt: FrozenSet['TM'], pp: FrozenSet[Path]) -> None:
        self.tt = tt
        self.pp = pp
        self.mt = dict()  # type: dict[str, float]
        for t in tt:
            self.mt[t.path.as_posix()] = t.path.stat().st_mtime_ns
        for p in pp:
            self.mt[p.as_posix()] = p.stat().st_mtime_ns

    def updated(self, other: 'Snapshot') -> set['TM']:
        """
        updated returns the set of test modules which are
            - not in this snapshot's test modules
            - which have been modified in other snapshot
            - which import a modified production module of other snapshot
        """
        tt = set()
        for p in other.pp:
            if (p.as_posix() not in self.mt
                    or p.stat().st_mtime_ns > self.mt[p.as_posix()]):
                for tm in other.production_to_test(p):
                    tt.add(tm)
        for tm in other.tt:
            if (tm.path.as_posix() not in self.mt
                    or tm.path.stat().st_mtime_ns
                    > self.mt[tm.path.as_posix()]):
                tt.add(tm)
        return tt

    def production_to_test(self, prd: Path):
        """
        production_to_test returns all test-modules importing the
        production module with given Path prd.
        """
        try:
            return self._pp_to_tt[prd.as_posix()]
        except AttributeError:
            self._pp_to_tt = dict()  # type: dict[str, list[TM]]
            for tm in self.tt:
                for p in tm.production_dependencies():
                    if p.as_posix() not in self._pp_to_tt:
                        self._pp_to_tt[p.as_posix()] = []
                    self._pp_to_tt[p.as_posix()].append(tm)
        except KeyError:
            return []
        if prd.as_posix() not in self._pp_to_tt:
            return []
        return self._pp_to_tt[prd.as_posix()]


class TM:
    """
    TM wraps a Path representing a test module of the watched package or
    on one of its sub-packages.
    """

    def __init__(self, watched: 'Dir', p: Path) -> None:
        self.path = p
        self.watched = watched

    def __str__(self) -> str:
        """__str__ reports the string representation of wrapped Path"""
        return str(self.path)

    def production_dependencies(self) -> Generator[Path, None, None]:
        """
        production_dependencies parses a test-module's root-imports
        for production-module imports of the watched package or one of
        it's sub-packages or the root-package.  Note relative-imports
        are not treated as well as __init__.py modules.
        """
        parsed = None
        try:
            parsed = ast.parse(self.path.read_text())
        except:
            return
        for node in ast.iter_child_nodes(parsed):
            if isinstance(node, ast.ImportFrom):
                if not node.module:
                    continue
                dep = self._import_to_module(node.module)
                if dep:  # may be a module imported into dep
                    for name in node.names:
                        d, found = self._resolve_from_import(
                            dep, name.name)
                        if found:
                            if d:
                                yield d
                        else:
                            yield dep
                    continue
                if not self._is_package_import(node.module):
                    continue
                for name in node.names:
                    dep = self._import_to_module(
                        node.module + '.' + name.name)
                    if dep:
                        yield dep
                continue
            if isinstance(node, ast.Import):
                for name in node.names:
                    dep = self._import_to_module(name.name)
                    if dep:
                        yield dep

    def _resolve_from_import(
        self, mod: Path | None, imp: str
    ) -> Tuple[Path | None, bool]:
        if not mod:
            return None, False
        for node in ast.iter_child_nodes(ast.parse(mod.read_text())):
            if isinstance(node, ast.ImportFrom):
                if not node.module:
                    continue
                dep = self._import_to_module(node.module)
                if dep:
                    for name in node.names:
                        if name.name != imp:
                            continue
                        return self._resolve_from_import(dep, imp)
                    continue
                if not self._is_package_import(node.module):
                    continue
                for name in node.names:
                    if name.name != imp:
                        continue
                    dep = self._import_to_module(
                        node.module + '.' + name.name)
                    if dep:
                        return dep, True
                    return None, False
                continue
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name != imp:
                        continue
                    dep = self._import_to_module(name.name, mod)
                    if dep:
                        return dep, True
        return None, False

    def _is_package_import(self, pkg: str) -> bool:
        rel_path = Path(pkg.replace(".", os.sep))
        if rel_path.name == self.watched.root_package.name:
            return True
        abs_path = self.watched.root_package.parent.joinpath(rel_path)
        subs = set(p.dir.as_posix() for p in self.watched.sub_packages())
        if abs_path.as_posix() in subs:
            return True
        return rel_path in [p for p in self.watched.sub_packages()]

    def _import_to_module(
        self, module_string: str, mod: Path | None = None
    ) -> Path | None:
        rel_path = Path(module_string.replace(".", os.sep) + ".py")
        abs_path = self.watched.root_package.parent.joinpath(rel_path)
        if abs_path.exists():
            return abs_path
        if not mod:
            mod = self.path
        abs_path = mod.parent.joinpath(rel_path)
        if abs_path.exists():
            return abs_path
        return None


def run_watcher(dir: Dir, should_quite: Queue):
    while True:
        try:
            should_quite.get(False)
        except Empty:
            pass
        else:
            break
        time.sleep(0.3)
    print("gracefully stopped")


def quitClosure(q: Queue) -> callable:
    return lambda sig, frame: q.put(True)


if __name__ == '__main__':
    import signal

    try:
        dir = Dir(os.getcwd())
    except DirNoPackage:
        print('can only watch packages (dir with __init__.py file)' +
            f'\n  {os.getcwd()}\nis no package.')
        sys.exit(1)
    else:
        quitQueue = Queue()
        signal.signal(signal.SIGINT, quitClosure(quitQueue))
        run_watcher(dir, quitQueue)
