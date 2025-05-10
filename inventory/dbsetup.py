from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

class DataModel:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        sqlite_file_name = "database.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)

    def create_db_and_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()
        yield session
