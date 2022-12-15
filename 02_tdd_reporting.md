# TDD Reporting

Implement a test for the simplest non trivial behavior which fails since
it is not implemented yet.  Our watcher should detect the changed test
file, run the test file and report the failed test, i.e. show the red
bar.  Has the needed code been implemented to make the test work the
watcher should detect the changed code file and report the green bar.
Then we refactor while the bar stays green until the production code has
the desired quality and we start all over again.  A further use case is
that some information was logged in a test.  Such a test should be
reported with the logged information.  Since we want feedback as fast
as possible only tests referring to changed code should be re-run.

From the above can be derived that the watcher should automatically
control the reporting of all test-modules in a watched directory.  To
realize that the watcher must be able to collect results of test runs
and these reported results must be sufficient to generate the desired
report.

Since we already have a default reporting mode -- report nothing if all
tests pass; report the failing tests otherwise -- a new reporting mode
is needed. 

    TDD-Mode

        * test run reports its results in json format
        * reports the number of ran tests in result json
        * reports the number of failed tests in result json
        * reports names of failed tests in result json
        * flags a failed test as failed
        * reports the error messages of failed tests in result json
        * reports logged output of logging tests in result json

Having all this information available we can build the watcher

    A Watcher

        * calls a test file with --report=tdd flag
        * summarizes the number of executed tests
        * summarizes the number of failed tests
        * names summary with code directory
        * shows summary green if all tests passed
        * shows summary red if not all tests passed
        * reports suite name of first failed test
        * shows first failed test
        * shows error message of first failed test
        * shows suite name of first logging test if green
        * shows first logging test if green
        * shows first logging test's log data if green
        * runs test files concurrently

See report_test.py, pyunit_test.py and watcher_test.py for a test drive
implementation of the above.  Note the above is a sketch of a first
thought process of the next step.  When it comes to the implementation
it might be that points which appear later are easier to implement then
points which come earlier or that a point is to big and becomes two
points etc.  I will not adapt this specification sketch to the
implementation to give you a more realistic picture of my development
process.