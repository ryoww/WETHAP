import sqlite3

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


    def previewData(self):
        self.cursor.execute("SELECT * FROM infos")
        response = self.cursor.fetchall()

        return response


    def isRegistered(
        self,
        labID: str
    ):
        self.cursor.execute(f"SELECT DISTINCT labID FROM infos WHERE labID = '{labID}'")
        response = self.cursor.fetchall()
        
        if response:
            return True
        else:
            return False

    def registeredRooms(self):
        self.cursor.execute(f"SELECT DISTINCT labID FROM infos")
        
        response = self.cursor.fetchall()
        rooms = [i[0] for i in response]
        return rooms

    def select(
        self,
        date: str,
        labID: str,
        numGen: int
    ):
        self.cursor.execute(f"SELECT * FROM infos WHERE labID = '{labID}' and date = '{date}' and numGen = {numGen}")
        data = self.cursor.fetchall()
        return data[0] if data else None


    def close(self):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    # DBへ接続
    db = DBCommands(DB_PATH = "./data.db")

    # WETHAP用のDBテーブルのテンプレートを作る
    db.createDB()

    # 登録されている研究室か(Boolean)
    print(db.isRegistered("テスト研究室"))
    
    # 登録されている研究室一覧を配列で取得
    print(db.registeredRooms())

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
    print(db.select(labID = "テスト研究室", date = "1970-1-1", numGen = 1))

    # DBの状態を保存、DBの接続を終了する
    db.close()