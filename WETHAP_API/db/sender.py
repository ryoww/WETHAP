import datetime

import psycopg
from utils.db_util import tableManager


class senderManager(tableManager):
    @property
    def column_info(self) -> dict[str, type]:
        column_info = {
            "id": int,
            "uuid": str,
            "labID": str,
            "create_at": datetime.datetime,
            "update_at": datetime.datetime,
        }
        return column_info

    def create_table(self) -> None:
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
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            self.connection.commit()
            return True

    def update(self, before_labID: str, after_labID: str):
        try:
            self.cursor.execute(
                f"""
                UPDATE {self.table} SET
                labID = %s,
                update_at = current_timestamp
                WHERE labID = %s
                """,
                (after_labID, before_labID),
            )
            self.connection.commit()
        except psycopg.errors.DatabaseError:
            self.connection.rollback()
            return False
        else:
            return True

    def remove(self, uuid: str):
        self.cursor.execute(
            f"""
            DELETE FROM {self.table}
            WHERE uuid = %s
            """,
            (uuid,),
        )
        self.connection.commit()

    def select(
        self, id: int = None, uuid: str = None, labID: str = None, wrap: bool = False
    ):
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
        if wrap:
            record = self.dict_cursor.fetchone()
        else:
            record = self.cursor.fetchone()
        return record

    def get_labID(self, id: str):
        """端末に割り当てられているlabIDを取得

        Args:
            id (str): 端末固有id
        """
        self.cursor.execute(
            f"""SELECT labID FROM {self.table} WHERE id = %s""",
            (id,),
        )
        record = self.cursor.fetchone()
        return record

    def get_all_labID(self):
        """端末に割り当てられているlabIDの一覧を取得"""
        self.cursor.execute(f"""SELECT labID FROM {self.table}""")
        records = self.cursor.fetchall()
        labIDs = [record[0] for record in records]
        return labIDs

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
