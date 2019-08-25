import itertools

from collections import OrderedDict

from .parser import Parser
from .xml_dump import XMLDump


def parse_definitions(file_paths):
    definition_names = set()
    return OrderedDict([
        (definition.name, definition)
        for definition in itertools.chain.from_iterable([
            Parser(XMLDump.FromFilePath(file_path))
            for file_path in file_paths
        ])
        if hasattr(definition, 'name') and not (
            definition.name in definition_names or
            definition_names.add(definition.name)
        )
    ])
