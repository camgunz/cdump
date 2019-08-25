from .cobjects import (
    Array, Builtin, Enumeration, EnumerationValue, Field, Function,
    FunctionType, Parameter, AnonymousParameter, SelfReference,
    Struct, Typedef, Unimplemented, Union
)


def intattr(node, attr_name):
    attr = node.get(attr_name)
    if not attr:
        return None
    return int(attr, 10)


class Parser:

    """Parses an XML dump."""

    def __init__(self, xml_dump):
        self.xml_dump = xml_dump
        self.top_level_tags = [
            'FundamentalType',
            'Enumeration',
            'ArrayType',
            'Typedef',
            'Struct',
            'Union',
            'FunctionType',
            'Function',
        ]

    def object_for_node(self, node):
        if node.tag == 'FundamentalType':
            builtin = node
            return Builtin(
                builtin.get('name'),
                int(builtin.get('size')),
                int(builtin.get('align'))
            )

        if node.tag == 'Enumeration':
            enum = node
            return Enumeration(enum.get('name'), [
                EnumerationValue(v.get('name'), int(v.get('init')))
                for v in enum.iterfind('EnumValue')
            ])

        if node.tag == 'ArrayType':
            array = node
            modifiers = []
            element_type_node = self.xml_dump.find_by_id(
                array.get('type'),
                modifiers
            )
            return Array(
                self.object_for_node(
                    element_type_node
                ).get_modified_reference(modifiers),
                intattr(array, 'min'),
                intattr(array, 'max'),
            )

        if node.tag == 'Typedef':
            typedef = node
            modifiers = []
            type_node = self.xml_dump.find_by_id(
                typedef.get('type'),
                modifiers
            )
            return Typedef(
                typedef.get('name'),
                self.object_for_node(
                    type_node
                ).get_modified_reference(modifiers)
            )

        if node.tag == 'Struct':
            struct = node
            fields = []
            if struct.get('members') is None:
                return Struct(struct.get('name'))
            for field_id in struct.get('members').split():
                field_node = self.xml_dump.find_by_id(
                    field_id,
                    [],
                    struct.get('id')
                )
                modifiers = []
                if field_node.tag == 'Field':
                    field_type_node = self.xml_dump.find_by_id(
                        field_node.get('type'),
                        modifiers,
                        struct.get('id')
                    )
                else:
                    field_type_node = field_node
                fields.append(Field(
                    field_node.get('name'),
                    self.object_for_node(
                        field_type_node
                    ).get_modified_reference(modifiers)
                ))
            return Struct(struct.get('name'), fields)

        if node.tag == 'Union':
            union = node
            fields = []
            for field_id in union.get('members').split():
                field_node = self.xml_dump.find_by_id(
                    field_id,
                    [],
                    union.get('id')
                )
                modifiers = []
                if field_node.tag == 'Field':
                    field_type_node = self.xml_dump.find_by_id(
                        field_node.get('type'),
                        modifiers,
                        union.get('id')
                    )
                else:
                    field_type_node = field_node
                fields.append(Field(
                    field_node.get('name'),
                    self.object_for_node(
                        field_type_node
                    ).get_modified_reference(modifiers)
                ))
            return Union(union.get('name'), fields)

        if node.tag == 'FunctionType':
            function_type = node
            parameters = []
            for argument_node in function_type.iterfind('Argument'):
                modifiers = []
                type_node = self.xml_dump.find_by_id(
                    argument_node.get('type'),
                    modifiers
                )
                parameters.append(AnonymousParameter(
                    self.object_for_node(
                        type_node
                    ).get_modified_reference(modifiers)
                ))
            modifiers = []
            return_type_node = self.xml_dump.find_by_id(
                function_type.get('returns'),
                modifiers
            )
            return FunctionType(
                parameters,
                self.object_for_node(
                    return_type_node
                ).get_modified_reference(modifiers)
            )

        if node.tag == 'Function':
            function = node
            parameters = []
            for argument_node in function.iterfind('Argument'):
                modifiers = []
                type_node = self.xml_dump.find_by_id(
                    argument_node.get('type'),
                    modifiers
                )
                parameters.append(Parameter(
                    argument_node.get('name'),
                    self.object_for_node(
                        type_node
                    ).get_modified_reference(modifiers)
                ))
            modifiers = []
            return_type_node = self.xml_dump.find_by_id(
                function.get('returns'),
                modifiers
            )
            return Function(
                function.get('name'),
                parameters,
                self.object_for_node(
                    return_type_node
                ).get_modified_reference(modifiers)
            )

        if node.tag == 'ElaboratedType':
            return SelfReference()

        if node.tag == 'Unimplemented':
            return Unimplemented()

        raise Exception(f'No object for {node}')

    def __iter__(self):
        return self.get_iterator()

    def get_iterator(self):
        for node in self.xml_dump.iterfind('FundamentalType'):
            yield self.object_for_node(node)

        for node in self.xml_dump.iter():
            if node.tag in self.top_level_tags:
                yield self.object_for_node(node)
