"""
Routes and views for the flask application.
"""

import urllib2
import sqlite3
from datetime import datetime
from flask import render_template, g, flash, redirect, url_for, request, make_response, jsonify
from GGJ16Flask import app

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

    #try:
    cur = g.db.execute('insert into rituals values (null, ?, ?, ?)', (game_id, player_id, ritual_name))
    g.db.commit()

    id = cur.lastrowid;

    return make_response(str(id), 200)

    #except sqlite3.Error as er:
    #    response = create400('Looks like someone already took that name!')
    #    return response

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

	return render_template(
		'ritual.html',
		title='Play!',
        game_id=url_game_id,
        ritual_id=url_ritual_id
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

@app.route('/ritual/add', methods=['POST'])
def ritual_add():

    cur = g.db.execute('select count from rituals')
    count = cur.fetchone()[0]

    g.db.execute('update rituals set count = ? where id = 0', [count + 1])
    g.db.commit()

    flash('Success!')
    return redirect(url_for('ritual'))

def create400(reason):
    response_dict = {'reason': reason}
    response_body = jsonify(response_dict)

    response = make_response(response_body, 400)
    response.headers['Content-Type'] = 'application/json'

    return response