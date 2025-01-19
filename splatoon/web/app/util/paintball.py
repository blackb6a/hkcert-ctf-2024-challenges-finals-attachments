import random
from flask import current_app
from app.util.crypto import public_hash, secret_hash

def simulate(paintball, x, y, nonce):
    token = paintball['token']
    game_secret = current_app.config.get('GAME_SECRET').encode()
    payload = f'{token}{nonce}'.encode()

    penalty  = public_hash(payload)<<128
    penalty |= secret_hash(game_secret, payload)
    penalty  = list(map(int, format(penalty, '0256b')))

    DX = 2 * sum(penalty[ 0:32])
    DY = 2 * sum(penalty[32:64])

    Δx = random.randint(-DX, DX)
    Δy = random.randint(-DY, DY)
    mana_multiplier = 1 + sum(penalty[64:192]) / 32
    power = sum(penalty[192:256]) / 64

    x0 = x + Δx
    y0 = y + Δx
    radius = paintball['radius']
    mana = paintball['base_mana'] * mana_multiplier

    return x0, y0, radius, mana, power