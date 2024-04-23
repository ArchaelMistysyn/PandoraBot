# Data handling
import pandas as pd
import time

# Query and Engine handling
from sqlalchemy import text, create_engine

# Session handling
from sqlalchemy.orm import scoped_session, sessionmaker

# Error handling
from mysql.connector.errors import Error as dbError
from sqlalchemy.exc import SQLAlchemyError

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
        engine = create_engine(engine_url, pool_size=10, max_overflow=20, pool_recycle=3600, pool_pre_ping=True)
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
        retries, max_retries, backoff_factor = 0, 3, 0.5

        while retries < max_retries:
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
                    return
            except (SQLAlchemyError, dbError, pymysql.err.OperationalError) as err:
                self.session.rollback()
                retries += 1
                time.sleep(backoff_factor * (2 ** retries))
                print(f"Retrying... Attempt {retries} due to Database Error: {err}")
            except Exception as e:
                print(f"Unhandled exception: {e}")
                break

    def close_session(self, exc=None):
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.remove()


pandora_database = start_engine()


def run_query(raw_query, return_value=False, batch=False, params=None):
    return pandora_database.run_session_query(raw_query, return_value=return_value, batch=batch, params=params)


async def close_database_session():
    pandora_database.close_session()
