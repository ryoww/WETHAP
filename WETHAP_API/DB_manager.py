import datetime
from decimal import Decimal

import psycopg2


class tableManager:
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

    def preview_data(self):
        """全レコードを取得"""
        self.cursor.execute(f"SELECT * FROM {self.table}")
        response = self.cursor.fetchall()
        return response

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
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            );
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
    ) -> list[INFO_TABLE_TYPES]:
        """全レコードを取得

        Returns:
            list[INFO_TABLE_TYPES]: 全レコード
        """
        self.cursor.execute(f"SELECT * FROM {self.table} ORDER BY id")
        response = self.cursor.fetchall()
        return response


class senderManager(tableManager):
    def create_table(self) -> None:
        """WETHAP sender用のtableを作成"""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id bytea PRIMARY KEY,
                labID text,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            );
            """
        )
        self.connection.commit()

    def get_labID(self, id: bytearray):
        """端末に割り当てられているlabIDを取得

        Args:
            id (bytearray): 端末固有id
        """
        self.cursor.execute(
            f"""SELECT labID FROM {self.table} WHERE id = %s ORDER BY update_at""",
            (id,),
        )
        response = self.cursor.fetchall()
        return response[-1] if response else None

    def get_all_labID(self):
        """端末に割り当てられているlabIDの一覧を取得"""
        self.cursor.execute(f"""SELECT DISTINCT labID FROM {self.table}""")
        response = self.cursor.fetchall()
        return response[-1] if response else None


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
    # print(infos_manager.preview_data())
    # infos_manager.delete_table()
    # infos_manager.create_table()
    # infos_manager.insert("テスト", str(datetime.date.today()), 0.0, 0.0, 0.0, 0.0, "晴れ")
    # infos_manager.update(10, "更新", str(datetime.date.today()), 1.0, 1.0, 1.0, 1.0, "雨")
    print(infos_manager.preview_data())
    infos_manager.close()

    sender_manager = senderManager("sender", **db_config)
    sender_manager.init_table()
    print(sender_manager.preview_data())
    sender_manager.close()
