from collections import OrderedDict

from .utils import comma_separated, paired, snake_case


class CObject:

    __slots__ = ()

    def __repr__(self):
        return f'{self.type_name}({self.attr_map_string})'

    def __str__(self):
        return repr(self)

    @property
    def attr_names(self):
        return self.__slots__

    @property
    def type_name(self):
        return snake_case(type(self).__name__)

    @property
    def attrs(self):
        return [getattr(self, name) for name in self.attr_names]

    @property
    def attr_map(self):
        return OrderedDict(zip(self.attr_names, self.attrs))

    @property
    def attr_map_string(self):
        return comma_separated([
            paired('=', *x) for x in self.attr_map.items()
        ])

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

    def to_dict(self):
        od = OrderedDict([('obj_type', self.type_name)])
        for attr_name, attr in zip(self.attr_names, self.attrs):
            if isinstance(attr, CObject):
                od[attr_name] = attr.to_dict()
            elif isinstance(attr, list):
                od[attr_name] = [
                    x.to_dict() if isinstance(x, CObject) else x
                    for x in attr
                ]
            else:
                od[attr_name] = attr
        return od


class ReferenceableCObject(CObject):

    def get_reference(self):
        name = getattr(self, 'name', None)
        if name is None:
            return self
        return Reference(type(self), getattr(self, 'name'))


class Array(CObject):

    __slots__ = ('element_type', 'min_size', 'max_size')

    def __init__(self, element_type, min_size, max_size):
        self.element_type = element_type
        self.min_size = min_size
        self.max_size = max_size


class Builtin(ReferenceableCObject):

    __slots__ = ('name', 'size', 'alignment')

    def __init__(self, name, size, alignment):
        self.name = name
        self.size = size
        self.alignment = alignment


class Const(CObject):

    __slots__ = ('type',)

    def __init__(self, type):
        self.type = type


class Enumeration(ReferenceableCObject):

    __slots__ = ('name', 'values')

    def __init__(self, name, values):
        self.name = name
        self.values = values


class EnumerationValue(CObject):

    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Field(CObject):

    __slots__ = ('name', 'type')

    def __init__(self, name, type):
        self.name = name
        self.type = type


class Function(ReferenceableCObject):

    __slots__ = ('name', 'parameters', 'return_type')

    def __init__(self, name, parameters, return_type):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type


class FunctionType(ReferenceableCObject):

    __slots__ = ('parameters', 'return_type')

    def __init__(self, parameters, return_type):
        self.parameters = parameters
        self.return_type = return_type


class Parameter(CObject):

    __slots__ = ('name', 'type')

    def __init__(self, name, type):
        self.name = name
        self.type = type


class AnonymousParameter(CObject):

    __slots__ = ('type',)

    def __init__(self, type):
        self.type = type


class Pointer(ReferenceableCObject):

    __slots__ = ('type',)

    def __init__(self, type):
        self.type = type


class Reference(CObject):

    __slots__ = ('type', 'name',)

    def __init__(self, type, name):
        self.type = snake_case(type.__name__)
        self.name = name


class SelfReference(CObject):

    __slots__ = ()


class Struct(ReferenceableCObject):

    __slots__ = ('name', 'members')

    def __init__(self, name, members=None):
        self.name = name
        self.members = members or []


class Typedef(ReferenceableCObject):

    __slots__ = ('name', 'type')

    def __init__(self, name, type):
        self.name = name
        self.type = type


class Unimplemented(CObject):

    __slots__ = ()


class Union(ReferenceableCObject):

    __slots__ = ('name', 'members')

    def __init__(self, name, members):
        self.name = name
        self.members = members
