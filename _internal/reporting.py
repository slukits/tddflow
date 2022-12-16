# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.
from dataclasses import dataclass, field
from typing import Dict, TextIO, Tuple

JSN_TEST_SUITE = "test_suite"
JSN_TESTS_COUNT = "tests_count"
JSN_FAILS_COUNT = "fails_count"
JSN_FAILS = "fails"
JSN_TEST_LOGS = "test_logs"


@dataclass
class TestAttributes:
    failed: bool = False
    logs: list[str] = field(default_factory=lambda: [])


class Report:
    """
    Report is the abstract type of which all reporting types should be
    derived.  A reporting-type r generates on a call of r.print the
    output of a suite's tests-run by processing the content of the
    *tests*-property which was filled with failing or logging tests
    during the test-run.
    """

    def __init__(self):
        """
        initializes the *tests* and *fails_count* properties for a
        suite's test run.
        """
        self.tests = dict()  # type: Dict[str:TestAttributes]
        """test stores failed or logging tests"""
        self.fails_count = 0  # type: int
        """
        _fails counts the failing tests since *tests* may also contain
        logging tests
        """

    def fail(self, name: str):
        """fail flags the test with given name as failed."""
        t = self.tests.get(name, None)
        if t is None:
            t = TestAttributes()
            self.tests[name] = t
        if t.failed:
            return
        t.failed = True
        self.fails_count += 1

    def log(self, name: str, msg: str):
        """log given message msg for test with given name."""
        t = self.tests.get(name, None)
        if t is None:
            t = TestAttributes()
            self.tests[name] = t
        t.logs.append(msg)

    def print(self, suite: str, out: TextIO):
        raise NotImplementedError(
            "pyunit: report: print not implemented")


class Default(Report):
    """
    A Report is used by a Suite instance to generate the desired output
    about a test run.
    """

    def print(self, suite: str, out: TextIO):
        if len(self.tests) == 0:
            return
        print("pyunit: failing/logging suite-tests:", file=out)
        print("{} ({}/{})".format(
            suite, len(self.tests), self.fails_count), file=out)
        for name, attrs in self.tests.items():
            print("  {}".format(name), file=out)
            for m in attrs.logs:
                print("    {}".format(m), file=out)


class TDD(Report):

    def __init__(self):
        super().__init__()
        self.test_count: int = 0

    def increase_test_count(self):
        self.test_count += 1

    def print(self, suite: str, out: TextIO):
        ll = []  # type: list[str]
        ll.append('  "{}": "{}"'.format(JSN_TEST_SUITE, suite))
        ll.append('  "{}": {}'.format(JSN_TESTS_COUNT, self.test_count))
        ll.append('  "{}": {}'.format(JSN_FAILS_COUNT, self.fails_count))
        ll.append('  "{}": [\n{}\n  ]'.format(
            JSN_FAILS,
            ",\n".join(
                [f'    "{t}"' for t, a in self.tests.items() if a.failed])
        ))
        logs = []

        for name, attrs in self.tests.items():
            if not len(attrs.logs):
                continue
            log = '    "{}": [\n      {}\n    ]'.format(
                name,
                ",\n      ".join(f'"{L}"' for L in attrs.logs)
            )
            logs.append(log)
        if len(logs):
            ll.append('  "{}": {{\n{}\n  }}'.format(
                JSN_TEST_LOGS, ",\n".join(logs)
            ))
        print('{{\n{}\n}}'.format(",\n".join(ll)), file=out)
