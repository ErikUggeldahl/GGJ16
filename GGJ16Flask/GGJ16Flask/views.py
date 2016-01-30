"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, g, flash, redirect, url_for
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

@app.route('/play/<url_game_id>')
def join_ritual(url_game_id):
    """Renders the ritual joining page"""

    cur = g.db.execute(
        'select rituals.id, rituals.game_id, players.name, rituals.name, count(ritual_players.ritual_id)'
        ' from rituals'
        ' inner join players'
        ' on rituals.leader_id=players.id'
        ' left join ritual_players'
        ' on rituals.game_id=ritual_players.game_id'
        ' and rituals.id=ritual_players.ritual_id'
        ' where rituals.game_id = ?'
        ' group by ritual_id'
        ' order by rituals.id asc',
        url_game_id
        )
    rituals = [dict(id=row[0], game_id=row[1], leader_name=row[2], name=row[3], count=row[4]) for row in cur.fetchall()]

    return render_template(
        'join_ritual.html',
        title='Join or Create Ritual',
        year=datetime.now().year,
        name="Test player",
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

@app.route('/ritual')
def ritual():
	"""Renders the ritual page."""

	cur = g.db.execute('select id, count from rituals')
	count = cur.fetchone()[1]

	return render_template(
		'ritual.html',
		count=count
	)

@app.route('/ritual/add', methods=['POST'])
def ritual_add():

    cur = g.db.execute('select count from rituals')
    count = cur.fetchone()[0]

    g.db.execute('update rituals set count = ? where id = 0', [count + 1])
    g.db.commit()

    flash('Success!')
    return redirect(url_for('ritual'))