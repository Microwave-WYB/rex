import re
from typing import ClassVar, Final, final


@final
class Pattern:
    _GROUP_CHECK: ClassVar[re.Pattern] = re.compile(r"^\([^()]*(?:\([^()]*\)[^()]*)*\)$")
    _NON_CAPTURING_GROUP_CHECK: ClassVar[re.Pattern] = re.compile(r"^\(\?:")

    def __init__(self, pattern: "str | Pattern") -> None:
        self._pattern = str(pattern)

        # Bind re.Pattern methods to the Pattern object
        self.search = self.compile().search
        self.match = self.compile().match
        self.fullmatch = self.compile().fullmatch
        self.findall = self.compile().findall
        self.finditer = self.compile().finditer
        self.split = self.compile().split
        self.sub = self.compile().sub
        self.subn = self.compile().subn
        self.flags = self.compile().flags
        self.groups = self.compile().groups
        self.groupindex = self.compile().groupindex

    def __str__(self) -> str:
        return self._pattern

    def __repr__(self) -> str:
        return f"Pattern({self._pattern!r})"

    @property
    def is_grouped(self) -> bool:
        """
        >>> Pattern("a").is_grouped
        False
        >>> Pattern("(a)").is_grouped
        True
        >>> Pattern("[a]").is_grouped
        False
        """
        return bool(self._GROUP_CHECK.match(self._pattern))

    def optional(self) -> "Pattern":
        """
        Make the pattern optional by appending a question mark.
        >>> Pattern("a").optional()
        Pattern('(?:a)?')
        """
        return Pattern(f"{self.precedence()}?")

    def one_or_more(self) -> "Pattern":
        """
        Match one or more occurrences of the pattern.
        >>> Pattern("a").one_or_more()
        Pattern('(?:a)+')
        """
        return Pattern(f"{self.precedence()}+")

    def zero_or_more(self) -> "Pattern":
        """
        Match zero or more occurrences of the pattern.
        >>> Pattern("a").zero_or_more()
        Pattern('(?:a)*')
        """
        return Pattern(f"{self.precedence()}*")

    def n_or_more(self, n: int) -> "Pattern":
        """
        Match n or more occurrences of the pattern.
        >>> Pattern("a").n_or_more(2)
        Pattern('(?:a){2,}')
        """
        return Pattern(f"{self.precedence()}{{{n},}}")

    def repeat(self, /, n: int, m: int | None = None) -> "Pattern":
        """
        Match n or n-m occurrences of the pattern.
        >>> Pattern("a").repeat(2)
        Pattern('(?:a){2}')
        """
        if m is None:
            return Pattern(f"{self.precedence()}{{{n}}}")
        return Pattern(f"{self.precedence()}{{{n},{m}}}")

    def capture(self, name: str | None = None) -> "Pattern":
        """
        Create a capture group from the pattern. If name is provided, creates a named capture group.
        If the pattern is already in a non-capturing group, converts it to a capturing group.
        If the pattern is already in a capturing group, returns it as is.

        >>> Pattern("abc").capture()
        Pattern('(abc)')
        >>> Pattern("(?:abc)").capture()
        Pattern('(abc)')
        >>> Pattern("(abc)").capture()
        Pattern('(abc)')
        >>> Pattern("abc").capture("word")
        Pattern('(?P<word>abc)')
        >>> Pattern("(?:abc)").capture("word")
        Pattern('(?P<word>abc)')
        >>> Pattern("[0-9]+").capture("number")
        Pattern('(?P<number>[0-9]+)')
        """
        pattern = self._pattern

        match (
            self.is_grouped,
            bool(self._NON_CAPTURING_GROUP_CHECK.match(pattern)),
            name is not None,
        ):
            # Already in capturing group, no name provided
            case (True, False, False):
                return Pattern(pattern)

            # Already in capturing group, convert to named
            case (True, False, True):
                return Pattern(f"(?P<{name}>{pattern[1:-1]})")

            # In non-capturing group, convert to regular capture
            case (True, True, False):
                return Pattern(f"({pattern[3:-1]})")

            # In non-capturing group, convert to named capture
            case (True, True, True):
                return Pattern(f"(?P<{name}>{pattern[3:-1]})")

            # Not in any group, add regular capture
            case (False, _, False):
                return Pattern(f"({pattern})")

            # Not in any group, add named capture
            case (False, _, True):
                return Pattern(f"(?P<{name}>{pattern})")

    def precedence(self) -> "Pattern":
        """
        Explicitly group the pattern using non-capturing parentheses (?:) for precedence control.
        We use ?: to make the group non-capturing.
        >>> Pattern("a").precedence()
        Pattern('(?:a)')
        """
        if not self.is_grouped:
            return Pattern(f"(?:{self})")
        return Pattern(self)

    def then(self, /, other: "Pattern") -> "Pattern":
        """
        Concatenate two patterns.
        >>> Pattern("a").then(Pattern("b"))
        Pattern('ab')
        """
        return Pattern(f"{self}{other}")

    def or_(self, /, other: "Pattern") -> "Pattern":
        """
        Union two patterns.
        >>> Pattern("a").or_(Pattern("b"))
        Pattern('(?:a)|(?:b)')
        """
        return Pattern(f"{self.precedence()}|{other.precedence()}")

    def compile(self) -> re.Pattern:
        """Compile the pattern to a re.Pattern object."""
        return re.compile(str(self))

    def __add__(self, other: "Pattern") -> "Pattern":
        """
        >>> Pattern("a") + Pattern("b")
        Pattern('ab')
        """
        return self.then(other)

    def __or__(self, other: "Pattern") -> "Pattern":
        """
        >>> Pattern("a") | Pattern("b")
        Pattern('(?:a)|(?:b)')
        """
        return self.or_(other)

    def __mul__(self, n: int | tuple[int, int]) -> "Pattern":
        """
        >>> Pattern("a") * 2
        Pattern('(?:a){2}')
        """
        if isinstance(n, int):
            return self.repeat(n)
        if len(n) != 2:
            raise ValueError("Expected a single integer or a tuple of two integers.")
        if not all(isinstance(i, int) for i in n):
            raise ValueError("Expected integers.")
        return self.repeat(*n)


