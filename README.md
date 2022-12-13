# gounit

Oh my, why an other testing framework?  Because implementing a testing
framework is an excellent exercise to get into a language.  Following
these jolly good ideas:

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
from pyunit import runTests, T

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
    runTests(AString)
```

Not repeating eight times the word test or four times the word assert.
By factoring features for assertion and test control flow out from the
test suite in its own type (inspired by the Go testing framework)
cluttering of the test suite's namespace is avoided, no need for
inheritance, no need for uppercase methods, no need for "marking" tests;
i.e. noise through repetition is down to a minimum while our IDE will
still offer us the T-API because of the type hinting.

Now imagine a little program which watches the directory we're working
on and always if a file whose name matches "*_test.py" is updated (yes
it's just a lot more useful to have a test file next to the module it
tests) it runs its test-suite(s) and reports the executed tests in the
following manner:

    a string
        can be capitalized
        can determine if it is upper case
        can be split into a list of strings at spaces
        split fails if a given separator is not a string

Imagine what it does to our focus if we work on a module of which we
have always an outline of its implemented behavior available.  Imagine
we choose our tests in a way that we always try to find the next most
simple yet not trivial missing behavior as our next test.  Then we not
only have an outline of the implemented behavior available but also the
thought process which led there.

Hence it looks like this little exercise has the potential to pay of.
Especially since we can build on top of an exemplary implementation of
Kent Beck from his "Test-Driven Development By Example" book.  There he
writes: "Driving a testing tool using the testing tool itself to run the
tests may seem a bit like performing brain surgery on yourself." Doesn't
that sound like fun?  [Tag along](01_ran.md) if you feel like it.