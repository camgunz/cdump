from decimal import Decimal
from collections import OrderedDict


def quote(x):
    return f"'{x}'" if isinstance(x, str) else x


def pj(s, x, y):
    return f'{x}{s}{y}'


def csl(l):
    return ', '.join(map(str, l))


def cslq(l):
    return csl(map(quote, l))


def cslp(s, p):
    return csl([pj(s, x, y) for x, y in p])


class CObject:

    __slots__ = ('definitions',)

    def __init__(self, definitions):
        self.definitions = definitions

    def __repr__(self):
        return f'{self.type_name}({self.attr_map_string})'

    def __str__(self):
        return repr(self)

    @property
    def type_name(self):
        return type(self).__name__.lower()

    @property
    def attr_names(self):
        return self.__slots__

    @property
    def attrs(self):
        return [getattr(self, name) for name in self.attr_names]

    @property
    def attr_database_types(self):
        for attr_name, attr in self.attr_map.items():
            if attr is None:
                yield 'NULL'
            elif attr_name == 'name':
                yield 'TEXT UNIQUE'
            elif isinstance(attr, (bool, int)):
                yield 'INTEGER'
            elif isinstance(attr, (float, Decimal)):
                yield 'REAL'
            elif isinstance(attr, str):
                yield 'TEXT'
            elif isinstance(attr, bytes):
                yield 'BLOB'
            elif isinstance(attr, Reference):
                continue
            else:
                raise TypeError(f'{attr_name} ({attr}) has unconvertible type')

    @property
    def attr_references(self):
        for attr_name, attr in self._attr_Map.items():
            if not isinstance(attr, Reference):
                continue
            field_name, ref = attr_name, attr
            definition = self.defs[ref.name]
                f'FOREIGN KEY ({field_name}) REFERENCES {

    @property
    def attr_column_defs(self):
        return [pj(' ', name, type) for name, type in zip(
            self.attr_names,
            self.attr_database_types
        )]

    @property
    def attr_map(self):
        return OrderedDict(zip(self.attr_names, self.attrs))

    @property
    def attr_map_string(self):
        return cslp('=', self.attr_map.items())

    def apply_modifiers(self, modifiers):
        obj = self
        for modifier in modifiers:
            if modifier == 'const':
                obj = Const(obj)
            elif modifier == 'pointer':
                obj = Pointer(obj)
        return obj

    def get_reference(self):
        return self

    def get_modified_reference(self, modifiers):
        return self.get_reference().apply_modifiers(modifiers)

    def create_database_table(self, cursor):
        print(
            f'CREATE TABLE IF NOT EXISTS {self.type_name}'
            f'  ({csl(self.attr_column_defs)})'
        )
        cursor.execute(
            f'CREATE TABLE IF NOT EXISTS {self.type_name}'
            f'  ({csl(self.attr_column_defs)})'
        )

    def write_to_database(self, cursor):
        cursor.execute(
            f'INSERT INTO {self.type_name} ({cslq(self.attr_names)})'
            f'  VALUES ({cslq(self.attrs)})'
        )


class ReferenceableCObject(CObject):

    def get_reference(self):
        name = getattr(self, 'name', None)
        if name is None:
            return self
        return Reference(type(self), getattr(self, 'name'))


class Array(CObject):

    __slots__ = ('definitions', 'element_type', 'min_size', 'max_size')

    def __init__(self, definitions, element_type, min_size, max_size):
        super().__init__(definitions)
        self.element_type = element_type
        self.min_size = min_size
        self.max_size = max_size


class Builtin(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'size', 'alignment')

    def __init__(self, definitions, name, size, alignment):
        super().__init__(definitions)
        self.name = name
        self.size = size
        self.alignment = alignment


class Const(CObject):

    __slots__ = ('definitions', 'type',)

    def __init__(self, definitions, type):
        super().__init__(definitions)
        self.type = type


class Enumeration(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'values')

    def __init__(self, definitions, name, values):
        super().__init__(definitions)
        self.name = name
        self.values = values


class EnumerationValue(CObject):

    __slots__ = ('definitions', 'name', 'value')

    def __init__(self, definitions, name, value):
        super().__init__(definitions)
        self.name = name
        self.value = value


class Field(CObject):

    __slots__ = ('definitions', 'name', 'type')

    def __init__(self, definitions, name, type):
        super().__init__(definitions)
        self.name = name
        self.type = type


class Function(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'parameters', 'return_type')

    def __init__(self, definitions, name, parameters, return_type):
        super().__init__(definitions)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type


class FunctionType(ReferenceableCObject):

    __slots__ = ('definitions', 'parameters', 'return_type')

    def __init__(self, definitions, parameters, return_type):
        super().__init__(definitions)
        self.parameters = parameters
        self.return_type = return_type


class Parameter(CObject):

    __slots__ = ('definitions', 'name', 'type')

    def __init__(self, definitions, name, type):
        super().__init__(definitions)
        self.name = name
        self.type = type


class AnonymousParameter(CObject):

    __slots__ = ('definitions', 'type',)

    def __init__(self, definitions, type):
        super().__init__(definitions)
        self.type = type


class Pointer(ReferenceableCObject):

    __slots__ = ('definitions', 'type',)

    def __init__(self, definitions, type):
        super().__init__(definitions)
        self.type = type


class Reference(CObject):

    __slots__ = ('definitions', 'type', 'name',)

    def __init__(self, definitions, type, name):
        super().__init__(definitions)
        self.type = type
        self.name = name

class SelfReference(CObject):

    __slots__ = ('definitions',)


class Struct(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'members')

    def __init__(self, definitions, name, members=None):
        super().__init__(definitions)
        self.name = name
        self.members = members or []


class Typedef(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'type')

    def __init__(self, definitions, name, type):
        super().__init__(definitions)
        self.name = name
        self.type = type


class Unimplemented(CObject):

    __slots__ = ('definitions',)


class Union(ReferenceableCObject):

    __slots__ = ('definitions', 'name', 'members')

    def __init__(self, definitions, name, members):
        super().__init__(definitions)
        self.name = name
        self.members = members
