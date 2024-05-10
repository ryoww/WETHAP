import os

import dotenv
from db.infos import InfosManager
from db.manual_infos import ManualInfosManager
from db.sender import SenderManager
from utils.ws_manager import SenderWebsocketManager

dotenv.load_dotenv()

db_config = {
    "conninfo": os.environ.get("DB_CONNINFO"),
    "password": os.environ.get("DB_PASSWORD"),
}

ws_manager = SenderWebsocketManager()
infos_manager = InfosManager(table="infos", **db_config)
manual_infos_manager = ManualInfosManager(table="manual_infos", **db_config)
sender_manager = SenderManager(table="senders", **db_config)
