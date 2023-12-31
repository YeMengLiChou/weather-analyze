import logging
import threading

import happybase
from happybase import Table, Connection


class HBaseUtils(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(HBaseUtils, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict):
        self.config = config
        self.__connection = self.__get_connection()
        self.tables = list(map(lambda x:x.decode(), (self.__connection.tables())))
        self.tables_instance = dict()
        for table in self.config['tables']:
            # 没有就创建表
            if table['name'] not in self.tables:
                families = dict()
                for family in table['families']:
                    families[family] = dict(max_versions=3)
                self.create_table(table['name'], families)

    def close(self):
        self.__connection.close()

    def __get_table(self, table_name: str) -> Table:
        if table_name not in self.tables_instance:
            self.tables_instance[table_name] = self.__connection.table(table_name)
        return self.tables_instance[table_name]

    def __get_connection(self):
        return happybase.Connection(
            host=self.config['host'],
            port=self.config['port'],
        )

    @property
    def connect(self) -> Connection:
        if not self.__connection.transport.is_open():
            self.__connection = self.__get_connection()
        return self.__connection

    def create_table(self, table_name: str, families: dict, replace: bool = False) -> None:
        """创建表

        """
        if table_name.encode() in self.tables:
            if replace:
                self.delete_table(table_name)
            return

        self.__connection.create_table(
            table_name,
            families=families
        )
        self.tables = self.__connection.tables()

    def delete_table(self, table_name: str) -> None:
        """删除一个表
        """
        if table_name not in self.tables:
            return
            # raise RuntimeError(f'table {table_name} not exists!')
        self.__connection.delete_table(table_name, disable=True)
        print(f'deleted table {table_name}')

    def put_cell(self, table_name: str, row_key: str, column_family: str, column: str, value: str,
                 timestamp: int = None) -> None:
        """插入一个单元格

        类比 shell 中的 put 指令

        :param table_name 表
        :param row_key 行键
        :param column_family 列族
        :param column
        :param value
        :param timestamp 时间戳，不指定则为当前时间
        """
        table = self.__get_table(table_name)
        if not column or len(column) == 0:
            column = column_family.encode()
        else:
            column = f"{column_family}:{column}".encode()
        table.put(row_key, {column: value.encode()}, timestamp)

    def put_column_family(self, table_name: str, row_key: str, column_family: str, data: dict,
                          timestamp: int = None) -> None:
        """插入一行的数据

        类比 shell 中的 put 指令

        :param table_name 表
        :param row_key 行键
        :param column_family 列族
        :param data 插入的数据，格式为``{'column'-'value' }``
        :param timestamp 事件
        """
        table = self.__get_table(table_name)
        result = dict()
        for column, value in data.items():
            if not column or len(column) == 0:
                column = column_family.encode()
            else:
                column = f"{column_family}:{column}".encode()
            result[column] = value.encode()

        table.put(row_key, result, timestamp)

    def put_row(self, table_name: str, row_key: str, data: dict, timestamp: int = None) -> None:
        """插入一行的数据

        类比 shell 中的 put 指令

        :param table_name 表
        :param row_key 行键
        :param data 插入的数据，格式为``{'column_family:column'--'value'} }``
        :param timestamp 事件
        """
        table = self.__get_table(table_name)
        result = dict[bytes, bytes]()
        for column, value in data.items():
            if not isinstance(value, str):
                value = str(value)
            result[column.encode()] = value.encode()
        try:
            table.put(row_key, result, timestamp)
        except Exception as e:
            logging.exception(e)
            print(row_key)
            print(result)

#
