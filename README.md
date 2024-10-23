# REX: Regular Expression Library for Humans

> [!WARNING]
>
> This tool is in a very early stage and under heavy developments and should not be used in production code.

## Examples:

Let's see a comparison between the standard `re` module and `rex`:

With the built-in `re` module:

```python
import re

hexdigit = r"[0-9a-fA-F]"
uuid_pattern = re.compile(
    rf"{hexdigit}{{8}}-{hexdigit}{{4}}-{hexdigit}{{4}}-{hexdigit}{{4}}-{hexdigit}{{12}}"
)

print(uuid_pattern.fullmatch("01234567-89ab-cdef-0123-456789abcdef"))

```

With `rex`:

```python
from rex import DIGIT, char_cls, seq

hexdigit = DIGIT | char_cls("a-fA-F")
uuid_pattern = seq(
    hexdigit[8], "-", hexdigit[4], "-", hexdigit[4], "-", hexdigit[4], "-", hexdigit[12]
)

print(uuid_pattern.fullmatch("01234567-89ab-cdef-0123-456789abcdef"))
```

## Installation:

```bash
pip install git+https://github.com/Microwave-WYB/rex.git
```

## Usage:

### Working with `rex.Pattern`:

Here's the basic usage of `rex.Pattern`:

```python
from rex import lit

# Create a pattern object with literal string "hello"
pattern = lit("hello")  # r"hello"

pattern.one_or_more()  # r"(?:hello)+"

pattern.zero_or_more()  # r"(?:hello)*"

pattern.n_or_more(3)  # r"(?:hello){3,}"

pattern.optional()  # r"(?:hello)?"

pattern.repeat(3)  # r"(?:hello){3}"

pattern.repeat(3, 5)  # r"(?:hello){3,5}"

pattern.capture("greet")  # r"(?P<greet>hello)"
```

You can also use all methods in `re.Pattern` with `rex.Pattern`:

```python
pattern.compile()  # re.compile(r"hello")
pattern.match("hello")  # <re.Match object; span=(0, 5), match='hello'>
pattern.fullmatch("hello")  # <re.Match object; span=(0, 5), match='hello'>
pattern.findall("hello")  # ['hello']
list(pattern.finditer("hello"))  # [<re.Match object; span=(0, 5), match='hello'>]
pattern.split("hello")  # ['', '']
pattern.sub("hello", "world")  # 'world'
pattern.subn("hello", "world")  # ('world', 1)
pattern.flags  # 0
pattern.groups  # 0
pattern.groupindex  # {}
```

### Using operators:

You can use `+` for concatenation and `|` for alternation:

```python
from rex import lit

ab = lit("a") + lit("b")
a_or_b = lit("a") | lit("b")
```

The operators also support directly operating on strings. If any of the operands is a pattern, the result will be a pattern:

```python
ab = lit("a") + "b"  # Identical to lit("a") + lit("b")
a_or_b = "a" | lit("b")  # Identical to lit("a") | lit("b")
```

You can also use `__getitem__` for repeating patterns:

```python
# "hello" repeated 3 times
pattern[3]  # r"(?:hello){3}"

# "hello" repeated 3 to 5 times
pattern[3, 5]  # r"(?:hello){3,5}"

# "hello" repeated 0-3 times
pattern[:3]  # r"(?:hello){,3}"

# "hello" repeated 3 or more times
pattern[3:]  # r"(?:hello){3,}"

# "hello" repeated one or more times
pattern[1:]  # r"(?:hello)+"

# "hello" repeated zero or more times
pattern[:]  # r"(?:hello)*"

# optional "hello"
pattern[:1]  # r"(?:hello)?"
```

### Predefined Patterns:

```python
from rex import DIGIT, END, START, WS, WORD

ten_digits = DIGIT[10]

full_string_ten_digits = START + ten_digits + END

ten_words = WORD[10]

words_with_spaces = (WORD | WS)[10]
```

### Factory Functions:

You can use a set of factory functions to create patterns:

```python
from rex import lit, seq, opt, char_cls, capture_groups

# literal "hello"
lit("hello")

# "hello" followed by "world"
seq("hello", "world")
# or
lit("hello") + lit("world")

# optional "hello"
opt("hello")
# or
lit("hello").optional()

# hex digits defined by character class
char_cls("0-9a-fA-F")

# capture groups
greeting_pattern = capture_groups(greet="Hello", name=WORLD.one_or_more(), end="!")
greeting_pattern.match("Hello, world!").groupdict()
# {'greet': 'Hello', 'name': 'world', 'end': '!'}
```
