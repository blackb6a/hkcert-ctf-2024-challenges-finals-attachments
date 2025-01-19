from PIL import Image
from http import HTTPStatus, HTTPMethod
from flask import Blueprint, request, current_app, send_file, session, render_template
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

route = Blueprint('pages', __name__)


@route.route('/', methods=[HTTPMethod.GET])
def homepage():
    return render_template('homepage.html'), HTTPStatus.OK

@route.route('/login/', methods=[HTTPMethod.GET])
def login():
    return render_template('login.html'), HTTPStatus.OK

@route.route('/scoreboard/', methods=[HTTPMethod.GET])
def scoreboard():
    return render_template('scoreboard.html'), HTTPStatus.OK
