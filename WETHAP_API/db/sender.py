import datetime

from utils.db_util import TableManager


class SenderManager(TableManager):
    @property
    def column_info(self) -> dict[str, type]:
        column_info = {
            "id": int,
            "uuid": str,
            "identifier": str,
            "lab_id": str,
            "create_at": datetime.datetime,
            "update_at": datetime.datetime,
        }
        return column_info

    def create_table(self) -> None:
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY,
                uuid text UNIQUE NOT NULL,
                identifier text UNIQUE NOT NULL,
                lab_id text UNIQUE,
                create_at timestamptz NOT NULL DEFAULT current_timestamp,
                update_at timestamptz NOT NULL DEFAULT current_timestamp
            )
            """
        )
        self.connection.commit()

    def _insert(self, uuid: str, identifier: str, lab_id: str) -> tuple[str, tuple]:
        query = f"""
                INSERT INTO {self.table} (uuid, identifier, lab_id)
                VALUES (%s, %s, %s)
                """
        params = (uuid, identifier, lab_id)
        return query, params

    def _update(self, id: int, after_lab_id: str) -> tuple[str, tuple]:
        query = f"""
                UPDATE {self.table} SET
                lab_id = %s,
                update_at = current_timestamp
                WHERE id = %s
                """
        params = (after_lab_id, id)
        return query, params

    def _remove(self, uuid: str) -> tuple[str, tuple]:
        query = f"""
                DELETE FROM {self.table}
                WHERE uuid = %s
                """
        params = (uuid,)
        return query, params

    def select(
        self,
        id: int = None,
        uuid: str = None,
        identifier: str = None,
        lab_id: str = None,
        wrap: bool = False,
    ):
        input_query = []
        input_params = []
        if id is not None:
            input_query.append("id = %s")
            input_params.append(id)
        if uuid is not None:
            input_query.append("uuid = %s")
            input_params.append(uuid)
        if identifier is not None:
            input_query.append("identifier = %s")
            input_params.append(identifier)
        if lab_id is not None:
            input_query.append("lab_id = %s")
            input_params.append(lab_id)
        if len(input_query) <= 0:
            raise ValueError
        query = f"""
                SELECT * FROM {self.table}
                WHERE {' AND '.join(input_query)}
                """
        record = self.select_one(query, input_params, wrap)
        return record

    def get_lab_id(self, id: str):
        """端末に割り当てられているlab_idを取得

        Args:
            id (str): 端末固有id
        """
        self.cursor.execute(
            f"""SELECT lab_id FROM {self.table} WHERE id = %s""",
            (id,),
        )
        record = self.cursor.fetchone()[0]
        return record

    def get_all_lab_id(self):
        """端末に割り当てられているlab_idの一覧を取得"""
        self.cursor.execute(f"""SELECT lab_id FROM {self.table}""")
        records = self.cursor.fetchall()
        lab_ids = [record[0] for record in records]
        return lab_ids

    def change_lab_id(self, before_lab_id: str, after_lab_id: str):
        query = f"""
                UPDATE {self.table} SET
                lab_id = %s, update_at = current_timestamp
                WHERE lab_id = %s
                """
        params = (after_lab_id, before_lab_id)

        self.transaction(query, params)

    def get_lab_id_from_identifier(self, identifier: str):
        self.cursor.execute(
            f"""
            SELECT lab_id FROM {self.table}
            WHERE identifier = %s
            """,
            (identifier,),
        )
        record = self.cursor.fetchone()[0]
        return record
