import datetime
from decimal import Decimal

import psycopg
from utils.db_util import TableManager


class InfosManager(TableManager):
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

    def create_table(self) -> None:
        """WETHAP infos用のテーブルを作成"""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY,
                lab_id text NOT NULL,
                date date NOT NULL,
                num_gen integer,
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
            CREATE UNIQUE INDEX ON {self.table} (lab_id, date, num_gen)
            WHERE num_gen IS NOT NULL
            """
        )
        self.connection.commit()

    def insert(
        self,
        lab_id: str,
        date: str,
        num_gen: int,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> bool:
        """レコードを追加

        Args:
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            num_gen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        try:
            self.cursor.execute(
                f"""
                INSERT INTO {self.table} (
                    lab_id, date, num_gen, temperature, humidity, pressure, weather
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (lab_id, date, num_gen, temperature, humidity, pressure, weather),
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
        lab_id: str,
        date: str,
        num_gen: int,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> bool:
        """レコードを更新

        Args:
            id (int): 変更したいレコードのid
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            num_gen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        try:
            self.cursor.execute(
                f"""
                UPDATE {self.table} SET
                lab_id = %s,
                date = %s,
                num_gen = %s,
                temperature = %s,
                humidity = %s,
                pressure = %s,
                weather = %s,
                update_at = current_timestamp
                WHERE id = %s
                """,
                (lab_id, date, num_gen, temperature, humidity, pressure, weather, id),
            )
            self.connection.commit()
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

    def select(self, lab_id: str, date: str, num_gen: int) -> INFO_TABLE_TYPES:
        """条件に合うレコードを取得

        Args:
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            num_gen (int): 時限

        Returns:
            INFO_TABLE_TYPES: 検索結果
        """
        self.cursor.execute(
            f"""
            SELECT lab_id, date, num_gen, temperature, humidity, pressure, weather
            FROM {self.table}
            WHERE lab_id = %s and date = %s and num_gen = %s
            ORDER BY update_at desc
            """,
            (lab_id, date, num_gen),
        )
        record = self.cursor.fetchone()
        return record

    def remove(self, lab_id: str, date: str, num_gen: int):
        self.cursor.execute(
            f"""
            DELETE FROM {self.table}
            WHERE lab_id = %s AND date = %s AND num_gen = %s
            """,
            (lab_id, date, num_gen),
        )
        self.connection.commit()

    def is_registered(self, lab_id: str) -> bool:
        """登録済みの研究室か

        Args:
            lab_id (str): 研究室名

        Returns:
            bool: 判定結果
        """
        self.cursor.execute(
            f"SELECT DISTINCT lab_id FROM {self.table} WHERE lab_id = %s", (lab_id,)
        )
        record = self.cursor.fetchone()
        return bool(record)

    def registered_rooms(self) -> list[str]:
        """登録済みの研究室一覧

        Returns:
            list[str]: 登録済み研究室
        """
        self.cursor.execute(f"SELECT DISTINCT lab_id FROM {self.table}")
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
        self.cursor.execute(
            f"""
            SELECT lab_id, date, num_gen, temperature, humidity, pressure, weather
            FROM {self.table} ORDER BY id
            """
        )
        records = self.cursor.fetchall()
        return records
