"""
Routes and views for the flask application.
"""

import urllib2
import sqlite3
from datetime import datetime
from ast import literal_eval
from random import shuffle, randrange
from flask import render_template, g, flash, redirect, url_for, request, make_response, jsonify
from GGJ16Flask import app

ICON_COUNT = 262

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""

    cur = g.db.execute('select id, name from games')
    games = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        games=games
    )
    #return redirect(url_for('ritual'))

@app.route('/create_player', methods=['POST'])
def create_player():
    """Create a new player"""

    try:
        cur = g.db.execute('insert into players values (null, ?)', [request.form['username']])
        g.db.commit()

        id = cur.lastrowid;

        return make_response(str(id), 200)

    except sqlite3.Error as er:
        response = create400('Looks like someone already took that name!')
        return response

@app.route('/create_ritual', methods=['POST'])
def create_ritual():
    """Create a new ritual"""

    game_id = request.form['game_id']
    player_id = request.form['player_id']
    ritual_name = request.form['ritual_name']

    print "Creating for " + str(player_id) + " with name " + ritual_name + " on " + str(game_id)

    try:
        cur = g.db.execute('insert into rituals values (null, ?, ?, ?, ?, ?, ?)', (game_id, player_id, ritual_name, '', '', 0))

        ritual_id = cur.lastrowid;

        cur = g.db.execute('insert into ritual_players values (null, ?, ?, ?)', (game_id, ritual_id, player_id))
        g.db.commit();

        return make_response(str(ritual_id), 200)

    except sqlite3.Error as er:
        response = create400('Looks like someone already took that name!')
        return response

@app.route('/play/<url_game_id>')
def join_ritual(url_game_id):
    """Renders the ritual joining page"""

    cur = g.db.execute(
        'select rituals.id, rituals.game_id, players.name, rituals.name, count(ritual_players.id)'
        ' from rituals'
        ' inner join players'
        ' on rituals.leader_id=players.id'
        ' left join ritual_players'
        ' on rituals.game_id=ritual_players.game_id'
        ' and rituals.id=ritual_players.ritual_id'
        ' where rituals.game_id = ?'
        ' group by rituals.id'
        ' order by rituals.id asc',
        url_game_id
        )
    rituals = [dict(id=row[0], game_id=row[1], leader_name=row[2], name=row[3], count=row[4]) for row in cur.fetchall()]

    return render_template(
        'join_ritual.html',
        title='Join or Create Ritual',
        year=datetime.now().year,
        name=urllib2.unquote(request.cookies.get('username')),
        rituals=rituals
    )

@app.route('/play/<url_game_id>/<url_ritual_id>')
def ritual(url_game_id, url_ritual_id):
    """Renders the ritual page."""

    player_id = request.cookies.get('id')

    sequence, _ = get_sequence(url_game_id, url_ritual_id)
    if find_player_icon_in_sequence(sequence, player_id) == -1:

        cur = g.db.execute('insert into ritual_players values (null, ?, ?, ?)', (url_game_id, url_ritual_id, player_id))

        players = get_players_for_ritual(url_game_id, url_ritual_id)

        sequence = create_ritual_sequence(players)

        cur = g.db.execute('update rituals set sequence = ? where game_id = ? and id = ?', (str(sequence), url_game_id, url_ritual_id))

        g.db.commit()

    icon_indices = [randrange(262) for i in range(9)]

    #next_icon = randrange(262)

    sequence, _ = get_sequence(url_game_id, url_ritual_id)
    icon = find_player_icon_in_sequence(sequence, player_id)

    icon_indices.append(icon)
    shuffle(icon_indices)

    #print "Player icon: " + str(icon)

    sequence, _ = get_sequence(url_game_id, url_ritual_id)
    next_player_id = find_next_player_in_sequence(sequence, player_id)

    next_icon = find_player_icon_in_sequence(sequence, str(next_player_id))

    next_player = "You're the end!"
    print "Next Player: " + str(next_player_id)
    if next_player_id != -1:
        next_player = get_player_name_for_id(next_player_id)

    return render_template(
	    'ritual.html',
	    title='Play!',
        game_id=url_game_id,
        ritual_id=url_ritual_id,
        icon_indices=icon_indices,
        next_icon_id=next_icon,
        next_player=next_player
	)

