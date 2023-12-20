from abc import ABC, abstractmethod

import psycopg
from psycopg.rows import dict_row


class tableManager(ABC):
    def __init__(
        self,
        table: str,
        conninfo: str,
        **kwargs,
    ) -> None:
        """init

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
        self.cursor.execute(f"SELECT * FROM {self.table}")
        if wrap:
            records = self.dict_cursor.fetchall()
        else:
            records = self.cursor.fetchall()
        return records

    @abstractmethod
    def insert(self) -> bool:
        """レコードを追加"""
        raise NotImplementedError
        try:
            self.cursor.execute(
                f"""
                INSERT INTO {self.table} ( )
                VALUES ( )
                """,
                (),
            )
            self.connection.commit()
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

    @abstractmethod
    def update(self) -> bool:
        """レコードを更新"""
        raise NotImplementedError
        try:
            self.cursor.execute(
                f"""
                UPDATE {self.table} SET
                update_at = current_timestamp
                WHERE
                """,
                (),
            )
            self.connection.commit()
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

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
    def remove(self) -> None:
        """条件に合うレコードを削除"""
        raise NotImplementedError
        self.cursor.execute(
            f"""
            DELETE FROM {self.table}
            WHERE
            """,
            (),
        )
        self.connection.commit()

    def close(self) -> None:
        """DBを保存し切断"""
        self.cursor.close()
        self.connection.commit()
        self.connection.close()

    def __del__(self):
        self.close()
