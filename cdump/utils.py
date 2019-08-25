def joined(s, l):
    return s.join(l)


def concatenated(l):
    return joined('', l)


def paired(s, a, b):
    return joined(s, [str(a), str(b)])


def surrounded(c, s):
    return paired(s, c, c)


def snake_case(s):
    return concatenated([
        concatenated(['_', c.lower()]) if c.isupper() and n > 0 else c.lower()
        for n, c in enumerate(s)
    ])


def single_quoted(x):
    return surrounded("'", x) if isinstance(x, str) else x


def double_quoted(x):
    return surrounded('"', x) if isinstance(x, str) else x


def comma_separated(l):
    return joined(', ', map(str, l))


def space_separated(l):
    return joined(' ', map(str, l))


def intattr(node, attr_name):
    attr = node.get(attr_name)
    if not attr:
        return None
    return int(attr, 10)


def elemstr(el):
    attrs = space_separated([
        paired('=', attr_name, double_quoted(attr_value))
        for attr_name, attr_value in el.items()
    ])
    return f'<{el.tag} {attrs}>'
