import datetime
from decimal import Decimal

from utils.db_util import TableManager


class InfosManager(TableManager):
    INFO_TABLE_TYPES = tuple[
        int,
        str,
        datetime.date,
        datetime.time,
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
                time time with time zone,
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

    def _insert(
        self,
        lab_id: str,
        date: str,
        time: str | None,
        num_gen: int | None,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> tuple[str, tuple]:
        """レコードを追加

        Args:
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            time (str): 時刻
            num_gen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        query = f"""
                INSERT INTO {self.table} (
                    lab_id, date, time, num_gen, temperature, humidity, pressure, weather
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
        params = (lab_id, date, time, num_gen, temperature, humidity, pressure, weather)
        return query, params

    def _update(
        self,
        id: int,
        lab_id: str,
        date: str,
        time: str,
        num_gen: int,
        temperature: float,
        humidity: float,
        pressure: float,
        weather: str,
    ) -> tuple[str, tuple]:
        """レコードを更新

        Args:
            id (int): 変更したいレコードのid
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)
            time (str): 時刻
            num_gen (int): 時限
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        query = f"""
                UPDATE {self.table} SET
                lab_id = %s,
                date = %s,
                time = %s,
                num_gen = %s,
                temperature = %s,
                humidity = %s,
                pressure = %s,
                weather = %s,
                update_at = current_timestamp
                WHERE id = %s
                """
        params = (
            lab_id,
            date,
            time,
            num_gen,
            temperature,
            humidity,
            pressure,
            weather,
            id,
        )
        return query, params

    def _remove(self, id: int) -> tuple[str, tuple]:
        query = f"""
                DELETE FROM {self.table}
                WHERE id = %s
                """
        params = (id,)
        return query, params

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

    def preview_data(self, wrap: bool = False) -> list[INFO_TABLE_TYPES]:
        """全レコードを取得

        Args:
            wrap (bool, optional): dict形式で返すか. Defaults to False.

        Returns:
            list[INFO_TABLE_TYPES]: 全レコード
        """
        query = f"""
            SELECT lab_id, date, time, num_gen, temperature, humidity, pressure, weather
            FROM {self.table} ORDER BY id
            """
        records = self.select_all(query, wrap=wrap)
        return records

    def get_rows(
        self,
        lab_id: str,
        row_limit: int,
        descending: bool = True,
        manual_only: bool = False,
        wrap: bool = False,
    ) -> list[INFO_TABLE_TYPES]:
        """指定した研究室の最新のレコードを取得

        Args:
            lab_id (str): 研究室名
            row_limit (int): 取得したい行数
            descending (bool): date, timeの降順・昇順 どちらでレコード取得するか デフォルトで降順(True)

        Returns:
            list[INFO_TABLE_TYPES]: レコード
        """
        order = "DESC" if descending else "ASC"
        if manual_only:
            query = f"SELECT * FROM {self.table} WHERE lab_id = %s and num_gen = NULL ORDER BY date %s, time %s LIMIT %s;"
        else:
            query = f"SELECT * FROM {self.table} WHERE lab_id = %s ORDER BY date %s, time %s LIMIT %s;"
        params = (lab_id, order, order, row_limit)

        records = self.select_all(query, params=params, wrap=wrap)
        return records
