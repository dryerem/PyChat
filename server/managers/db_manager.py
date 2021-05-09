import sqlite3


class DatabaseManager:
    def __init__(self, database_file_path: str):
        self.database_file_path = database_file_path
        self.database_connection = None

    def create_connection(self) -> sqlite3.Connection:
        """Create a connection to a database specified by db_filename
        :param db_filename: database file
        :return: Connection object or None
        """
        return sqlite3.connect(db_filename, check_same_thread=False)

    def search_user(self, username):
        pass