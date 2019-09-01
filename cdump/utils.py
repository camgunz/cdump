def join(s, l):
    return s.join(l)


def concatenate(l):
    return join('', l)


def pair(s, a, b):
    return join(s, [str(a), str(b)])


def surround(c, s):
    return pair(s, c, c)


def snake_case(s):
    return concatenate([
        concatenate(['_', c.lower()]) if c.isupper() and n > 0 else c.lower()
        for n, c in enumerate(s)
    ])


def single_quote(x):
    return surround("'", x) if isinstance(x, str) else x


def double_quote(x):
    return surround('"', x) if isinstance(x, str) else x


def comma_separate(l):
    return join(', ', map(str, l))


def space_separate(l):
    return join(' ', map(str, l))


def intattr(node, attr_name):
    attr = node.get(attr_name)
    if not attr:
        return None
    return int(attr, 10)


def elemstr(el):
    attrs = space_separate([
        pair('=', attr_name, double_quote(attr_value))
        for attr_name, attr_value in el.items()
    ])
    return f'<{el.tag} {attrs}>'


def id_gen(start=0):
    n = start
    yield n
    while True:
        n += 1
        yield n
