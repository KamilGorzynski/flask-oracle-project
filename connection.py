import os
import cx_Oracle
import time


def create_connection():
    connection = None
    while True:
        try:
            dsn_tns = cx_Oracle.makedsn("db", 1521, service_name="xe")
            conn = cx_Oracle.connect(
                user=os.environ.get("ORACLE_USR"),
                password=os.environ.get("ORACLE_PWD"),
                dsn=dsn_tns
            )
        except cx_Oracle.DatabaseError:
            # workaround, waiting while db starts pooling
            print("Connection initializing...")
            time.sleep(3)
            continue
        else:
            connection = conn
            break
    return connection
