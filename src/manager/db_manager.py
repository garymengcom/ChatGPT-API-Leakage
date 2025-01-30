import logging
import os
import sqlite3
from datetime import date
from sqlite3 import Connection, Cursor


class DatabaseManager:
    """
    This class is used to manage the database.
    """
    def __init__(self, db_filename: str):
        self.db_filename = db_filename
        self.con: Connection | None = None
        self.cur: Cursor | None = None

    def __enter__(self):
        if not os.path.exists(self.db_filename):
            logging.info("Creating database github.db")

        self.con = sqlite3.connect(self.db_filename)
        self.cur = self.con.cursor()

        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='APIKeys'")
        if self.cur.fetchone() is None:
            logging.info("Creating table APIKeys")
            self.cur.execute("CREATE TABLE APIKeys(apiKey, status, lastChecked)")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.con:
            self.con.close()


    def all_keys(self) -> list:
        if self.cur is None:
            raise ValueError("Cursor is not initialized")
        self.cur.execute("SELECT apiKey FROM APIKeys WHERE status='yes'")
        return self.cur.fetchall()

    def deduplicate(self) -> None:
        if self.con is None:
            raise ValueError("Connection is not initialized")
        if self.cur is None:
            raise ValueError("Cursor is not initialized")
        self.cur.execute("CREATE TABLE temp_table as SELECT apiKey, status, MAX(lastChecked) as lastChecked FROM APIKeys GROUP BY apiKey;")
        self.cur.execute("DROP TABLE APIKeys;")
        self.cur.execute("ALTER TABLE temp_table RENAME TO APIKeys;")
        self.con.commit()

    def delete(self, api_key: str) -> None:
        if self.con is None:
            raise ValueError("Connection is not initialized")
        if self.cur is None:
            raise ValueError("Cursor is not initialized")
        self.cur.execute("DELETE FROM APIKeys WHERE apiKey=?", (api_key,))
        self.con.commit()

    def insert(self, api_key: str, status: str):
        if self.con is None:
            raise ValueError("Connection is not initialized")
        if self.cur is None:
            raise ValueError("Cursor is not initialized")
        today = date.today()
        self.cur.execute("INSERT INTO APIKeys(apiKey, status, lastChecked) VALUES(?, ?, ?)", (api_key, status, today))
        self.con.commit()

    def key_exists(self, api_key: str) -> bool:
        if self.cur is None:
            raise ValueError("Cursor is not initialized")
        self.cur.execute("SELECT apiKey FROM APIKeys WHERE apiKey=?", (api_key,))
        return self.cur.fetchone() is not None

    def __del__(self):
        if self.con:
            self.con.close()
