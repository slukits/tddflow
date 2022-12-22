# Ran

If we develop a testing tool we want to be confident that it works
properly and we want to start using it as quickly as possible.  Hence
the tests of a suite should be run a falsy assertion should fail a test
and a failed test should be reported.  Making these three things work in
a minimal manner allows us to use the testing tool. 

So lets start with the behavior 

    "a suite's test methods are executed on a (suite) test run"

This is already a quite big first step.  But lets feel bold today and
see if we find something smaller along the way.  Please note I already
have implemented the tool "gounit" and I have Kent Beck's book with his
implementation suggestion lying next to me.  Hence don't expect from you
that you come up with the following proceeding as easily as it's written
down here.

Now how could the first step look like in terms of code:

```py
"""
In case the first step is to big: A called suite test has been run:

>>> s = TestSuite()
>>> s.suiteTestHasRun
False
>>> s.suite_test(None)
>>> s.suiteTestHasRun
True

A suite test is executed on a (suite) test run:

>>> from pyunit import runTests
>>> s = TestSuite()
>>> s.suiteTestHasRun
False
>>> runTests(s)
>>> s.suiteTestHasRun
True

A suite test has an T instance provided on execution:

>>> s = TestSuite()
>>> s.gotTestingTInstance
False
>>> runTests(s)
>>> s.gotTestingTInstance
True
"""
from pyunit import runTests, T


class TestSuite:

    def __init__(self):
        self.suiteTestHasRun = False
        self.gotTestingTInstance = False

    def suite_test(self, t: T):
        self.suiteTestHasRun = True
        self.gotTestingTInstance = isinstance(t, T)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

Note: we don't bother to implement a test parser and runner for single
test-functions since python has this nice doctest feature which we
leveraged above to avoid the self referential brain freeze.  See Part two
of "Test-Driven Development By Example" for a more challenging way of
implementing the first step.

To achieve a minimal useful version our test run should report a failed
truthy assertion and only a failed one.  Looking for an easy and minimal
inversive way to do black box testing the test runner was implemented to
allow to configure where the report of a test run is reported to.  This
feature will be leveraged to validate if a test run behaved expectedly.

```py
"""
A suite test fails if true assertion fails:

>>> from pyunit import runTests, Config
>>> s = TestTrueAssertion()
>>> s.failedTrueAssertion
False
>>> s.passedTrueAssertion
False
>>> runTests(s, Config(out=s.reportIO))
>>> s.failedTrueAssertion
True
>>> s.passedTrueAssertion
False

A failing suite test is reported:

>>> 'TrueAssertion' in s.reportIO.getvalue()
True
>>> 'fails_if_false' in s.reportIO.getvalue()
True
>>> 'passes_if_true' in s.reportIO.getvalue()
False
>>> s.reportIO.close()
"""

import io

from pyunit import T


class OutMock(io.StringIO):
    """
    OutMock allows to intercept and retrieve what a test run reports
    """

    def __init__(self, io_callback: callable):
        """given callable will be informed about every report-write"""
        super().__init__()
        self.__io_callback = io_callback

    def write(self, s: str) -> int:
        self.__io_callback(s)
        return super().write(s)


class TestTrueAssertion():

    def __init__(self):
        self.reportIO = OutMock(self._io_callback)
        self.failedTrueAssertion = False
        self.passedTrueAssertion = False

    def _io_callback(self, s: str):
        if 'fails_if_false' in s:
            self.failedTrueAssertion = True
        if 'passes_if_true' in s:
            self.passedTrueAssertion = True

    def fails_if_false(self, t: T):
        t.truthy(False)

    def passes_if_true(self, t: T):
        t.truthy(True)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
```


Now needs to be decided what is implemented next.  I choose the order

* [minimal reporting for TDD-cycle](02_tdd_reporting.md)
* [more sophisticated assertions and control flow](03_assert.md)
* having special methods like init, setUp, tearDown and final