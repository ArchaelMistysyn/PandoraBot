# Data handling
import pandas as pd

# Query and Engine handling
from sqlalchemy import text, create_engine

# Session handling
from sqlalchemy.orm import scoped_session, sessionmaker

# Error handling
from mysql.connector.errors import Error as dbError

# Driver import
import pymysql

# Initialize database
db_info = None
with open("bot_db_login.txt", 'r') as data_file:
    for line in data_file:
        db_info = line.split(";")


def start_engine():
    try:
        engine_url = f'mysql+pymysql://{db_info[2]}:{db_info[3]}@{db_info[0]}/{db_info[1]}'
        engine = create_engine(
            engine_url,
            pool_size=10,  # Pool size
            max_overflow=20,  # Max. number of connections including overflow
            pool_recycle=3600,  # Recycle connections after one hour
            pool_timeout=30,  # Timeout for getting a connection from the pool
            echo_pool=True,  # For debugging: Prints pool output to stdout
            pool_pre_ping=True  # Checks for broken connections before using them
        )
        SessionFactory = sessionmaker(bind=engine)
        session_obj = scoped_session(SessionFactory)
        return Database(session_obj)
    except dbError as err:
        print("Database Error: {}".format(err))
        return None


class Database:
    def __init__(self, session):
        self.session = session

    def run_session_query(self, raw_query, return_value=False, batch=False, params=None):
        try:
            query = text(raw_query)
            # Handle query with a return value
            if return_value:
                result = self.session.execute(query, params)
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            # Handle query with no return value
            if batch and params is not None:
                with self.session.begin_nested():
                    for param_set in params:
                        self.session.execute(query, param_set)
                return
            else:
                execution_params = params if params is not None else {}
                if not self.session.is_active:
                    self.session.begin()
                self.session.execute(query, execution_params)
                if not self.session.is_active:
                    self.session.commit()
        except dbError as err:
            self.session.rollback()
            print("Database Error: {}".format(err))

    def close_session(self, exc=None):
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.remove()


pandora_database = start_engine()


def run_query(raw_query, return_value=False, batch=False, params=None):
    return pandora_database.run_session_query(raw_query, return_value=return_value, batch=batch, params=params)


async def close_pandora_database_session():
    pandora_database.close_session()
