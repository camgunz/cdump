import sqlite3


class Database:

    def __init__(self, db_name=':memory:'):
        self._conn = sqlite3.connect(db_name)
        self._table_cache = set()

    def write_definitions(self, definitions):
        cursor = self._conn.cursor()
        for definition in definitions:
            # pylint: disable=unidiomatic-typecheck
            if type(definition) not in self._table_cache:
                definition.create_database_table(cursor)
                self._table_cache.add(type(definition))
            definition.write_to_database(cursor)
        self._conn.commit()
