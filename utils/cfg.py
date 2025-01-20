import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))


@dataclass
class ConfigDB():
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    QUEUE_DB_NAME: str = os.getenv("QUEUE_DB_NAME")


cfg_db: ConfigDB = ConfigDB()
