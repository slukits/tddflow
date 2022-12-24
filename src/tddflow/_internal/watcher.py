# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


from typing import Generator, Tuple, FrozenSet, Callable, Iterable, Any, Iterator
import ast
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from multiprocessing.pool import Pool
import multiprocessing
import subprocess
from queue import Queue, Empty

tddflow_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if tddflow_path not in sys.path:
    sys.path.insert(0, tddflow_path)

from tddflow._internal.reporting import (
    JSN_TESTS_COUNT, JSN_FAILS_COUNT, JSN_TEST_SUITE, JSN_FAILS,
    JSN_TEST_LOGS)

from tddflow._internal.tui import TUI, Args

REPORT_ARG = '--report=json'


class DirNoPackage(Exception):
    pass


class Dir:
    """
    Dir represents a directory from tddflow's points of and may be
    passed to the watcher-modules main function in order to be watched
    for changes and executing test-runs appropriately.
    """

    def __init__(
        self, dir: str,
        dep_gen: Callable[
            [Iterable['TM']], list[Tuple[Path, list[Path]]]] | None = None
    ) -> None:
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
        self._dep_gen = dep_gen or TM.dependencies
        self._last_snapshot = Snapshot(
            frozenset(), frozenset(), self._dep_gen, self.mappings())
        self.timeout = 10.0  # type: float

    def map(self, s: str):
        if '->' not in s: return
        p, t = s.split("->", maxsplit=1)
        if self.root_package.joinpath(p).exists():
            p = self.root_package.joinpath(p)
        if self.root_package.joinpath(t).exists():
            t = self.root_package.joinpath(t)
        try:
            self.static_maps[p].append(Path(t))
        except AttributeError:
            self.static_maps = {p: [Path(t)]}
        except KeyError:
            self.static_maps[p] = [Path(t)]

    def mappings(self) -> dict[Path, list[Path]]:
        try:
            return self.static_maps
        except AttributeError:
            return dict()

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
                if (not d.is_dir() or d.name in self._ignore_packages
                        or not self.is_package(d)):
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
        return ((p.name.startswith("test_")
                or p.name.endswith("_test.py"))
                and p.name not in self._ignore_modules)

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
                and p.name not in self._ignore_modules
                and not self.is_test_module(p))

    def test_modules_to_run(self) -> 'Analysis':
        """
        test_modules_to_run returns the test-modules which have been
        updated or import an updated production module since its last
        call.  Hence test_modules_to_run must be called only once per
        run-request.
        """
        now = Snapshot(
            frozenset(tm for tm in self.test_modules()),
            frozenset(pm for pm in self.production_modules()),
            self._dep_gen, self.mappings()
        )
        tt = self._last_snapshot.updated(now)
        self._last_snapshot = now
        return tt

    def run_test_module(self, tm: Path) -> Tuple[list[str], dict[str, str]]:
        ss = []  # type: list[str]
        ee = dict()
        try:
            result = subprocess.run([
                "python", str(tm), REPORT_ARG],
                capture_output=True,
                text=True,
                cwd=str(tm.parent),
                timeout=self.timeout
            )
        except subprocess.TimeoutExpired:
            rel_tm = str(tm).removeprefix(str(self.root_package))
            ee[rel_tm] = '    ' + 'test run\'s timeout expired'
            return ss, ee
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


class Pkg:
    """
    Pkg represents a subpackage in a watched package's root package.
    """

    def __init__(self, d: Path) -> None:
        self.dir = d

    def __str__(self) -> str:
        return str(self.dir)


class Snapshot:

    def __init__(
        self,
        tt: FrozenSet['TM'],
        pp: FrozenSet[Path],
        dep_gen: Callable[[Iterable['TM']], list[Tuple[Path, list[Path]]]],
        static_mappings: dict[Path, list[Path]]
    ) -> None:
        self.tt = tt
        self.pp = pp
        self.dep_gen = dep_gen
        self.static_mappings = static_mappings
        self.mt = dict()  # type: dict[str, float]
        for t in tt:
            self.mt[t.path.as_posix()] = t.path.stat().st_mtime_ns
        for p in pp:
            self.mt[p.as_posix()] = p.stat().st_mtime_ns

    def updated(self, other: 'Snapshot') -> 'Analysis':
        """
        updated returns the set of test modules which are
            - not in this snapshot's test modules
            - which have been modified in other snapshot
            - which import a modified production module of other snapshot
        """
        analysis = Analysis()
        for p in other.pp:
            if (p.as_posix() not in self.mt
                    or p.stat().st_mtime_ns > self.mt[p.as_posix()]):
                analysis.mod_pp[str(p)] = other.production_to_test(p)
        for tm in other.tt:
            if (tm.path.as_posix() not in self.mt
                    or tm.path.stat().st_mtime_ns
                        > self.mt[tm.path.as_posix()]):
                analysis.mod_tt.add(tm.path)
        return analysis

    def production_to_test(self, prd: Path) -> list[Path]:
        """
        production_to_test returns all test-modules importing the
        production module with given Path prd.
        """
        try:
            return self._pp_to_tt[prd.as_posix()]
        except AttributeError:
            self._pp_to_tt = dict()  # type: dict[str, set[Path]]
            for tm, dd in self.dep_gen(self.tt):
                for d in dd:
                    if d.as_posix() not in self._pp_to_tt:
                        self._pp_to_tt[d.as_posix()] = set()
                    self._pp_to_tt[d.as_posix()].add(tm)
            for d, tt in self.static_mappings.items():
                if d not in self.pp:
                    continue
                try:
                    self._pp_to_tt[d.as_posix()] = self._pp_to_tt[
                        d.as_posix()].union(tt)
                except KeyError:
                    self._pp_to_tt[d.as_posix()] = set(tt)
        except KeyError:
            return []
        if prd.as_posix() not in self._pp_to_tt:
            return []
        return self._pp_to_tt[prd.as_posix()]


