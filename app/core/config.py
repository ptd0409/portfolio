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
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        self.JWT_ALGORITHM = "HS256"
        self.JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", 60))
        self.ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
        self.ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


        if not self.DATABASE_URL_ASYNC:
            raise RuntimeError("DATABASE_URL_ASYNC is not set")
        if not self.DATABASE_URL_SYNC:
            raise RuntimeError("DATABASE_URL_SYNC is not set")

settings = Settings()
