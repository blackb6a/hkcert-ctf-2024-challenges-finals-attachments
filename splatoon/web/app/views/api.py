import math
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

from app.cache import cache
from app.db import db
from app.limiter import limiter
from app.util import master
from app.util.decorators import login_required
from app.util.paintball import simulate

# =========

route = Blueprint('api', __name__)


@route.route('/login/', methods=[HTTPMethod.POST])
def login():
    request_data = request.get_json()

    token = request_data.get('token')

    user_id = master.authenticate(token)
    if user_id is None:
        return {'error': 'invalid credentials'}, HTTPStatus.FORBIDDEN

    session['user_id'] = user_id

    return {}, HTTPStatus.OK


"""Retrieve the current game map (in PNG)"""
@route.route('/map/', methods=[HTTPMethod.GET])
def get_map():
    return send_file('/tmp/map-latest.png', mimetype='image/png')

"""Retrieve the current scoreboard"""
@route.route('/scoreboard/', methods=[HTTPMethod.GET])
@cache.cached(timeout=3)
def get_scoreboard():
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            users.id AS user_id, users.name AS user_name, users.color AS user_color, COUNT(board.user_id) AS score
        FROM users
        LEFT JOIN
            board ON users.id = board.user_id
        GROUP BY users.id
    ''')
    results = cursor.fetchall()
    
    results = [
        {
            'id': result['user_id'],
            'name': result['user_name'],
            'color': result['user_color'],
            'score': result['score']
        }
        for result in results
    ]
    results = sorted(results, key=lambda r: r['score'], reverse=True)
    return results

"""Retrieve the current player"""
@route.route('/me/', methods=[HTTPMethod.GET])
@login_required
@limiter.limit('5/second', key_func=lambda: f"get_me/{session.get('user_id')}")
def get_me(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user_id, ))
    user = cursor.fetchone()
    if user is None:
        return {'error': 'unexpected error, please contact challenge admins'}, HTTPStatus.INTERNAL_SERVER_ERROR

    mana = min(100, time.time() - user['mana_reference'])

    return {
        'user': {
            'id': user['id'],
            'name': user['name'],
            'color': user['color'],
            'mana_reference': user['mana_reference'],
            'mana': mana,
        }
    }, HTTPStatus.OK


"""List the active paintballs of the current player"""
@route.route('/paintballs/', methods=[HTTPMethod.GET])
@login_required
@limiter.limit('5/second', key_func=lambda: f"list_paintballs/{session.get('user_id')}")
def list_paintballs(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM paintballs WHERE user_id = ? AND is_used = 0 AND available_at <= ?', (current_user_id, time.time()))
    paintballs = cursor.fetchall()

    marshaled_paintballs = []
    for paintball in paintballs:
        _, _, _, mana, _ = simulate(paintball, 0, 0, '')

        marshaled_paintballs.append({
            'id': paintball['id'],
            'user_id': paintball['user_id'],
            'token': paintball['token'],
            'radius': paintball['radius'],
            'mana': math.ceil(mana),
            'is_used': paintball['is_used']
        })
        
    return {'paintballs': marshaled_paintballs}, HTTPStatus.OK

"""Retrieve the latest 50 messages"""
@route.route('/messages/', methods=[HTTPMethod.GET])
@login_required
@limiter.limit('2/second', key_func=lambda: f"list_messages/{session.get('user_id')}")
@cache.cached(timeout=1)
def list_messages(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages ORDER BY created_at DESC LIMIT 50')
    messages = cursor.fetchall()

    return {'messages': [
        message['content']
        for message in messages
    ]}, HTTPStatus.OK


"""Throw a paintball onto the game board"""
@route.route('/paintballs/', methods=[HTTPMethod.POST])
@login_required
@limiter.limit('5/second', key_func=lambda: f"throw_paintball/{session.get('user_id')}")
def throw_paintball(current_user_id):
    request_data = request.get_json()

    token = request_data.get('token')
    x = request_data.get('x')
    y = request_data.get('y')
    nonce = request_data.get('nonce', '')
    current_time = time.time()

    if type(x) != int: return {'error': 'invalid type for x'}, HTTPStatus.FORBIDDEN
    if type(y) != int: return {'error': 'invalid type for y'}, HTTPStatus.FORBIDDEN
    if type(token) != str: return {'error': 'invalid type for token'}, HTTPStatus.FORBIDDEN
    if type(nonce) != str: return {'error': 'invalid type for nonce'}, HTTPStatus.FORBIDDEN
    if x < 0 or x >= 768: return {'error': 'invalid x-coordinate'}, HTTPStatus.FORBIDDEN
    if y < 0 or y >= 768: return {'error': 'invalid y-coordinate'}, HTTPStatus.FORBIDDEN

    conn = db.get_connection()
    cursor = conn.cursor()

    # Checks if the cooldown is finished
    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user_id, ))
    user = cursor.fetchone()
    if user is None:
        return {'error': 'user not found'}, HTTPStatus.FORBIDDEN

    user_name = user['name']
    user_color = user['color']

    # Retrieves the paintball by token
    cursor.execute('SELECT * FROM paintballs WHERE token = "%s" AND is_used = 0' % (token, ))
    paintball = cursor.fetchone()
    if paintball is None: return {'error': 'paintball not found'}, HTTPStatus.FORBIDDEN
    
    x0, y0, radius, mana, power = simulate(paintball, x, y, nonce)
    current_mana_reference = max(current_time-100, user['mana_reference']) + mana
    if current_mana_reference >= current_time:
        return {'error': 'insufficient mana'}, HTTPStatus.FORBIDDEN

    # Uses the paintball
    cursor.execute('UPDATE paintballs SET is_used = 1 WHERE token = ? AND is_used = 0', (token, ))

    if cursor.rowcount == 0:
        return {'error': 'paintball not found'}, HTTPStatus.FORBIDDEN

    current_app.logger.info(f'{user_name} threw a paintball (token {token}) with {mana} MP')

    cursor.execute('UPDATE users SET mana_reference = ? WHERE id = ?', (current_mana_reference, current_user_id))
    
    cursor.execute('''
        UPDATE board SET user_id = ?
        WHERE
            (x-?)*(x-?) + (y-?)*(y-?) <= ?*? AND
            abs(random() % 4294967296) / 4294967296.0 < ? - round((x-?)*(x-?) + (y-?)*(y-?)) / (?*?)
    ''', (current_user_id, x0, x0, y0, y0, radius, radius, power, x0, x0, y0, y0, radius, radius))
    pixels_painted = cursor.rowcount

    cursor.execute('INSERT INTO messages (content, created_at) VALUES (?, ?)', (
        f'<span style="color: {user_color}">{user_name}</span> threw a paintball with radius {radius}, painted {pixels_painted} pixels', current_time
    ))

    # Draws the current game map
    cursor.execute('''
        SELECT
            board.x AS x, board.y AS y, users.color AS user_color
        FROM board
        JOIN
            users ON board.user_id = users.id
    ''')
    results = cursor.fetchall()

    im = Image.new('RGB', (768, 768))

    px = im.load()
    for result in results:
        x, y, color = result['x'], result['y'], result['user_color']
        px[x, y] = ast.literal_eval(color[3:])

    im.save(f'/tmp/map-{current_time}.png')
    im.save('/tmp/map-latest.png')

    conn.commit()

    current_mana = current_time - current_mana_reference
    return {'mana': current_mana}, HTTPStatus.OK
