import psycopg2
from random import sample
import json

def connect():
    db = {
    "host":"localhost",
    "database":"cah",
    "user":"postgres",
    "port":5433,
    "password":"nopwd"
    }
    conn = psycopg2.connect(
    	host = db['host'],
    	database = db['database'],
    	user = db['user'],
    	port = db['port'],
    	password = db['password'],
    )

    return conn

def reset_deck():
    with connect() as conn, conn.cursor() as cursor:
        query = "UPDATE  deck SET has_been_drawn = false"
        cursor.execute(query)


def upload_card(cursor,player_id,card_id):

    query = """
        INSERT INTO player_hand(player_id,card_id)
         VALUES (%s,%s)
        """
    params = (player_id,str(card_id))
    cursor.execute(query,params)

def reset_played_card(cursor):
    query = """DELETE FROM played_card"""
    cursor.execute(query)
    
def reset_player(cursor):
    
    query = """
    UPDATE player
    SET is_zar=false,has_played = false
    """
    cursor.execute(query)

def get_players_id_list(cursor):
    
    query_player_list = "SELECT (setting_json) FROM setting where setting_name = 'players_id_list'"
    cursor.execute(query_player_list)
    players_id_list = cursor.fetchall()[0][0]
    
    return players_id_list

def get_current_zar(cursor):
    
    query_current_player = "SELECT player_id FROM player where is_zar"
    cursor.execute(query_current_player)
    curr_zar_id = cursor.fetchall()[0][0]
    return curr_zar_id

def update_zar(cursor,curr_zar_id,players_id_list):
    
    curr_zar_pos = players_id_list.index(curr_zar_id)
    print(curr_zar_pos)
    if curr_zar_pos == (len(players_id_list)-1):
        next_zar_pos = 0
    else: 
        next_zar_pos = curr_zar_pos + 1
    
    reset_player(cursor)
    
    next_zar_id = players_id_list[next_zar_pos]
    
    
    init_zar(cursor,next_zar_id)

def draw_card_id(cursor, card_type, num_cards_to_draw):

    query = """
    SELECT  card_id FROM  deck
    WHERE  card_type = %s AND NOT has_been_drawn
    """
    params = (card_type,)
    cursor.execute(query,params)
    rows = cursor.fetchall()
    valid_id_list = [el[0] for el in rows]

    card_id_drawn = tuple(sample(valid_id_list,num_cards_to_draw))


    query = """
    UPDATE deck     
    SET has_been_drawn = true
    WHERE  card_id  in %s
    """
    params = (card_id_drawn,)
    cursor.execute(query,params)

    return card_id_drawn