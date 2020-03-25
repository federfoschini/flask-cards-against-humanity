import psycopg2
import os
def connect():
    
    conn = psycopg2.connect(os.environ.connect('DATABASE_URL')
    )

    return conn

