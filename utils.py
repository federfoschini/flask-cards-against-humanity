import psycopg2
import os
def connect():
    db = {
    "host":"localhost",
    "database":"cah",
    "user":"postgres",
    "port":5433,
    "password":"nopwd",

    }
    conn = psycopg2.connect(host = db['host'],database = db['database'],user = db['user'],port = db['port'],
    password = db['password'],
    )

    return conn

