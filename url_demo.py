from rex.core import DIGIT, END, START, WORD, capture_groups, char_cls, opt

http_url_pattern = capture_groups(
    scheme="http" + opt("s") + "://",
    domain_name=((WORD | DIGIT | "-")[1:] + ".")[1:] + WORD[2:63],
    port=opt(":" + DIGIT[1:5]),
    path=opt(("/" + char_cls("?#", negate=True)[:])),
    query=opt("?" + (WORD | DIGIT | char_cls("=&%+.-_"))[1:]),
    fragment=opt("#" + (WORD | DIGIT | char_cls("=&%+.-_"))[1:]),
)
http_url_pattern = START + http_url_pattern + END
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
