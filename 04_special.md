# Special Methods of Test Suites

The following test-methods should be treated special by tddflow:

- *init* is executed before any other suite method is executed.
- *setup* is executed before each test
- *tear_down* is executed after each test
- *finalize* is executed after all tests have been executed.

If init fails the whole suite fails and no tests are executed.  If setup
fails following test is not executed.  But tear_down is always executed
even if setup failed.  Hence it must be considered in tear_down
implementations that setup operations like obtaining a database
connection have not succeeded.  To support these considerations provided
T instance of a tear_down call has the property t.has_setup_passed.  