@app.route('/play/<url_game_id>/<url_ritual_id>', methods=['POST'])
def ritual_post(url_game_id, url_ritual_id):
    """Handles ritual inputs."""

    player_id_str = request.form['player_id']
    player_id = literal_eval(player_id_str)
    choice_str = request.form['choice']
    choice = literal_eval(choice_str)

    sequence, last_in_seq = get_sequence(url_game_id, url_ritual_id)
    last_index = find_in_sequence(sequence, last_in_seq)

    #print "Sequence: " + str(sequence)

    #print "Player ID: " + str(player_id)

    #print "Next player: " + str(find_next_player_in_sequence(sequence, player_id))

    choice_tuple = (player_id, choice)
    new_index = find_in_sequence(sequence, choice_tuple)

    if new_index > last_index:
        cur = g.db.execute('select points from rituals where game_id = ? and id = ?', (url_game_id, url_ritual_id))
        multiplier = get_ritual_population(url_game_id, url_ritual_id)
        points = cur.fetchone()[0] + (1 * multiplier)
        cur = g.db.execute('update rituals set points = ? where game_id = ? and id = ?', (str(points), url_game_id, url_ritual_id))

    cur = g.db.execute('update rituals set last_in_sequence = ? where game_id = ? and id = ?', (str(choice_tuple), url_game_id, url_ritual_id))

    g.db.commit()

    #print new_index

    return make_response("", 201)

@app.route('/spectate/<url_game_id>')
def spectate(url_game_id):
    """Renders the spectator page."""

    rituals = get_progress(url_game_id)

    return render_template(
        'spectate.html',
        title='Spectate',
        year=datetime.now().year,
        rituals=rituals
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

def create400(reason):
    response_dict = {'reason': reason}
    response_body = jsonify(response_dict)

    response = make_response(response_body, 400)
    response.headers['Content-Type'] = 'application/json'

    return response

def create_ritual_sequence(players):
    player_sequence = [(playerid, randrange(ICON_COUNT)) for playerid in players]

    shuffle(player_sequence)

    return player_sequence

def get_players_for_ritual(game_id, ritual_id):
    cur = g.db.execute(
        'select player_id from ritual_players where game_id = ? and ritual_id = ?',
        (game_id, ritual_id)
        )

    player_ids = [row[0] for row in cur.fetchall()]
    return player_ids

def get_sequence(game_id, ritual_id):
    cur = g.db.execute(
        'select sequence, last_in_sequence from rituals where game_id = ? and id = ?',
        (game_id, ritual_id)
        )

    row = cur.fetchone()
    sequence_str = row[0]
    last_in_seq_str = row[1]

    sequence = []
    last_in_seq = ()

    if sequence_str:
        sequence = literal_eval(sequence_str)

    if last_in_seq_str:
        last_in_seq = literal_eval(last_in_seq_str)

    return sequence, last_in_seq

def get_progress(game_id):
    cur = g.db.execute(
        'select name, points from rituals where game_id = ?',
        (game_id)
        )

    return [create_ritual_progress(row) for row in cur.fetchall()]

def create_ritual_progress(db_row):
    return { 'name': db_row[0], 'progress': db_row[1] / 2 }

def get_ritual_population(game_id, ritual_id):
    cur = g.db.execute(
        'select count(*) from ritual_players where game_id = ? and ritual_id = ?',
        (game_id, ritual_id)
        )

    return cur.fetchone()[0]

def get_player_name_for_id(player_id):

    print "Get player: " + str(player_id)

    cur = g.db.execute(
        'select name from players where id = ?',
        ([str(player_id)])
        )

    return cur.fetchone()[0]

def find_in_sequence(sequence, entry):
    if not entry or not sequence:
        return -1

    for i, seq_val in enumerate(sequence):
        if entry[0] == seq_val[0]:
            return i

    return -1

def find_player_icon_in_sequence(sequence, player_id):
    if not sequence:
        return -1
    
    player_id_int = literal_eval(player_id)

    #print sequence

    for seq_val in sequence:
        #print "Player ID: " + player_id + " seq_val: " + str(seq_val[0])
        if seq_val[0] == player_id_int:
            #print "Found player, i: " + str(i) + " length - 1: " + str(len(sequence) - 1)
            return seq_val[1]

    return -1

def find_next_player_in_sequence(sequence, player_id):
    if not sequence:
        return -1
    
    player_id_int = literal_eval(player_id)

    #print sequence

    for i, seq_val in enumerate(sequence):
        #print "Player ID: " + player_id + " seq_val: " + str(seq_val[0])
        if seq_val[0] == player_id_int:
            #print "Found player, i: " + str(i) + " length - 1: " + str(len(sequence) - 1)
            if i < len(sequence) - 1:
                return sequence[i + 1][0]

    return -1