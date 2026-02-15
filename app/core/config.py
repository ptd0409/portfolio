import os
from dotenv import load_dotenv

load_dotenv()

class Settings():
    def __init__(self):
        self.APP_NAME = os.environ.get("APP_NAME")
        self.APP_ENV = os.environ.get("APP_ENV")
        self.DATABASE_URL_ASYNC = os.environ.get("DATABASE_URL_ASYNC")
        self.DATABASE_URL_SYNC = os.environ.get("DATABASE_URL_SYNC")
        self.ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")

        if not self.DATABASE_URL_ASYNC:
            raise RuntimeError("DATABASE_URL_ASYNC is not set")
        if not self.DATABASE_URL_SYNC:
            raise RuntimeError("DATABASE_URL_SYNC is not set")

settings = Settings()
