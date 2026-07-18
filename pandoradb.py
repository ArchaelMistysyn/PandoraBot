# Data handling
import pandas as pd
import time
import asyncio

# Query and Engine handling
from sqlalchemy import text, create_engine

# Session handling
from sqlalchemy.orm import sessionmaker

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
        # Recycle time 6 hours.
        engine = create_engine(engine_url, pool_size=10, max_overflow=20, pool_recycle=43200, pool_pre_ping=True)
        SessionFactory = sessionmaker(bind=engine)
        return Database(SessionFactory)
    except (SQLAlchemyError, pymysql.err.Error) as err:
        print("Database Error: {}".format(err))
        return None


class Database:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _run_query(self, raw_query, return_value=False, batch=False, params=None):
        retries = 0
        query = text(raw_query)

        while retries < 3:
            try:
                with self.session_factory() as session:
                    if return_value:
                        if batch and params is not None:
                            results = []
                            for param_set in params:
                                result = session.execute(query, param_set)
                                results.append(pd.DataFrame(result.fetchall(), columns=result.keys()))
                            return results
                        result = session.execute(query, params or {})
                        return pd.DataFrame(result.fetchall(), columns=result.keys())
                    with session.begin():
                        if batch and params is not None:
                            session.execute(query, params)
                        else:
                            session.execute(query, params or {})
                    return None
            except (SQLAlchemyError, pymysql.err.Error) as err:
                retries += 1
                print(f"Retrying... Attempt {retries}: {err}")
                if retries >= 3:
                    raise
                time.sleep(0.5 * (2 ** retries))

    async def run_session_query(self, raw_query, return_value=False, batch=False, params=None):
        return await asyncio.to_thread(self._run_query, raw_query, return_value, batch, params)


pandora_database = start_engine()


async def run_query(raw_query, return_value=False, batch=False, params=None):
    return await pandora_database.run_session_query(raw_query, return_value=return_value, batch=batch, params=params)

