import sqlite3
from flask import Flask, g, current_app

class SQLite:
    def init_app(self, app):
        self.app = app

        # Create tables if not exists
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id             INTEGER PRIMARY KEY,
            name           VARCHAR(256) NOT NULL,
            color          VARCHAR(256) NOT NULL,
            mana_reference INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS paintballs (
            id           INTEGER PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            token        VARCHAR(16) NOT NULL,
            radius       INTEGER NOT NULL,
            base_mana    INTEGER NOT NULL,
            available_at INTEGER NOT NULL,
            is_used      INTEGER NOT NULL CHECK (is_used IN (0, 1)) DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS board (
            x             INTEGER NOT NULL,
            y             INTEGER NOT NULL,
            user_id       INTEGER
        );

        CREATE TABLE IF NOT EXISTS messages (
            content    VARCHAR(1024) NOT NULL,
            created_at INTEGER NOT NULL
        );
        ''')

        app.teardown_appcontext(self.close_connection)

    def get_connection(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_connection(self, exception=None):
        db = g.pop('db', None)
        if not db: return
        db.rollback()
        db.close()

# ==

db = SQLite()

def init_app(app):
    db.init_app(app)
