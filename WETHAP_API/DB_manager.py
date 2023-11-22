import datetime
from decimal import Decimal
import psycopg2
from utils.db_util import tableManager


class infosManager(tableManager):
    COLUMN_INFO = {
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
                labID text,
                date date,
                numGen integer,
                temperature numeric,
                humidity numeric,
                pressure numeric,
                weather text,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp,
                UNIQUE (labID, date, numGen)
            )
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
        except psycopg2.errors.DatabaseError:
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
        except psycopg2.errors.DatabaseError:
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
        records = self.cursor.fetchall()
        return records[0] if records else None

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
        records = self.cursor.fetchall()
        return bool(records)

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


class senderManager(tableManager):
    COLUMN_INFO = {
        "id": int,
        "uuid": str,
        "labID": str,
        "create_at": datetime.datetime,
        "update_at": datetime.datetime,
    }

    def create_table(self) -> None:
        """WETHAP sender用のtableを作成"""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY NOT NULL,
                uuid text UNIQUE NOT NULL,
                labID text UNIQUE,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            )
            """
        )
        self.connection.commit()

    def insert(self, uuid: str, labID: str):
        try:
            self.cursor.execute(
                f"""
                INSERT INTO {self.table} (uuid, labID)
                VALUES (%s, %s)
                """,
                (uuid, labID),
            )
        except psycopg2.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

    def select(self, id: int = None, uuid: str = None, labID: str = None):
        where = ([], [])
        if id is not None:
            where[0].append("id = %s")
            where[1].append(id)
        if uuid is not None:
            where[0].append("uuid = %s")
            where[1].append(uuid)
        if labID is not None:
            where[0].append("labID = %s")
            where[1].append(labID)
        if len(where[0]) <= 0:
            raise ValueError
        self.cursor.execute(
            f"""
            SELECT * FROM {self.table}
            WHERE {' AND '.join(where[0])}
            """,
            (*where[1],),
        )
        record = self.cursor.fetchall()
        return record[0] if record else None

    def get_labID(self, id: str):
        """端末に割り当てられているlabIDを取得

        Args:
            id (str): 端末固有id
        """
        self.cursor.execute(
            f"""SELECT labID FROM {self.table} WHERE id = %s""",
            (id,),
        )
        response = self.cursor.fetchall()
        return response[0] if response else None

    def get_all_labID(self):
        """端末に割り当てられているlabIDの一覧を取得"""
        self.cursor.execute(f"""SELECT labID FROM {self.table}""")
        response = self.cursor.fetchall()
        return response[0] if response else None

    def change_labID(self, id: int, labID: str):
        self.cursor.execute(
            f"""
            UPDATE {self.table} SET
            labID = %s, update_at = current_timestamp
            WHERE id = %s
            """,
            (labID, id),
        )
        self.connection.commit()


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
    infos_manager = infosManager(table="infos", **db_config)
    infos_manager.init_table()
    # print(infos_manager.preview_data())
    # infos_manager.delete_table()
    # infos_manager.create_table()
    # infos_manager.insert("テスト", str(datetime.date.today()), 0.0, 0.0, 0.0, 0.0, "晴れ")
    # infos_manager.update(10, "更新", str(datetime.date.today()), 1.0, 1.0, 1.0, 1.0, "雨")
    print(infos_manager.preview_data())
    infos_manager.close()

    sender_manager = senderManager("sender", **db_config)
    sender_manager.init_table()
    print(sender_manager.fetch_all())
    sender_manager.close()
