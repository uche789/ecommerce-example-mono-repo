from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

class DataModel:
    def __init__(self):
        sqlite_file_name = "database.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)

    def create_db_and_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        yield session
    