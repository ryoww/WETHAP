import os

import dotenv
from db.infos import infosManager
from db.sender import senderManager
from utils.ws_manager import websocketManager

dotenv.load_dotenv()

db_config = {
    "conninfo": os.environ.get("DB_CONNINFO"),
    "password": os.environ.get("DB_PASSWORD"),
}

ws_manager = websocketManager()
infos_manager = infosManager(table="infos", **db_config)
sender_manager = senderManager(table="senders", **db_config)
