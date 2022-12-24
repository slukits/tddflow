# gounit

Oh my, why an other testing framework?  Because implementing a testing
framework is an excellent exercise to get into a language.  Following:

- beautiful is better then ugly (Tim Peters)
- easy things should be easy, and hard things possible (Larry Wall)
- The more often a message with the same content is received the less
  information it contains (Claude Shannon)
- Design for the common case
- Don't Repeat Yourself
- Keep It Simple Stupid

the basic example of python's unittest module...

```py
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
```

... could become:

```py
from tddflow import run, T

class AString: 

    def can_be_capitalized(self, t: T):
        t.equal('foo'.upper(), 'FOO')

    def _a_helper_function(self):
        pass

    def can_determine_if_it_is_upper_case(self, t: T):
        t.truthy('FOO'.isupper())
        t.falsy('Foo'.isupper())

    def can_be_split_into_a_list_of_strings_at_spaces(self, t: T):
        s = 'hello world'
        t.equal(s.split(), ['hello', 'world'])

    def split_fails_if_a_given_separator_is_not_a_string(self, t: T):
        t.raises(lambda: s.split(2), TypeError)

if __name__ == '__main__':
    run(AString)
```

Not repeating eight times the word 'test' or four times the word
'assert'.  By factoring features for assertion and test control flow out
from the test suite in its own type (inspired by the Go testing
framework) cluttering of the test suite's namespace is avoided, no need
for inheritance, no need for uppercase methods, no need for "marking"
tests; i.e. noise through repetition is down to a minimum while our IDE
will still offer us the T-API because of the type hinting.

To make this little exercise (more) useful we want to add also a tddflow
command

```
    python -m tddflow
```

which should watch the modules of the package it was executed in
together with its sub-packages for modifications on test or production
modules.  Is a test module modified it should be automatically executed
and the result of the test run should be reported.  As well as all test
modules importing absolute a modified production module should be
executes on its modification.  If all tests succeed we get the "green
bar" if not we get the "red bar" and failed tests are reported.  It also
should report "logging tests", i.e. if a test is executed containing a
line

    t.log(type(interesting_value))

it will report the test with the logged text which comes in handy in
my experience.

Kent Beck writes in "Test-Driven Development By Example": "Driving a
testing tool using the testing tool itself to run the tests may seem a
bit like performing brain surgery on yourself." Doesn't that sound like
fun?  [Tag along](https://github.com/slukits/tddflow/blob/main/01_ran.md)
if you feel like it.
