from flask import Flask,render_template,jsonify, redirect, request
from init_methods import init_game
from init_methods import init_next_turn
from utils import connect
import psycopg2

app = Flask(__name__)


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
def get_players_table(cursor):
	query = """
	SELECT  player_id, name, is_zar, has_played, score
	FROM player
	"""
	cursor.execute(query)
	columns_player = ['player_id', 'name', 'is_zar', 'has_played', 'score']
	rows = cursor.fetchall()
	players = [{key:val for key,val in zip(columns_player,row)} for row in rows]
	return players

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

def combine_q_a(q_text,a_text):
    
    if '_' in q_text:
        q_a_text = q_text.replace('_',a_text)
    else:
        q_a_text = ' '.join([q_text, a_text])
        
    return q_a_text




@app.route("/")
def hello():
    return "This is card against humanity"

@app.route("/player")
def player():
    return render_template('player.html')

@app.route("/test")
def test():
    return render_template('test.html')

@app.route('/init_page')
def init_page():
	with connect() as conn, conn.cursor() as cursor:
		players_list = get_players_table(cursor)

	return render_template('init_page.html',players_list = players_list)

@app.route('/init_page', methods=['POST'])
def init_games_method():
	name_string = request.form['text']
	names = name_string.split(',')
	init_game(names,num_cards_to_draw=10)
	with connect() as conn, conn.cursor() as cursor:
		players_list = get_players_table(cursor)	

	return render_template('init_page.html',players_list = players_list)


@app.route("/player/<player_id>")
def player_player_id(player_id):

	with connect() as conn, conn.cursor() as cursor:
		turn_complete = False
		num_player = get_num_players(cursor)
		#get player data
		player = get_player(cursor, player_id)
		player_hand = get_player_hand(cursor,player_id)
		played_card = get_played_card(cursor)
		players_list = get_players_table(cursor)	

	if len(played_card) < num_player: 

		return render_template('player.html',
								player = player,
								player_hand = player_hand,
								players_list = players_list,
								turn_complete = turn_complete,
								played_card = played_card )

	else:
		turn_complete = True
		q_text = [card['card_text'] for card in played_card  if card['is_zar']][0]
		combined_played_card = []
		for card in played_card:
		    if not card['is_zar']:
		        updated_card = {}
		        updated_card['player_id'] = card['player_id']
		        updated_card['name'] = card['name']
		        updated_card['card_text'] = combine_q_a(q_text,card['card_text'])
		        combined_played_card.append(updated_card)

		return render_template('player.html',
								player = player,
								player_hand = player_hand,
								players_list = players_list,
								turn_complete = turn_complete,
								played_card = combined_played_card )

@app.route("/player/<player_id>/<card_id>")
def player_player_id_card_id(player_id,card_id):

	with connect() as conn, conn.cursor() as cursor:
		

		short_params = (player_id,)
		long_params = (player_id,card_id)

		#update_player
		query_update = """
		UPDATE player
		SET has_played = true
		WHERE player_id = %s
		"""
		cursor.execute(query_update,short_params)

		#insert card
		query_insert = """
		INSERT INTO played_card (player_id, card_id)
		VALUES (%s,%s)
		ON CONFLICT DO NOTHING
		"""
		#delete card
		query_delete = """
		DELETE FROM player_hand
		WHERE player_id = %s AND card_id = %s
		"""

		cursor.execute(query_insert,long_params)
		cursor.execute(query_delete,long_params)
		

	return redirect(f'/player/{player_id}')

@app.route("/player/<player_id>/declare_winner/<winner_id>")
def player_player_id_declare_winner_winner_id(player_id,winner_id):
	
	with connect() as conn, conn.cursor() as cursor:
		if player_id != winner_id:
			query = """
			UPDATE player
			SET score = score+1
			WHERE player_id = %s
			"""
			params = (winner_id,)
			cursor.execute(query,params)
	init_next_turn()
	return redirect(f'/player/{player_id}')

	
if __name__ == "__main__":

	#app.run(host = '192.168.137.1',port = 5000,debug = True)
	app.run()