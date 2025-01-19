from PIL import Image
from http import HTTPStatus, HTTPMethod
from flask import Blueprint, request, current_app, send_file, session
import random
import itertools
import time
import requests
import os
import base64
import ast

from app.db import db
from app.limiter import limiter
from app.util import master
from app.util.decorators import login_required
from app.util.crypto import public_hash, secret_hash
from app.util.marshalers import marshal_paintball

route = Blueprint('ticks', __name__)

# Admin APIs. Those are not intended to be vulnerable, but I guess I can't stop
# you from finding 0-days, right? :)

@route.route('/', methods=[HTTPMethod.POST])
def handle_tick():
    auth_header = request.headers.get('Authorization')
    expected_auth_token = current_app.config.get('AUTHORIZATION_TOKEN')
    if auth_header != f'Bearer {expected_auth_token}':
        return {'error': 'incorrect auth token for admin'}, HTTPStatus.FORBIDDEN

    request_data = request.get_json()
    action = request_data.get('action')
    tick = request_data.get('tick')
    if type(tick) != int:
        return {'error': 'incorrect tick'}, HTTPStatus.BAD_REQUEST

    if action == 'start':
        return handle_start_tick(tick), HTTPStatus.OK
    elif action == 'end':
        return handle_end_tick(tick), HTTPStatus.OK

    return {'error': 'incorrect action'}, HTTPStatus.BAD_REQUEST

# ======

def handle_start_tick(tick: int):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Distributes the paintballs to the players (some paintballs are time-locked)
    users = master.list_players()
    t = time.time()

    paintball_specifications = [
        (32, 8, 0),
        (32, 8, 0),
        (32, 8, 0),
        (32, 8, 0),
        (32, 8, 0),
        (40, 12, 60),
        (40, 12, 60),
        (40, 12, 60),
        (40, 12, 60),
        (48, 16, 120),
        (48, 16, 120),
        (48, 16, 120),
        (56, 20, 180),
        (56, 20, 180),
        (64, 24, 240),
        (96, 40, 240),
    ]

    paintballs = []
    for user, (radius, cooldown, Δt) in itertools.product(users, paintball_specifications):
        user_id, *_ = user

        token = base64.b64encode(os.urandom(9)).decode()
        paintballs.append([user_id, token, radius, cooldown, t + Δt])
        current_app.logger.info(f'generated paintball for user #{user_id} (token {token}, radius {radius})')

    cursor.executemany('INSERT INTO users (id, name, color) VALUES (?, ?, ?) ON CONFLICT DO NOTHING', users)
    cursor.executemany('INSERT INTO paintballs (user_id, token, radius, base_mana, available_at) VALUES (?, ?, ?, ?, ?)', paintballs)
    cursor.executemany('INSERT INTO board (x, y) VALUES (?, ?)', [(x, y) for x, y in itertools.product(range(768), repeat=2)])
    cursor.execute('INSERT INTO messages (content, created_at) VALUES (?, ?)', (
        f'Tick {tick} begins!',
        t
    ))

    conn.commit()

    im = Image.new('RGB', (768, 768))
    im.save(f'/tmp/map-{t}.png')
    im.save('/tmp/map-latest.png')

    return {}

def handle_end_tick(tick: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT
            users.id AS user_id, COUNT(board.user_id) AS score
        FROM users
        LEFT JOIN
            board ON users.id = board.user_id
        GROUP BY users.id
    ''')
    results = cursor.fetchall()

    cursor.execute('DELETE FROM paintballs')
    cursor.execute('DELETE FROM board')
    conn.commit()
    
    return {
        'teams': [
            {'id': result['user_id'], 'score': result['score']}
            for result in results
        ]
    }
