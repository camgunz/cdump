from collections import OrderedDict

from .utils import comma_separate, pair, snake_case


class CDef:

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
        return comma_separate([
            pair('=', *x) for x in self.attr_map.items()
        ])

    def to_dict(self):
        od = OrderedDict([('obj_type', self.type_name)])
        for attr_name, attr in zip(self.attr_names, self.attrs):
            if isinstance(attr, CDef):
                od[attr_name] = attr.to_dict()
            elif isinstance(attr, list):
                od[attr_name] = [
                    x.to_dict() if isinstance(x, CDef) else x
                    for x in attr
                ]
            elif isinstance(attr, OrderedDict):
                od[attr_name] = OrderedDict([
                    (k, v.to_dict() if isinstance(v, CDef) else v)
                    for k, v in attr.items()
                ])
            else:
                od[attr_name] = attr
        return od


class Array(CDef):

    __slots__ = ('element_type', 'element_count')

    def __init__(self, element_type, element_count=None):
        self.element_type = element_type
        self.element_count = element_count


class Builtin(CDef):
    pass


class Bool(Builtin):

    __slots__ = ('name', 'size', 'alignment')

    def __init__(self, name, size, alignment):
        self.name = name
        self.size = size
        self.alignment = alignment


class Integer(Builtin):

    __slots__ = ('name', 'size', 'alignment')

    def __init__(self, name, size, alignment):
        self.name = name
        self.size = size
        self.alignment = alignment


class FloatingPoint(Builtin):

    __slots__ = ('name', 'size', 'alignment')

    def __init__(self, name, size, alignment):
        self.name = name
        self.size = size
        self.alignment = alignment


class Void(Builtin):

    __slots__ = ()


class Enum(CDef):

    __slots__ = ('type', 'values')

    def __init__(self, enum_type, values):
        self.type = enum_type
        self.values = values


class Function(CDef):

    __slots__ = ('name', 'parameters', 'return_type')

    def __init__(self, name, parameters, return_type):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type


class FunctionPointer(CDef):

    __slots__ = ('parameters', 'return_type')

    def __init__(self, parameters, return_type):
        self.parameters = parameters
        self.return_type = return_type


class BlockFunctionPointer(CDef):

    __slots__ = ('parameters', 'return_type')

    def __init__(self, parameters, return_type):
        self.parameters = parameters
        self.return_type = return_type


class Pointer(CDef):

    __slots__ = ('base_type',)

    def __init__(self, base_type):
        self.base_type = base_type


class BlockPointer(Pointer):

    __slots__ = ('base_type',)


class Reference(CDef):

    __slots__ = ('target',)

    def __init__(self, target):
        self.target = target


class Struct(CDef):

    __slots__ = ('name', 'fields')

    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


class Typedef(CDef):

    __slots__ = ('name', 'type')

    def __init__(self, name, type):
        self.name = name
        self.type = type


class Union(CDef):

    __slots__ = ('name', 'fields')

    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
