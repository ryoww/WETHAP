import re
from abc import ABC, abstractmethod

import psycopg
from psycopg.rows import dict_row


class TableManager(ABC):
    def __init__(
        self,
        table: str,
        conninfo: str,
        **kwargs,
    ) -> None:
        """postgresql用table操作基底クラス

        Args:
            table (str): テーブル名
            conninfo (str): postgresql://...
            **kwargs: 接続パラメータ
        """
        self.table = table
        self.connection = psycopg.connect(conninfo=conninfo, **kwargs)
        self.cursor = self.connection.cursor()
        self.dict_cursor = self.connection.cursor(row_factory=dict_row)

    @abstractmethod
    def create_table(self) -> None:
        """テーブルを作成"""
        raise NotImplementedError
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            )
            """
        )
        self.connection.commit()

    def delete_table(self) -> None:
        """テーブルを削除"""
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table}")
        self.connection.commit()

    def init_table(self) -> None:
        """テーブルを初期化"""
        self.delete_table()
        self.create_table()

    def get_all(self, wrap: bool = True) -> list:
        """全レコードを取得"""
        query = f"SELECT * FROM {self.table}"
        if wrap:
            self.dict_cursor.execute(query)
            records = self.dict_cursor.fetchall()
        else:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
        return records

    def transaction(self, query: str, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except psycopg.DatabaseError as error:
            query = re.sub("\n *", " ", query)
            print(f"transaction error: {query=}, {params=}")
            self.connection.rollback()
            raise error

    def insert(self, *args, **kwargs):
        """レコードを追加"""
        query, params = self._insert(*args, **kwargs)
        self.transaction(query, params)

    def update(self, *args, **kwargs):
        """レコードを更新"""
        query, params = self._update(*args, **kwargs)
        self.transaction(query, params)

    def remove(self, *args, **kwargs):
        """条件に合うレコードを削除"""
        query, params = self._remove(*args, **kwargs)
        self.transaction(query, params)

    def select_one(
        self, query: str, params: tuple = None, wrap: bool = True
    ) -> tuple | dict:
        """条件に合うレコードを1つ取得"""
        if wrap:
            self.dict_cursor.execute(query, params)
            records = self.dict_cursor.fetchone()
        else:
            self.cursor.execute(query, params)
            records = self.cursor.fetchone()
        return records

    def select_all(
        self, query: str, params: tuple = None, wrap: bool = True
    ) -> list[tuple | dict]:
        """条件に合うレコードを全て取得"""
        if wrap:
            self.dict_cursor.execute(query, params)
            records = self.dict_cursor.fetchall()
        else:
            self.cursor.execute(query, params)
            records = self.cursor.fetchall()
        return records

    @abstractmethod
    def select(self) -> tuple:
        """条件に合うレコードを取得"""
        raise NotImplementedError
        self.cursor.execute(
            f"""
            SELECT * FROM {self.table}
            WHERE
            """,
            (),
        )
        return self.cursor.fetchone()

    @abstractmethod
    def _insert(self) -> tuple[str, tuple]:
        raise NotImplementedError
        query = f"""
                INSERT INTO {self.table} ( )
                VALUES ( )
                """
        params = ()
        return query, params

    @abstractmethod
    def _update(self) -> tuple[str, tuple]:
        raise NotImplementedError
        query = f"""
                UPDATE {self.table} SET
                update_at = current_timestamp
                WHERE
                """
        params = ()
        return query, params

    @abstractmethod
    def _remove(self) -> tuple[str, tuple]:
        raise NotImplementedError
        query = f"""
            DELETE FROM {self.table}
            WHERE
            """
        params = ()
        return query, params

    def close(self) -> None:
        """DBを保存し切断"""
        self.cursor.close()
        self.dict_cursor.close()
        self.connection.commit()
        self.connection.close()

    def __del__(self):
        self.close()
