import os.path
import subprocess

from clang.cindex import (  # pylint: disable=import-error
    Config,
    CursorKind,
    Index,
    TranslationUnitLoadError,
    TypeKind
)

from .cdefs import (
    Array,
    BlockFunctionPointer,
    BlockPointer,
    Bool,
    Complex,
    FloatingPoint,
    Integer,
    Void,
    Enum,
    Function,
    FunctionPointer,
    Pointer,
    Reference,
    Struct,
    Typedef,
    Union
)

from .utils import str_id_gen


_BUILTIN_FLOATING_POINTS = [
    TypeKind.HALF,
    TypeKind.FLOAT,
    TypeKind.DOUBLE,
    TypeKind.LONGDOUBLE,
    TypeKind.FLOAT128,
]

_BUILTIN_INTEGERS = [
    TypeKind.CHAR16,
    TypeKind.CHAR32,
    TypeKind.CHAR_S,
    TypeKind.CHAR_U,
    TypeKind.INT,
    TypeKind.INT128,
    TypeKind.LONG,
    TypeKind.LONGLONG,
    TypeKind.SCHAR,
    TypeKind.SHORT,
    TypeKind.UCHAR,
    TypeKind.UINT,
    TypeKind.UINT128,
    TypeKind.ULONG,
    TypeKind.ULONGLONG,
    TypeKind.USHORT,
    TypeKind.WCHAR,
]


