import datetime
from decimal import Decimal

from psycopg import sql

from db.infos import InfosManager


class ManualInfosManager(InfosManager):
    INFO_TABLE_TYPES = tuple[
        int,
        str,
        datetime.date,
        datetime.time,
        Decimal,
        Decimal,
        Decimal,
        str,
        datetime.datetime,
        datetime.datetime,
    ]

    def create_table(self) -> None:
        """manual infos用のテーブルを作成"""
        self.cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {table} (
                id serial PRIMARY KEY,
                lab_id text NOT NULL,
                date date NOT NULL,
                time time with time zone,
                temperature numeric NOT NULL,
                humidity numeric NOT NULL,
                pressure numeric NOT NULL,
                weather text NOT NULL,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
                )
                """
            ).format(table=sql.Identifier(self.table))
        )
        self.connection.commit()

    def select(self, lab_id: str, date: str, wrap: bool = False) -> INFO_TABLE_TYPES:
        """条件に合うレコードを取得

        Args:
            lab_id (str): 研究室名
            date (str): 日付 (YYYY-MM-DD形式)

        Returns:
            INFO_TABLE_TYPES: 検索結果
        """
        query = sql.SQL(
            """
            SELECT lab_id, date, temperature, humidity, pressure, weather
            FROM {table}
            WHERE lab_id = %s and date = %s
            ORDER BY update_at desc
            """
        ).format(table=sql.Identifier(self.table))
        params = (lab_id, date)
        record = self.select_one(query, params, wrap=wrap)
        return record

    def _insert(
        self,
        lab_id: str,
        date: str,
        time: str | None,
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
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        query = sql.SQL(
            """
            INSERT INTO {table} (
                lab_id, date, time, temperature, humidity, pressure, weather
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        ).format(table=sql.Identifier(self.table))
        params = (lab_id, date, time, temperature, humidity, pressure, weather)
        return query, params

    def _update(
        self,
        id: int,
        lab_id: str,
        date: str,
        time: str,
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
            temperature (float): 温度
            humidity (float): 湿度
            pressure (float): 気圧
            weather (str): 天気
        """
        query = sql.SQL(
            """
            UPDATE {table} SET
                lab_id = %s,
                date = %s,
                time = %s,
                temperature = %s,
                humidity = %s,
                pressure = %s,
                weather = %s,
                update_at = current_timestamp
                WHERE id = %s
            """
        ).format(table=sql.Identifier(self.table))
        params = (lab_id, date, time, temperature, humidity, pressure, weather, id)
        return query, params

    def preview_data(self, wrap: bool = False) -> list[INFO_TABLE_TYPES]:
        """全レコードを取得

        Args:
            wrap (bool, optional): dict形式で返すか. Defaults to False.

        Returns:
            list[INFO_TABLE_TYPES]: 全レコード
        """
        query = sql.SQL(
            """
            SELECT lab_id, date, time, temperature, humidity, pressure, weather
            FROM {table} ORDER BY id
            """
        ).format(table=sql.Identifier(self.table))
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

        query = sql.SQL(
            "SELECT * FROM {table} WHERE lab_id = %s {manual} ORDER BY date {order}, time {order} LIMIT %s"
        ).format(
            table=sql.Identifier(self.table),
            order=sql.SQL(order),
            manual=sql.SQL("and num_gen IS NULL" if manual_only else ""),
        )
        params = (lab_id, row_limit)

        records = self.select_all(query, params=params, wrap=wrap)
        return records
