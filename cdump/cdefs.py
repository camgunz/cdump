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
        return dict(zip(self.attr_names, self.attrs))

    @property
    def attr_map_string(self):
        return comma_separate([
            pair('=', *x) for x in self.attr_map.items()
        ])

    def to_dict(self):
        od = {'obj_type': self.type_name}
        for attr_name, attr in zip(self.attr_names, self.attrs):
            if isinstance(attr, CDef):
                od[attr_name] = attr.to_dict()
            elif isinstance(attr, list):
                od[attr_name] = [
                    x.to_dict() if isinstance(x, CDef) else x
                    for x in attr
                ]
            elif isinstance(attr, dict):
                od[attr_name] = {
                    k: v.to_dict() if isinstance(v, CDef) else v
                    for k, v in attr.items()
                }
            else:
                od[attr_name] = attr
        return od


class Array(CDef):

    __slots__ = ('element_type', 'element_count')

    def __init__(self, element_type, element_count=None):
        self.element_type = element_type
        self.element_count = element_count


class ScalarType(CDef):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')

    def __init__(self, name, size, alignment, is_const, is_volatile):
        self.size = size
        self.alignment = alignment
        self.is_signed = not name.startswith('unsigned ')
        self.is_const = is_const
        self.is_volatile = is_volatile


class Void(ScalarType):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')

    def __init__(self, is_const):
        super().__init__('void', None, None, is_const, False)
        self.is_signed = False


class Bool(ScalarType):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')

    def __init__(self, size, alignment, is_const, is_volatile):
        super().__init__('bool', size, alignment, is_const, is_volatile)


class Integer(ScalarType):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')


class FloatingPoint(ScalarType):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')


class Complex(ScalarType):

    __slots__ = ('size', 'alignment', 'is_signed', 'is_const', 'is_volatile')


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

    __slots__ = ('parameter_types', 'return_type')

    def __init__(self, parameter_types, return_type):
        self.parameter_types = parameter_types
        self.return_type = return_type


class BlockFunctionPointer(CDef):

    __slots__ = ('parameters', 'return_type')

    def __init__(self, parameters, return_type):
        self.parameters = parameters
        self.return_type = return_type


class Pointer(CDef):

    __slots__ = ('base_type', 'is_const', 'can_alias', 'is_volatile')

    def __init__(self, base_type, is_const, can_alias, is_volatile):
        self.base_type = base_type
        self.is_const = is_const
        self.can_alias = can_alias
        self.is_volatile = is_volatile


class BlockPointer(Pointer):

    __slots__ = ('base_type', 'is_const', 'can_alias', 'is_volatile')


class Reference(CDef):

    __slots__ = ('target', 'is_const')

    def __init__(self, target, is_const):
        if target.startswith('const '):
            target = target[6:]
        self.target = target
        self.is_const = is_const


class Struct(CDef):

    __slots__ = ('name', 'fields', 'is_anonymous')

    def __init__(self, name, fields):
        if name is not None and name.startswith('const '):
            name = name[6:]
        self.name = name
        self.fields = fields
        self.is_anonymous = name is None


class Typedef(CDef):

    __slots__ = ('name', 'type')

    def __init__(self, name, type):
        if name.startswith('const '):
            name = name[6:]
        self.name = name
        self.type = type


class Union(CDef):

    __slots__ = ('name', 'fields', 'is_anonymous')

    def __init__(self, name, fields):
        if name is not None and name.startswith('const '):
            name = name[6:]
        self.name = name
        self.fields = fields
        self.is_anonymous = name is None
