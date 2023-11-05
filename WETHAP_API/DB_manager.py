import datetime
from decimal import Decimal

import psycopg2

TABLE_FIELD_TYPES = tuple[
    int,
    str,
    datetime.date,
    int,
    Decimal,
    Decimal,
    Decimal,
    str,
    datetime.datetime,
    datetime.datetime,
]


class DBManager:
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

    def create_table(self) -> None:
        """WETHAP用のtableを作成"""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY,
                labID text,
                date date,
                numGen integer,
                temperature numeric,
                humidity numeric,
                pressure numeric,
                weather text,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            );
            """
        )
        self.connection.commit()

    def delete_table(self) -> None:
        """テーブルを削除"""
        self.cursor.execute(f"DROP TABLE IF {self.table}")
        self.connection.commit()

    def insert(
        self,
        labID: str,
        date: str,
        numGen: int,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> None:
        """レコードを追加

        Args:
            labID (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            numGen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        self.cursor.execute(
            f"""
            INSERT INTO {self.table} (
                labID, date, numGen, temperature, humidity, pressure, weather
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (labID, date, numGen, temperature, humidity, pressure, weather),
        )
        self.connection.commit()

    def update(
        self,
        id: int,
        labID: str,
        date: str,
        numGen: int,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> None:
        """レコードを更新

        Args:
            id (int): 変更したいレコードのid
            labID (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            numGen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        self.cursor.execute(
            f"""
            UPDATE {self.table} SET
            labID = %s,
            date = %s,
            numGen = %s,
            temperature = %s,
            humidity = %s,
            pressure = %s,
            weather = %s,
            update_at = current_timestamp
            WHERE id = %s
            """,
            (labID, date, numGen, temperature, humidity, pressure, weather, id),
        )
        self.connection.commit()

    def select(self, labID: str, date: str, numGen: int) -> TABLE_FIELD_TYPES:
        """条件に合うレコードを取得

        Args:
            labID (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            numGen (int): 時限

        Returns:
            TABLE_FIELD_TYPES: 検索結果
        """
        self.cursor.execute(
            f"""
            SELECT * FROM {self.table}
            WHERE labID = %s and date = %s and numGen = %s
            ORDER BY update_at
            """,
            (labID, date, numGen),
        )
        response = self.cursor.fetchall()
        return response[-1] if response else None

    def is_registered(self, labID: str) -> bool:
        """登録済みの研究室か

        Args:
            labID (str): 研究室名

        Returns:
            bool: 判定結果
        """
        self.cursor.execute(
            f"SELECT DISTINCT labID FROM {self.table} WHERE labID = %s", (labID,)
        )
        response = self.cursor.fetchall()
        return bool(response)

    def registered_rooms(self) -> list[str]:
        """登録済みの研究室一覧

        Returns:
            list[str]: 登録済み研究室
        """
        self.cursor.execute(f"SELECT DISTINCT labID FROM {self.table}")
        response = self.cursor.fetchall()
        rooms = [room[0] for room in response]
        return rooms

    def preview_data(
        self,
    ) -> list[TABLE_FIELD_TYPES]:
        """全レコードを取得

        Returns:
            list[TABLE_FIELD_TYPES]: 全レコード
        """
        self.cursor.execute(f"SELECT * FROM {self.table} ORDER BY id")
        response = self.cursor.fetchall()
        return response

    def close(self) -> None:
        """DBを保存し切断"""
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    import os

    import dotenv

    dotenv.load_dotenv()
    db_config = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
    }
    manager = DBManager(table="infos", **db_config)
    # print(manager.preview_data())
    # manager.delete_table()
    manager.create_table()
    # manager.insert("テスト", str(datetime.date.today()), 0.0, 0.0, 0.0, 0.0, "晴れ")
    # manager.update(10, "更新", str(datetime.date.today()), 1.0, 1.0, 1.0, 1.0, "雨")
    print(manager.preview_data())
    manager.close()