class Analysis:
    """
    An Analysis of the modifications in a watched directory is returned
    by the updated-method of a snapshot which compares two snapshots for
    modifications and determines from that which test modules should be
    run.
    """

    def __init__(self) -> None:
        self.mod_tt = set()  # type: set[Path]
        self.mod_pp = dict()  # type: dict[str, set[Path]]

    def __iter__(self) -> Iterator[Path]:
        return (tm for tm in self.tt)

    def __len__(self) -> int:
        return len(self.tt)

    def pop(self) -> Path:
        return self.tt.pop()

    @property
    def tt(self) -> set[Path]:
        try:
            return self._tt
        except AttributeError:
            self._tt = set()  # type: set[Path]
            self._tt = self._tt.union(t for t in self.mod_tt)
            for ptm in self.mod_pp.values():
                self._tt = self._tt.union(t for t in ptm)
        return self._tt


class TM:
    """
    TM wraps a Path representing a test module of the watched package or
    of one of its sub-packages.
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

    @staticmethod
    def dependencies(tt: Iterable['TM']) -> list[Tuple[Path, list[Path]]]:
        return [(tm.path, [d for d in tm.production_dependencies()]) for tm in tt]


mp_pool = None  # type: None|Pool


def dep_gen(tm: TM) -> Tuple[Path, list[Path]]:
    return tm.path, [p for p in tm.production_dependencies()]


def parallel_dep_gen(tt: Iterable[TM]) -> list[Tuple[Path, list[Path]]]:
    if mp_pool:
        return mp_pool.map(dep_gen, tt)
    return []


def run_tests(
    pool: Pool, dir: Dir, tt: Iterable[Path]
) -> Tuple[list[str], dict[str, str]]:
    rr = pool.map(dir.run_test_module, tt)
    ss = []  # type: list[str]
    ee = dict()  # type: dict[str,str]
    for r in rr:
        if len(r[0]):
            ss.extend(r[0])
        if len(r[1]):
            ee.update(r[1])
    return ss, ee


def dbg_run(dir: Dir, pool: Pool, tui: TUI, frq: float) -> bool:
    analysis = dir.test_modules_to_run()  # uses also the pool
    args = Args(
        frq=frq,
        tm_out=dir.timeout,
        ignore_pkg=dir._ignore_packages,
        ignore_mdl=dir._ignore_modules,
        mappings=dict()
    )
    if len(analysis):
        start = datetime.now()
        ss, ee = run_tests(pool, dir, analysis)
        elapsed = (datetime.now() - start).total_seconds()
        tui.print_summary(ss, round(elapsed, 3), len(ee) > 0)
        tui.print_args(args)
        tui.print_analysis(
            (str(tm) for tm in analysis.mod_tt),
            dict((p, (str(t) for t in ttm))
                 for p, ttm in analysis.mod_pp.items())
        )
    else:
        tui.print_summary([], False)
        tui.print_args(args)
        tui.write_line('no tests to run')
    try:
        input('\npress enter for the next tests-run')
    except EOFError:
        return True
    return False


def run_modules(
    pool: Pool, dir: Dir, tt: Iterable[Path], tui: TUI, first: bool, frq: float
) -> bool:
    if len(tt):
        if first:
            first = False
        start = datetime.now()
        ss, ee = run_tests(pool, dir, tt)
        elapsed = (datetime.now() - start).total_seconds()
        parsed = tui.print_summary(ss, round(elapsed, 3), len(ee) > 0)
        if len(ee):
            tui.print_failed_modules(ee)
        if len(parsed):
            tui.print_suites(parsed)
        tui.print_buttons()
    elif first:
        first = False
        tui.print_summary([], 0.000)
        tui.print_buttons()
    time.sleep(frq)
    return first


def watcher(
    dir: Dir, 
    should_quite: Queue, 
    frq: float,
    dbg: bool
):
    tui = TUI()
    first = True
    with multiprocessing.Pool() as pool:
        global mp_pool
        mp_pool = pool
        dir._dep_gen = parallel_dep_gen
        while True:
            try:
                should_quite.get(False)
            except Empty:
                pass
            else:
                break
            try:
                c = tui.inp.get(False)
            except Empty:
                pass
            else:
                if c == 'q':
                    break
                if c == 'r':
                    first = run_modules(pool, dir,
                        [tm.path for tm in dir.test_modules()],
                        tui, first, frq
                    )
                    continue
                if c == 'a':
                    tui.about()
                    tui.print_buttons()
                    continue
            if dbg:
                if dbg_run(dir, pool, tui, frq):
                    break
                continue
            tt = dir.test_modules_to_run()  # uses also the pool
            first = run_modules(pool, dir, tt, tui, first, frq)
        tui.restore()
        print('\ntddflow: gracefully stopped\n')
