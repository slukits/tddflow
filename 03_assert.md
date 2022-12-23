# More On Assertions

To test drive the watcher implementation the assert_.T type with the
only assertion 'truthy' was already extended by the methods

- failed(bool[, str]) to flag a test as failed but continuing its 
  execution
- fatal([str]) to flag a test as failed and stop its execution
- fatal_if_not(bool[, str]) to fail and stop a test if given 
  argument doesn't evaluate to true.  Since all asserting methods
  return True in case of success and False otherwise fatal_if_not
  can be used abort a test in case a specific assertion fails.
- raises(Callable, Type, str) asserts if given callable raises an
  exception of given type
- log(str) logs given string as output to the test it was called
  in.  Since the watcher reports also logging tests this is an 
  easy and quick way to investigate a return or variable value.

While any assertion is transformable into a True/False statement
"expecting 'False' to be truthy" is not a very useful error message
most of the time.  To be more expressive a few more specific assertion
should be added:

- falsy(bool[, str]) fails a test iff given bool is truthy
- in_(Any, Iterable[Any][, str]) Note an [argument] argument is 
  optional while collection[type-info] specifies a collection's
  element's type.  *in* fails the test if given element is not in
  given iterable.
- not_in(Any, Iterable[Any][, str]) fails the test if given element
  is in given iterable.
- is_(Any, Any) fails the test if given arguments don't have the same id
- is_not(Any, Any) fails the test if given arguments have the same id
- is_instance(Any, Any) fails the test if first argument is not an
  instance of second
- is_not_instance(Any, Any) fails the test if given first argument is an
  instance of second
- eq(Any, Any) fails the test if given arguments are not equal (!=).
- eq_str(Any, Any) fails the test if given arguments have not the
  same string representation.
- eq_repr(An, Any) fails the test if given arguments have not the
  same representation
- not_eq(Any, Any) fails the test if given arguments are equal.
- not_eq_str(Any, Any) fails the test if given arguments have the
  same string representation
- not_eq_rpr(Any, Any) fails the test if given arguments have the
  same representation.
- matched(str|bytes, Pattern) fails the test if given string or 
  bytes not matched by given pattern.
- space_match(str|bytes, ...str) fails the test if given string is
  not matched by the '\s*?'.join-ed strings whereas each variadic
  string is escaped before joining them together.
- start_matched(str|bytes, ...str) fails the test if given string
  is not matched by the '.*?'.join-ed strings whereas each 
  variadic string is escaped before joining them together. 
- not_matched(str|bytes, Pattern) fails the test if
  matched(str|bytes, Patter)

Note the idea for space and star match assertions is to make tests less
brittle if only structural aspects should be asserted, e.g. given string s

    """
    <tr>
      <td>
        the answer is 42
      </td>
    </tr>
    """

would pass the assertion

    t.star_matched(s, 'tr', 'td', '42', 'td', 'tr')

From my experience the above assertions cover the common use-cases
and allow for more useful failure messages.

Last but not least the handling of special methods like setup and
tear_down [is implemented](04_special.md).