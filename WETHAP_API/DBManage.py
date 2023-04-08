import sqlite3

class DBCommands:

    def __init__(self, DB_PATH):
        self.DB_PATH = DB_PATH
        self.connection = sqlite3.connect(self.DB_PATH)
        self.cursor = self.connection.cursor()


    def createDB(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS infos(labID TEXT, numGen INTEGER, temperature INTEGER, humidity INTEGER, pressure INTEGER, weather TEXT)")


    def insert(
        self,
        labID: str,
        numGen: int,
        temperature: int,
        humidity: int,
        pressure: int,
        weather: str):
        self.cursor.execute(f"INSERT INTO infos VALUES('{labID}', {numGen}, {temperature}, {humidity}, {pressure}, '{weather}')")


    def select(
        self,
        labID: str,
        numGen: int):
        self.cursor.execute(f"SELECT * FROM  infos WHERE labID = '{labID}' and numGen = {numGen}")
        return self.cursor.fetchall()[0]


    def close(self):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    DBManage = DBCommands(DB_PATH = "./test.db")
    DBManage.createDB()
    DBManage.insert(
        labID = "ゆゆゆ",
        numGen = 4,
        temperature = 20.0,
        humidity = 30.0,
        pressure = 1000,
        weather = "晴れ")
    data = DBManage.select(labID = "みみみ", numGen = 3)
    DBManage.close()

    print(data)