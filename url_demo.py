from rex.core import DIGIT, END, START, WORD, capture_groups, char_cls, lit

http_url_pattern = capture_groups(
    scheme=START + lit("http") + lit("s").optional() + lit("://"),
    domain_name=((WORD | DIGIT | lit("-")).one_or_more() + lit(".")).one_or_more()
    + WORD.repeat(2, 63),
    port=(lit(":") + DIGIT.repeat(1, 5)).optional(),
    path=(lit("/") + char_cls("?#", negate=True).zero_or_more()).optional(),
    query=(lit("?") + (WORD | DIGIT | char_cls("=&%+.-_")).one_or_more()).optional(),
    fragment=(lit("#") + (WORD | DIGIT | char_cls("=&%+.-_")).one_or_more()).optional() + END,
)
print(http_url_pattern)


examples = [
    "http://www.google.com",
    "https://www.google.com?q=hello",
    "https://www.google.com:8080?q=hello#world",
    "https://www.google.com:8080/api/search/v1?q=hello#world",
    "https://www.google.com:8080?q=hello+world#1",
]

for example in examples:
    print(example)
    match = http_url_pattern.match(example)
    if match is not None:
        print(match.groupdict())
    else:
        print("No match")
    print()
