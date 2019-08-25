import subprocess

from lxml import etree


class XMLDump:

    class NotFoundError(Exception):

        def __init__(self, type_id):
            super().__init__(self, f'No node for {type_id}')

    def __init__(self, xml_data):
        self._xml_data = xml_data
        self.tree = etree.ElementTree(etree.fromstring(xml_data))

    @classmethod
    def FromFilePath(cls, file_path):
        return cls(subprocess.check_output([
            'castxml', '-fno-builtin', '--castxml-output=1', '-o', '-',
            file_path
        ]).decode('utf-8'))

    def as_xml(self):
        return self._xml_data

    def iterfind(self, *args, **kwargs):
        return self.tree.iterfind(*args, **kwargs)

    def iter(self, *args, **kwargs):
        return self.tree.iter(*args, **kwargs)

    def find_by_id(self, type_id, modifiers, record_id=None):
        node = self.tree.find(f"//*[@id='{type_id}']")

        if node is None:
            raise self.NotFoundError(type_id)

        while True:
            if node.tag == 'PointerType':
                modifiers.append('pointer')
                node = self.find_by_id(node.get('type'), modifiers, record_id)
            elif node.tag == 'CvQualifiedType':
                if node.get('const'):
                    modifiers.append('const')
                node = self.find_by_id(node.get('type'), modifiers, record_id)
            elif node.tag == 'ElaboratedType':
                if node.get('type') == record_id:
                    break
                node = self.find_by_id(node.get('type'), modifiers, record_id)
            else:
                break

        return node
