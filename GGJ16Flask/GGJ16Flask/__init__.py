"""
The flask application package.
"""

import sqlite3
from flask import Flask, session, g, abort, render_template
from contextlib import closing

DATABASE = 'ritual.db'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'admin'

def connect_db():
    print "DATABASE: " + app.config['DATABASE']

    conn = sqlite3.connect(app.config['DATABASE'])

    print "Connection: " + conn

    return conn

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

import GGJ16Flask.views