def lit(s: str) -> Pattern:
    """
    Create a literal pattern, escaping special regex characters.
    >>> lit("a")
    Pattern('a')
    """
    return Pattern(re.escape(s))


def char_class(*args: str | Pattern, negate: bool = False) -> Pattern:
    """
    Create a character set from a string.
    >>> char_class("a", "b", "c")
    Pattern('[abc]')
    >>> char_class("abc", "def", negate=True)
    Pattern('[^abcdef]')
    """
    return Pattern(("[^" if negate else "[") + "".join(str(arg) for arg in args) + "]")


def concat(*args: str | Pattern) -> Pattern:
    """
    Concatenate multiple patterns. Strings are escaped and converted to literal patterns.
    >>> concat("a", "b", "c")
    Pattern('abc')
    """
    pattern = Pattern("")
    for arg in args:
        if isinstance(arg, str):
            arg = lit(arg)
        pattern += arg
    return pattern


def create_parser(**kwargs: Pattern) -> Pattern:
    """Create a parser pattern from a dictionary of patterns."""
    pattern = Pattern("")
    for key, value in kwargs.items():
        pattern += value.capture(key)
    return pattern


# Commonly used patterns
WORD: Final[Pattern] = Pattern(r"\w")
WORD_BOUNDARY: Final[Pattern] = Pattern(r"\b")
NON_WORD_BOUNDARY: Final[Pattern] = Pattern(r"\B")
WS: Final[Pattern] = Pattern(r"\s")
DIGIT: Final[Pattern] = Pattern(r"\d")
START: Final[Pattern] = Pattern("^")
END: Final[Pattern] = Pattern("$")
ALPHAS: Final[Pattern] = Pattern(r"[a-zA-Z]")
UPPER: Final[Pattern] = Pattern(r"[A-Z]")
LOWER: Final[Pattern] = Pattern(r"[a-z]")
ALPHANUMS: Final[Pattern] = Pattern(r"[a-zA-Z0-9]")
