from abc import ABC

import psycopg2


class tableManager(ABC):
    COLUMN_INFO = {}

    def __init__(
        self,
        table: str,
        dbname: str,
        user: str,
        password: str,
        host: str,
        port: int,
        **kwargs,
    ) -> None:
        """init

        Args:
            table (str): テーブル名
            dbname (str): DB名
            user (str): ユーザ名
            password (str): パスワード
            host (str): ホスト名またはIPアドレス
            port (int): ポート番号
        """
        self.table = table
        self.connection: psycopg2.extensions.connection = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port, **kwargs
        )
        self.cursor: psycopg2.extensions.cursor = self.connection.cursor()

    def create_table(self):
        """テーブルを作成"""
        raise NotImplementedError

    def delete_table(self) -> None:
        """テーブルを削除"""
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table}")
        self.connection.commit()

    def init_table(self) -> None:
        """テーブルを初期化"""
        self.delete_table()
        self.create_table()

    def fetch_all(self, wrap: bool = True):
        """全レコードを取得"""
        self.cursor.execute(f"SELECT * FROM {self.table}")
        records = self.cursor.fetchall()
        if not wrap:
            return records
        wrapped_records = self.wrap_records(records)
        return wrapped_records

    def wrap_records(self, response: list | tuple) -> list | tuple:
        """fetch結果をフィールド名を辞書としたdictに変換

        Args:
            response (list|tuple): レコード

        Returns:
            list|tuple: 変換後のレコード
        """
        if isinstance(response, tuple):
            wrapped = {
                key: item for key, item in zip(self.COLUMN_INFO.keys(), response)
            }
        elif isinstance(response, list):
            wrapped = [
                {key: item for key, item in zip(self.COLUMN_INFO.keys(), record)}
                for record in response
            ]
        else:
            raise ValueError
        return wrapped

    def insert(self):
        """レコードを追加"""
        raise NotImplementedError

    def update(self):
        """レコードを更新"""
        raise NotImplementedError

    def select(self):
        """条件に合うレコードを取得"""
        raise NotImplementedError

    def remove(self):
        """条件に合うレコードを削除"""
        raise NotImplementedError

    def close(self) -> None:
        """DBを保存し切断"""
        self.cursor.close()
        self.connection.commit()
        self.connection.close()
