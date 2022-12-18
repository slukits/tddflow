# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


import ast
import os
from typing import Generator, Tuple
from pathlib import Path
import sys


class DirNoPackage(Exception): pass


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
        for node in ast.iter_child_nodes(ast.parse(self.path.read_text())):
            if isinstance(node, ast.ImportFrom):
                dep, found = self._import_to_module(node.module)
                if found: # may be a module imported into dep
                    for name in node.names:
                        d, found = self._resolve_from_import(
                            dep, name.name)
                        if found:
                            yield d
                        else:
                            yield dep
                    continue
                if not self._is_package_import(node.module):
                    continue
                for name in node.names:
                    dep, found = self._import_to_module(
                        node.module + '.' + name.name)
                    if found:
                        yield dep
                continue
            if isinstance(node, ast.Import):
                for name in node.names:
                    dep, found = self._import_to_module(name.name)
                    if found:
                        yield dep

    def _resolve_from_import(
        self, mod: Path, imp: str
    ) -> Tuple[Path|None, bool]:
        for node in ast.iter_child_nodes(ast.parse(mod.read_text())):
            if isinstance(node, ast.ImportFrom):
                dep, found = self._import_to_module(node.module)
                if found:
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
                    dep, found = self._import_to_module(
                        node.module + '.' + name.name)
                    if found:
                        return dep, True
                    return None, False
                continue
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name != imp:
                        continue
                    dep, found = self._import_to_module(name.name, mod)
                    if found:
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
        self, module_string: str, mod: Path|None = None
    ) -> Tuple[Path|None, bool]:
        rel_path = Path(module_string.replace(".", os.sep)+".py")
        abs_path = self.watched.root_package.parent.joinpath(rel_path)
        if abs_path.exists():
            return abs_path, True
        if not mod:
            mod = self.path
        abs_path = mod.parent.joinpath(rel_path)
        if abs_path.exists():
            return abs_path, True
        return None, False


class PM:
    """
    PM represents a production module of a watched sub-package.
    """

    def __init__(self, watched: 'Dir', p: Path) -> None:
        self.path = p
        self.watched = watched

    def __str__(self) -> str:
        return str(self.path)


class Pkg:
    """
    Pkg represents a subpackage in a watched package's root package.
    """

    def __init__(self, d: Path) -> None:
        self.dir = d

    def __str__(self) -> str:
        return str(self.dir)


class Dir:
    """
    Dir represents a directory from pyunit's points of and may be
    passed to the watcher-modules main function in order to be watched
    for changes and executing test-runs appropriately.
    """

    def __init__(self, dir: str) -> None:
        """
        init initializes a watched directory and fails if directory
        is not a package.  Note a watched dir will in its proceedings
        ignore the '__pycache__'-package and '__init__.py'-module.
        """
        self.dir = Path(dir)  # type: Path
        if not self.is_package(self.dir):
            raise DirNoPackage(f"'{dir}' is not a package")
        self._ignore_packages = ['__pycache__']
        self._ignore_modules = ['__init__.py']
        root = self.root_package
        if str(root.parent) not in sys.path:
            sys.path.insert(0, str(root.parent))

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

    def sub_packages(self) -> Generator[Pkg, None, None]:
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

    def test_modules(self) -> Generator[TM, None, None]:
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

    def snapshot(self) -> 'Snapshot':
        """
        snapshot generates a state of the watched package and its
        sub-packages at the time it is called.  snapshots make the
        watched package and its sub-packages comparable for change and
        map production modules to test modules which import them.
        """
        pass


class Snapshot: pass