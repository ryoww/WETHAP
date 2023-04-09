import sqlite3
import json

class DBCommands:
    def __init__(self, DB_PATH):
        self.DB_PATH = DB_PATH
        self.connection = sqlite3.connect(self.DB_PATH)
        self.cursor = self.connection.cursor()

    def createDB(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS infos(labID TEXT, date DATE, numGen INTEGER, temperature INTEGER, humidity INTEGER, pressure INTEGER, weather TEXT)")

    def insert(
        self,
        labID: str,
        date: str,
        numGen: int,
        temperature: int,
        humidity: int,
        pressure: int,
        weather: str
    ):
        self.cursor.execute(f"INSERT INTO infos VALUES('{labID}', '{date}', {numGen}, {temperature}, {humidity}, {pressure}, '{weather}')")

    def select(
        self,
        date: str,
        labID: str,
        numGen: int
    ):
        self.cursor.execute(f"SELECT * FROM infos WHERE labID = '{labID}' and date = '{date}' and numGen = {numGen}")
        data = self.cursor.fetchall()
        return data[0] if len(data) == 1 else None

    def close(self):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    # DBへ接続
    db = DBCommands(DB_PATH = "./test.db")

    # WETHAP用のDBテーブルのテンプレートを作る
    db.createDB()

    # データを挿入する
    db.insert(
        labID = "テスト研究室",
        date = "1970-1-1",
        numGen = 1,
        temperature = 0,
        humidity = 0,
        pressure = 0,
        weather = "晴れ")

    # 条件に合ったデータを、レコードをタプルとした配列で取得
    data = db.select(labID = "テスト研究室", date = "1970-1-1", numGen = 1)
    print(data)

    # DBの状態を保存、DBの接続を終了する
    db.close()