class Parser:

    def __init__(self, preprocessor, libclang=None):
        self._preprocessor = preprocessor
        if libclang:
            Config.set_library_file(libclang)

    def _handle_typedef(self, cursor):
        typedef_type = cursor.underlying_typedef_type
        if typedef_type.kind != TypeKind.ELABORATED:
            typedef_type = self._handle_type(cursor, typedef_type)
        else:
            decl = typedef_type.get_declaration()
            if decl.is_anonymous() and decl.kind == CursorKind.STRUCT_DECL:
                typedef_type = self._handle_struct(decl)
            else:
                typedef_type = Reference(
                    typedef_type.spelling, typedef_type.is_const_qualified()
                )
        return Typedef(cursor.spelling, typedef_type)

    def _handle_union(self, cursor):
        name = cursor.type.spelling
        if not name.startswith('union '):
            name = f'union {name}'
        fields = {}
        for child in cursor.get_children():
            if child.type.kind != TypeKind.ELABORATED:
                if child.kind == CursorKind.STRUCT_DECL:
                    # Ignore these and wait for the elaborated ref later
                    continue
                fields[child.spelling] = self._handle_cursor(child)
            elif len(list(child.get_children())) != 1:
                fields[child.spelling] = self._handle_cursor(child)
            elif next(child.get_children()).type.kind != TypeKind.RECORD:
                fields[child.spelling] = self._handle_cursor(child)
            else:
                record_fields = {}
                for rc in next(child.get_children()).get_children():
                    record_fields[rc.spelling] = self._handle_cursor(rc)
                fields[child.spelling] = Struct(child.spelling, record_fields)
        return Union(name if not cursor.is_anonymous() else None, fields)

    def _handle_struct(self, cursor):
        name = cursor.type.spelling
        if not name.startswith('struct '):
            name = f'struct {name}'
        return Struct(
            name if not cursor.is_anonymous() else None, {
                c.spelling: self._handle_cursor(c)
                for c in cursor.get_children()
            }
        )

    def _handle_enum(self, cursor):
        if cursor.is_anonymous():
            name = None
        else:
            name = cursor.type.spelling
            if not name.startswith('enum'):
                name = f'enum {name}'
        return Enum(
            name=name,
            enum_type=self._handle_type(cursor, cursor.enum_type),
            values={
                child.spelling: child.enum_value
                for child in cursor.get_children()
            }
        )

    def _handle_function(self, cursor):
        param_names = str_id_gen(prefix='param_')
        return Function(
            cursor.spelling,
            {
                param.spelling or next(param_names):
                self._handle_type(cursor, param.type)
                for param in cursor.get_arguments()
            },
            self._handle_type(cursor, cursor.result_type)
        )

    def _handle_type(self, cursor, ctype):
        if ctype.kind == TypeKind.VOID:
            return Void(ctype.is_const_qualified())
        if ctype.kind == TypeKind.BOOL:
            return Bool(
                ctype.get_size(),
                ctype.get_align(),
                ctype.is_const_qualified(),
                ctype.is_volatile_qualified()
            )
        if ctype.kind in _BUILTIN_INTEGERS:
            return Integer(
                ctype.spelling,
                ctype.get_size(),
                ctype.get_align(),
                ctype.is_const_qualified(),
                ctype.is_volatile_qualified(),
                cursor.is_bitfield(),
                cursor.get_bitfield_width()
            )
        if ctype.kind in _BUILTIN_FLOATING_POINTS:
            return FloatingPoint(
                ctype.spelling,
                ctype.get_size(),
                ctype.get_align(),
                ctype.is_const_qualified(),
                ctype.is_volatile_qualified(),
            )
        if ctype.kind == TypeKind.COMPLEX:
            return Complex(
                ctype.spelling,
                ctype.get_size(),
                ctype.get_align(),
                ctype.is_const_qualified(),
                ctype.is_volatile_qualified(),
            )
        if ctype.kind == TypeKind.CONSTANTARRAY:
            if cursor.kind in (CursorKind.FIELD_DECL,
                               CursorKind.FUNCTION_DECL):
                name = None
            else:
                name = cursor.spelling
            return Array(
                name=name,
                element_type=self._handle_type(cursor, ctype.element_type),
                element_count=ctype.element_count
            )
        if ctype.kind == TypeKind.TYPEDEF:
            return Reference(ctype.spelling, ctype.is_const_qualified())
        if ctype.kind == TypeKind.ELABORATED:
            return Reference(ctype.spelling, ctype.is_const_qualified())
        if ctype.kind == TypeKind.POINTER:
            pointee = ctype.get_pointee()
            if pointee.kind == TypeKind.FUNCTIONPROTO:
                return FunctionPointer(
                    dict(
                        zip(
                            str_id_gen(prefix='param_'),
                            map(
                                lambda t: self._handle_type(cursor, t),
                                pointee.argument_types()
                            )
                        )
                    ),
                    self._handle_type(cursor, pointee.get_result())
                )
            return Pointer(
                self._handle_type(cursor, pointee),
                ctype.is_const_qualified(),
                not ctype.is_restrict_qualified(),
                ctype.is_volatile_qualified()
            )
        if ctype.kind == TypeKind.BLOCKPOINTER:
            pointee = ctype.get_pointee()
            if pointee.kind == TypeKind.FUNCTIONPROTO:
                return BlockFunctionPointer(
                    dict(
                        zip(
                            str_id_gen(prefix='param_'),
                            map(
                                lambda t: self._handle_type(cursor, t),
                                pointee.argument_types()
                            )
                        )
                    ),
                    self._handle_type(cursor, pointee.get_result())
                )
            return BlockPointer(
                self._handle_type(cursor, pointee),
                ctype.is_const_qualified(),
                not ctype.is_restrict_qualified(),
                ctype.is_volatile_qualified()
            )
        if ctype.kind == TypeKind.INCOMPLETEARRAY:
            return Array(
                name=None,
                element_type=self._handle_type(cursor, ctype.element_type),
                element_count=None
            )

    def _handle_field(self, cursor):
        return self._handle_type(cursor, cursor.type)

    def _handle_cursor(self, cursor):
        if cursor.kind == CursorKind.TYPEDEF_DECL:
            return self._handle_typedef(cursor)
        if cursor.kind == CursorKind.UNION_DECL:
            return self._handle_union(cursor)
        if cursor.kind == CursorKind.FIELD_DECL:
            return self._handle_field(cursor)
        if cursor.kind == CursorKind.STRUCT_DECL:
            return self._handle_struct(cursor)
        if cursor.kind == CursorKind.ENUM_DECL:
            return self._handle_enum(cursor)
        if cursor.kind == CursorKind.FUNCTION_DECL:
            return self._handle_function(cursor)
        if cursor.kind == CursorKind.TRANSLATION_UNIT:
            return
        if cursor.kind == CursorKind.VAR_DECL:
            return
        if cursor.kind == CursorKind.PACKED_ATTR:
            return

    def _walk(self, cursor):
        yield self._handle_cursor(cursor)
        for child in cursor.get_children():
            yield self._handle_cursor(child)

    def parse(self, file_path):
        if not os.path.isfile(file_path):
            return []

        cmd = [self._preprocessor, '-E', file_path]
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as cpp:
            index = Index.create()
            try:
                translation_unit = index.parse(
                    file_path, unsaved_files=[(file_path, cpp.stdout)]
                )
            except TranslationUnitLoadError as exc:
                raise Exception(f'Error loading {file_path}: {exc}') from None

            return filter(None, self._walk(translation_unit.cursor))
