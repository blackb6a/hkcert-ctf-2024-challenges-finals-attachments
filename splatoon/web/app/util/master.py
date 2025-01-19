import re
import requests
from flask import current_app

# This is the APIs that the challenge server interacts with the CTF server.
# You don't need to look into this.

"""Authenticate an user given the token."""
def authenticate(user_token):
    if not re.fullmatch(r'[a-zA-Z0-9]{32}', user_token): return None

    base_uri = current_app.config.get('MASTER_SERVER_BASE_URI')
    auth_token = current_app.config.get('MASTER_SERVER_AUTHENTICATION_TOKEN')

    r = requests.get(f'{base_uri}/{user_token}/', headers={
        'Authorization': f'Bearer {auth_token}'
    }, verify=False)
    if r.status_code != 200: return None

    j = r.json()
    user = j.get('team')
    if user is None: return None

    user_id = user.get('id')
    if user_id is None: return None

    return user_id

"""Retrieve a list of users from the CTF server. The entries are in 3-tuples (id, name, color)."""
def list_players():
    base_uri = current_app.config.get('MASTER_SERVER_BASE_URI')
    auth_token = current_app.config.get('MASTER_SERVER_AUTHENTICATION_TOKEN')

    r = requests.get(f'{base_uri}/', headers={
        'Authorization': f'Bearer {auth_token}'
    }, verify=False)
    if r.status_code != 200: raise Exception(f'unexpected response code {r.status_code}')

    j = r.json()
    users = [
        (user['id'], user['name'], user['color'])
        for user in j.get('teams')
    ]

    return users
