def marshal_paintball(row):
    return {
        'id': row['id'],
        'user_id': row['user_id'],
        'token': row['token'],
        'radius': row['radius'],
        'base_mana': row['base_mana'],
        'is_used': row['is_used']
    }
