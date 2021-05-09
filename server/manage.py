import sqlite3


def create_connection(db_filename: str) -> sqlite3.Connection:
    """Create a connection to a database specified by db_filename
    :param db_filename: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_filename, check_same_thread=False)
    except Error as e:
        print("[create_connection] - ", e)

    return conn