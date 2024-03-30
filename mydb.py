import pandorabot
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import mysql.connector
from mysql.connector.errors import Error
import pymysql

# Initialize database
db_info = None
with open("bot_db_login.txt", 'r') as data_file:
    for line in data_file:
        db_info = line.split(";")


class Database:
    def __init__(self, database, engine):
        self.database, self.engine = database, engine

    def run_query(self, raw_query, return_value=False, batch=False, params=None):
        try:
            query = text(raw_query)
            # Handle query with a return value
            if return_value:
                output = pd.read_sql(query, self.database, params=params)
                return output
            # Handle query with no return value
            if batch and params is not None:
                with self.database.begin() as trans:
                    for param_set in params:
                        self.database.execute(query, param_set)
            else:
                execution_params = params if params is not None else {}
                self.database.execute(query, execution_params)
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

    def close_engine(self):
        try:
            self.database.close()
            self.engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))


def start_engine():
    try:
        engine_url = f'mysql+pymysql://{db_info[2]}:{db_info[3]}@{db_info[0]}/{db_info[1]}'
        engine = sqlalchemy.create_engine(engine_url)
        my_database = engine.connect()
        database_object = Database(my_database, engine)
        return database_object
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        return None


def run_single_query(raw_query, return_value=False, batch=False, params=None):
    pandora_db = start_engine()
    pandora_db.run_query(raw_query, return_value=return_value, batch=batch, params=params)
    pandora_db.close_engine()