import psycopg2
from random import sample
from db_operation import reset_deck
from db_operation import connect
from db_operation import upload_card,reset_player,reset_played_card
from db_operation import reset_played_card
from db_operation import reset_player
from db_operation import get_players_id_list
from db_operation import get_current_zar
from db_operation import update_zar
from db_operation import draw_card_id
import json
import uuid
def play_answer_card(cursor,player_id,card_id):
    
    params = (player_id,card_id)
    #insert card
    query_insert = """
    INSERT INTO played_card (player_id, card_id)
    VALUES (%s,%s)
    ON CONFLICT DO NOTHING
    """
    
    query_delete = """
    DELETE FROM player_hand
    WHERE player_id = %s AND card_id = %s
    """
    cursor.execute(query_insert,params)
    cursor.execute(query_delete,params)
    return None

def init_player(cursor,player_id,name,card_id_drawn):
    query = """
    INSERT INTO  player (player_id, name)
    VALUES(%s,%s)
    """
    params = (player_id,name)
    cursor.execute(query,params)
    for card_id in card_id_drawn:
        upload_card(cursor,player_id,card_id)

def init_zar(cursor,player_id):
	query ="""UPDATE player
				SET is_zar = true, has_played = true
				where player_id =%s"""
	params = (player_id,)
	cursor.execute(query,params)


	card_type = 'Q'
	num_cards_to_draw = 1
	card_id_drawn = draw_card_id(cursor, card_type, num_cards_to_draw)
	query = """
	        INSERT INTO  played_card (player_id, card_id)
	        VALUES(%s,%s)
	        """
	params = (player_id,card_id_drawn[0],)
	cursor.execute(query,params)
    
def init_next_turn():
    
    with connect() as conn, conn.cursor() as cursor:
        players_id_list = get_players_id_list(cursor)
        curr_zar_id = get_current_zar(cursor)
        
        reset_played_card(cursor)
        
        for player_id in players_id_list:
            if player_id != curr_zar_id:
                card_id_drawn = draw_card_id(cursor, 'A', 1)
                for card_id in card_id_drawn:
                    upload_card(cursor,player_id,card_id)
             
        update_zar(cursor,curr_zar_id,players_id_list)




def init_setting(players_id_list):

	with connect() as conn, conn.cursor() as cursor:
		query_clear = """
			DELETE FROM setting WHERE setting_name = 'players_id_list'
		"""

		cursor.execute(query_clear)

		query_upload = """
			INSERT INTO setting
			(setting_name,setting_json)
			VALUES('players_id_list',%s)
		"""
		params = (json.dumps(players_id_list),)

		cursor.execute(query_upload,params)

def init_game(names,num_cards_to_draw=10):
	
	reset_deck()

	with connect() as conn, conn.cursor() as cursor:
		query = """
		DELETE FROM  player;
		DELETE FROM  player_hand;
		DELETE FROM played_card;
		"""
		cursor.execute(query)
		card_type = 'A'
		zar_initialized = False
		players_id_list = []
		for name in names:
			player_id = str(uuid.uuid4())
			card_id_drawn = draw_card_id(cursor, card_type, num_cards_to_draw)
			init_player(cursor,player_id,name,card_id_drawn)

			if zar_initialized == False:
				init_zar(cursor,player_id)
				zar_initialized = True
			players_id_list.append(player_id)

		init_setting(players_id_list)
		#init played_card

def get_player(cursor, player_id):

	#get player data
	query = """
	SELECT  player_id, name, is_zar, has_played, score
	FROM player
	WHERE  player_id = %s
	"""
	params = (player_id,)
	cursor.execute(query,params)
	row = cursor.fetchall()
	player = {}
	if len(row)>0:
	    columns_player = ['player_id', 'name', 'is_zar', 'has_played', 'score']
	    
	    player = {col_name:col_value for col_name,col_value in zip(columns_player,row[0])}

	return player

def get_player_hand(cursor,player_id):

	query = """
		    SELECT P.card_id,C.card_text
		    FROM player_hand P JOIN card C on P.card_id = C.card_id 
		    where P.player_id = %s
		    """
	columns_card = ['card_id','card_text']
	params = (player_id,)
	cursor.execute(query, params)
	player_hand_tups = cursor.fetchall()

	player_hand = {}
	if len(player_hand_tups)>0:

	    player_hand = [{'card_num':i+1,'card_id':card[0],'card_text':card[1]} 
	    				for i,card in enumerate (player_hand_tups)]

	return player_hand

def get_played_card(cursor):

	query = """
		SELECT p.player_id, p.name, p.is_zar,pc.card_id,c.card_text
		FROM played_card PC 
		JOIN player P ON pc.player_id= p.player_id 
		JOIN card C on pc.card_id=c.card_id
	"""

	cursor.execute(query)

	rows = cursor.fetchall()

	columns_played_card = ['player_id', 'name', 'is_zar','card_id','card_text']
	    
	played_card = [{col_name:col_value for col_name,col_value in zip(columns_played_card,row)}
	for row in rows]

	return played_card
def get_num_players(cursor):

	query = "SELECT COUNT (*) FROM player"
	cursor.execute(query)

	num_players = cursor.fetchall()[0][0]
	return num_players	