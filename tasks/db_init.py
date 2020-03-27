import psycopg2
import yaml
import os
from pandas import DataFrame

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


sql_create_card_table = """ CREATE TABLE IF NOT EXISTS card (
                        card_id int primary key,
                        expansion text not null,
                        card_type char(1) not null,
                        num_answers int not null,
                        card_text text not null
                        )
                    """

sql_create_player_table = """ CREATE TABLE IF NOT EXISTS player (
                        player_id text primary key,
                        name text not null,
                        is_zar boolean default false,
                        has_played boolean default false,
                        score int default 0
                        )
                    """

sql_create_deck_table = """ CREATE TABLE IF NOT EXISTS deck (
                        card_id int primary key,
                        card_type char(1) not null,
                        num_answers int not null,
                        has_been_drawn boolean default false
                        )
                    """

sql_create_player_hand_table =  """ CREATE TABLE IF NOT EXISTS player_hand (
                        player_id text not null,
                        card_id int not null
                        )
                    """

sql_create_played_card_table =  """ CREATE TABLE IF NOT EXISTS played_card (
                        player_id text not null,
                        card_id int not null
                        )
                    """

sql_create_setting_table =  """ CREATE TABLE IF NOT EXISTS setting (
                        setting_name text not null,
                        setting_json json not null
                        )
                    """
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_card_table)
print('finished sql_create_card_table')
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_player_table)
print('finished sql_create_player_table')
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_deck_table)
    print('finished sql_create_deck_table')
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_player_hand_table)
    print('finished sql_create_player_hand_table')
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_played_card_table)
    print('finished sql_create_played_card_table')
with connect() as conn, conn.cursor() as cursor:
    cursor.execute(sql_create_setting_table)
    print('finished sql_create_setting_table')