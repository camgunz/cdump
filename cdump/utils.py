def snakeify(s):
    return ''.join([
        f'_{c.lower()}' if c.isupper() and n > 0 else c.lower()
        for n, c in enumerate(s)
    ])

def build_id_generator():
    id = 1
    while True:
        yield id
        id += 1
