import datetime
from decimal import Decimal

import psycopg
from utils.db_util import tableManager


class infosManager(tableManager):
    INFO_TABLE_TYPES = tuple[
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

    @property
    def column_info(self) -> dict[str, type]:
        column_info = {
            "id": int,
            "labID": str,
            "date": datetime.date,
            "numGen": int,
            "temperature": Decimal,
            "humidity": Decimal,
            "pressure": Decimal,
            "weather": str,
            "create_at": datetime.datetime,
            "update_at": datetime.datetime,
        }
        return column_info

    def create_table(self) -> None:
        """WETHAP infos用のテーブルを作成"""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY,
                labID text NOT NULL,
                date date NOT NULL,
                numGen integer,
                temperature numeric NOT NULL,
                humidity numeric NOT NULL,
                pressure numeric NOT NULL,
                weather text NOT NULL,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            )
            """
        )
        self.cursor.execute(
            f"""
            CREATE UNIQUE INDEX ON {self.table} (labID, date, numGen)
            WHERE numGen IS NOT NULL
            """
        )
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
    ) -> bool:
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
        try:
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
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

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
    ) -> bool:
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
        try:
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
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

    def select(self, labID: str, date: str, numGen: int) -> INFO_TABLE_TYPES:
        """条件に合うレコードを取得

        Args:
            labID (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            numGen (int): 時限

        Returns:
            INFO_TABLE_TYPES: 検索結果
        """
        self.cursor.execute(
            f"""
            SELECT * FROM {self.table}
            WHERE labID = %s and date = %s and numGen = %s
            ORDER BY update_at desc
            """,
            (labID, date, numGen),
        )
        record = self.cursor.fetchone()
        return record

    def remove(self, labID: str, date: str, numGen: int):
        self.cursor.execute(
            f"""
            DELETE FROM {self.table}
            WHERE labID = %s AND date = %s AND numGen = %s
            """,
            (labID, date, numGen),
        )
        self.connection.commit()

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
        record = self.cursor.fetchone()
        return bool(record)

    def registered_rooms(self) -> list[str]:
        """登録済みの研究室一覧

        Returns:
            list[str]: 登録済み研究室
        """
        self.cursor.execute(f"SELECT DISTINCT labID FROM {self.table}")
        records = self.cursor.fetchall()
        rooms = [record[0] for record in records]
        return rooms

    def preview_data(
        self,
    ) -> list[INFO_TABLE_TYPES]:
        """全レコードを取得

        Returns:
            list[INFO_TABLE_TYPES]: 全レコード
        """
        self.cursor.execute(f"SELECT * FROM {self.table} ORDER BY id")
        records = self.cursor.fetchall()
        return records
