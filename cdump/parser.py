import os.path

from clang.cindex import (
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

    def __init__(self, libclang=None):
        if libclang:
            Config.set_library_file(libclang)

    def _handle_typedef(self, cursor):
        typedef_type = cursor.underlying_typedef_type
        if typedef_type.kind == TypeKind.ELABORATED:
            typedef_type = Reference(
                typedef_type.spelling,
                typedef_type.is_const_qualified()
            )
        else:
            typedef_type = self._handle_type(typedef_type)
        return Typedef(cursor.spelling, typedef_type)

    def _handle_union(self, cursor):
        return Union(
            cursor.type.spelling if not cursor.is_anonymous() else None,
            {c.spelling: self._handle_cursor(c) for c in cursor.get_children()}
        )

    def _handle_struct(self, cursor):
        name = cursor.type.spelling
        if not name.startswith('struct '):
            name = f'struct {name}'
        return Struct(
            name if not cursor.is_anonymous() else None,
            {c.spelling: self._handle_cursor(c) for c in cursor.get_children()}
        )

    def _handle_enum(self, cursor):
        return Enum(
            self._handle_type(cursor.enum_type),
            {
                child.spelling: child.enum_value
                for child in cursor.get_children()
            }
        )

    def _handle_function(self, cursor):
        param_names = str_id_gen(prefix='arg_')
        return Function(
            cursor.spelling,
            {
                param.spelling or next(param_names):
                self._handle_type(param.type)
                for param in cursor.get_arguments()
            },
            self._handle_type(cursor.result_type)
        )

    def _handle_type(self, ctype):
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
            return Array(
                self._handle_type(ctype.element_type),
                ctype.element_count
            )
        if ctype.kind == TypeKind.TYPEDEF:
            return Reference(ctype.spelling, ctype.is_const_qualified())
        if ctype.kind == TypeKind.ELABORATED:
            return Reference(ctype.spelling, ctype.is_const_qualified())
        if ctype.kind == TypeKind.POINTER:
            pointee = ctype.get_pointee()
            if pointee.kind == TypeKind.FUNCTIONPROTO:
                return FunctionPointer(
                    list(map(self._handle_type, pointee.argument_types())),
                    self._handle_type(pointee.get_result())
                )
            return Pointer(
                self._handle_type(pointee),
                ctype.is_const_qualified(),
                not ctype.is_restrict_qualified(),
                ctype.is_volatile_qualified()
            )
        if ctype.kind == TypeKind.BLOCKPOINTER:
            pointee = ctype.get_pointee()
            if pointee.kind == TypeKind.FUNCTIONPROTO:
                return BlockFunctionPointer(
                    list(map(self._handle_type, pointee.argument_types())),
                    self._handle_type(pointee.get_result())
                )
            return BlockPointer(
                self._handle_type(pointee),
                ctype.is_const_qualified(),
                not ctype.is_restrict_qualified(),
                ctype.is_volatile_qualified()
            )
        if ctype.kind == TypeKind.INCOMPLETEARRAY:
            return Array(self._handle_type(ctype.element_type))

    def _handle_field(self, cursor):
        return self._handle_type(cursor.type)

    def _handle_cursor(self, cursor):
        if cursor.kind == CursorKind.TRANSLATION_UNIT:
            return
        if cursor.kind == CursorKind.VAR_DECL:
            return
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

    def _walk(self, cursor):
        yield self._handle_cursor(cursor)
        for child in cursor.get_children():
            yield self._handle_cursor(child)

    def parse(self, file_path):
        index = Index.create()
        if not os.path.isfile(file_path):
            return []
        try:
            translation_unit = index.parse(file_path)
        except TranslationUnitLoadError as exc:
            raise Exception(f'Error loading {file_path}: {exc}') from None
        return filter(None, self._walk(translation_unit.cursor))
