import re

from rex import DIGIT, char_cls, seq

hexdigit = r"[0-9a-fA-F]"
uuid_pattern = re.compile(
    rf"{hexdigit}{{8}}-{hexdigit}{{4}}-{hexdigit}{{4}}-{hexdigit}{{4}}-{hexdigit}{{12}}"
)
print(uuid_pattern.fullmatch("01234567-89ab-cdef-0123-456789abcdef"))

hexdigit = DIGIT | char_cls("a-fA-F")
uuid_pattern = seq(
    hexdigit[8], "-", hexdigit[4], "-", hexdigit[4], "-", hexdigit[4], "-", hexdigit[12]
)
print(uuid_pattern.fullmatch("01234567-89ab-cdef-0123-456789abcdef"))
