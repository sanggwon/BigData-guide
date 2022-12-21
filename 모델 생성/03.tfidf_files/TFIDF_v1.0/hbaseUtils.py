import sys
import happybase
from imp import reload

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class HbaseUtils(object):
    def __init__(self, host, port, size):
        self.pool = happybase.ConnectionPool(size=size, host=host, port=port)

    '''
    families = {"f1":dict(),"f2":dict()}
    '''

    def create_table(self, table_name, families):
        try:
            with self.pool.connection() as connection:
                connection.create_table(table_name, families)
        except Exception as e:
            print(e)

    def delete_table(self, table_name, disable=False):
        try:
            with self.pool.connection() as connection:
                connection.delete_table(table_name, disable=disable)
        except Exception as e:
            print(e)

    def read_table(self, table_name):
        with self.pool.connection() as connection:
            return connection.table(table_name)

    def read_tables(self):
        with self.pool.connection() as connection:
            return connection.tables()

    def insert(self, table_name, row, data, timestamp=None, wal=True):
        try:
            with self.pool.connection() as connection:
                connection.table(table_name).put(row, data, timestamp=timestamp, wal=wal)
        except Exception as e:
            print(e)

    def insert_batch(self, table_name, data_list, batch_size=1000):
        try:
            with self.pool.connection() as connection:
                with connection.table(table_name).batch(batch_size=batch_size) as batch:
                    for data in data_list:
                        batch.put(data['row'], data['data'], data['timestamp'] if 'timestamp' in data else None)
        except Exception as e:
            print(e)

    def delete(self, table_name, row, columns=None, timestamp=None, wal=True):
        try:
            with self.pool.connection() as connection:
                connection.table(table_name).delete(row, columns=columns, timestamp=timestamp, wal=wal)
        except Exception as e:
            print(e)

    def read_row(self, table_name, row, columns=None, timestamp=None, include_timestamp=None):
        try:
            with self.pool.connection() as connection:
                return connection.table(table_name).row(row, columns=columns, timestamp=timestamp,
                                                        include_timestamp=include_timestamp)
        except Exception as e:
            print(e)

    def read_rows(self, table_name, rows, columns=None, timestamp=None, include_timestamp=None, need_dict=False):
        try:
            with self.pool.connection() as connection:
                result = connection.table(table_name).rows(rows, columns=columns, timestamp=timestamp,
                                                           include_timestamp=include_timestamp)
                return result if not need_dict else dict(result)
        except Exception as e:
            print(e)

    def read_cells(self, table_name, row, column, versions=None, timestamp=None, include_timestamp=False):
        try:
            with self.pool.connection() as connection:
                return connection.table(table_name).cells(row, column, versions=versions, timestamp=timestamp,
                                                          include_timestamp=include_timestamp)
        except Exception as e:
            print(e)

    def read_families(self, table_name):
        try:
            with self.pool.connection() as connection:
                return connection.table(table_name).families()
        except Exception as e:
            print(e)

    def read_regions(self, table_name):
        try:
            with self.pool.connection() as connection:
                return connection.table(table_name).regions()
        except Exception as e:
            print(e)

    def read_scan(self, table_name, row_start=None, row_stop=None, row_prefix=None, columns=None,
                  filter=None, timestamp=None, include_timestamp=False, batch_size=1000,
                  scan_batching=None, limit=None, sorted_columns=False, reverse=False):
        try:
            with self.pool.connection() as connection:
                return connection.table(table_name).scan(row_start=row_start, row_stop=row_stop,
                                                         row_prefix=row_prefix,
                                                         columns=columns, filter=filter, timestamp=timestamp,
                                                         include_timestamp=include_timestamp, batch_size=batch_size,
                                                         scan_batching=scan_batching, limit=limit,
                                                         sorted_columns=sorted_columns, reverse=reverse)
        except Exception as e:
            print(e)