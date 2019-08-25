from .cobjects import (
    Array, Builtin, Enumeration, EnumerationValue, Field, Function,
    FunctionType, Parameter, AnonymousParameter, SelfReference,
    Struct, Typedef, Unimplemented, Union
)
from .utils import elemstr, intattr


class Parser:

    TOP_LEVEL_TAGS = [
        'FundamentalType', 'Enumeration', 'ArrayType', 'Typedef',
        'Struct', 'Union', 'FunctionType', 'Function',
    ]

    def __init__(self, xml):
        self.xml = xml

    def __iter__(self):
        return self.get_iterator()

    # pylint: disable=no-self-use
    def parse_fundamental_type_node(self, node):
        return Builtin(
            node.get('name'),
            int(node.get('size')),
            int(node.get('align'))
        )

    # pylint: disable=no-self-use
    def parse_enumeration_node(self, node):
        return Enumeration(node.get('name'), [
            EnumerationValue(
                enum_value_node.get('name'),
                int(enum_value_node.get('init'))
            )
            for enum_value_node in node.iterfind('EnumValue')
        ])

    def parse_array_type_node(self, node):
        mods = []
        elem_type_node = self.xml.find_by_id(node.get('type'), mods)
        return Array(
            self.modified_reference_for_node(elem_type_node, mods),
            intattr(node, 'min'),
            intattr(node, 'max'),
        )

    def parse_typedef_node(self, node):
        mods = []
        type_node = self.xml.find_by_id(node.get('type'), mods)
        return Typedef(
            node.get('name'),
            self.modified_reference_for_node(type_node, mods)
        )

    def parse_field_node(self, node, outer_id):
        mods = []
        type_node = self.xml.find_by_id(
            node.get('type'),
            mods,
            outer_id
        ) if node.tag == 'Field' else node
        return Field(
            node.get('name'),
            self.modified_reference_for_node(type_node, mods)
        )

    def parse_argument_nodes(self, parent):
        parameters = []
        for argument_node in parent.iterfind('Argument'):
            mods = []
            type_node = self.xml.find_by_id(argument_node.get('type'), mods)
            parameters.append(
                Parameter(
                    argument_node.get('name'),
                    self.modified_reference_for_node(type_node, mods)
                ) if argument_node.get('name')
                else AnonymousParameter(
                    self.modified_reference_for_node(type_node, mods)
                )
            )
        return parameters

    def parse_struct_node(self, node):
        return Struct(node.get('name'), [
            self.parse_field_node(self.xml.find_by_id(
                field_id,
                [],
                node.get('id')
            ), node.get('id')) for field_id in node.get('members').split()
        ]) if node.get('members') else Struct(node.get('name'))

    def parse_union_node(self, node):
        return Union(node.get('name'), [
            self.parse_field_node(self.xml.find_by_id(
                field_id,
                [],
                node.get('id')
            ), node.get('id')) for field_id in node.get('members').split()
        ])

    def parse_function_type_node(self, node):
        mods = []
        return_type_node = self.xml.find_by_id(node.get('returns'), mods)
        return FunctionType(
            self.parse_argument_nodes(node),
            self.modified_reference_for_node(return_type_node, mods)
        )

    def parse_function_node(self, node):
        mods = []
        return_type_node = self.xml.find_by_id(node.get('returns'), mods)
        return Function(
            node.get('name'),
            self.parse_argument_nodes(node),
            self.modified_reference_for_node(return_type_node, mods)
        )

    def object_for_node(self, node):
        if node.tag == 'FundamentalType':
            return self.parse_fundamental_type_node(node)
        if node.tag == 'Enumeration':
            return self.parse_enumeration_node(node)
        if node.tag == 'ArrayType':
            return self.parse_array_type_node(node)
        if node.tag == 'Typedef':
            return self.parse_typedef_node(node)
        if node.tag == 'Struct':
            return self.parse_struct_node(node)
        if node.tag == 'Union':
            return self.parse_union_node(node)
        if node.tag == 'FunctionType':
            return self.parse_function_type_node(node)
        if node.tag == 'Function':
            return self.parse_function_node(node)
        if node.tag == 'ElaboratedType':
            return SelfReference()
        if node.tag == 'Unimplemented':
            return Unimplemented()
        raise Exception(f'No object for {elemstr(node)}')

    def modified_reference_for_node(self, node, modifiers):
        return self.object_for_node(node).get_modified_reference(modifiers)

    def get_iterator(self):
        for node in self.xml.iterfind('FundamentalType'):
            yield self.object_for_node(node)

        for node in self.xml.iter():
            if node.tag in self.TOP_LEVEL_TAGS:
                yield self.object_for_node(node)
