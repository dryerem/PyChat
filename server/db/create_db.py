warning = """\
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+                                                                                                                        +
+    WARNING! This script create a new database. Please, run it only if sure you want to that created a new database.    +\n\
+    WARNING! Run that script can lead to, that be delete a current database.                                            +\n\
+                                                                                                                        +
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
import sqlite3


def create_connection(db_filename: str) -> sqlite3.Connection:
    """Create a connection to a database specified by db_filename
    :param db_filename: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_filename)
    except Error as e:
        print("[create_connection] - ", e)

    return conn

def create_users_table(conn: sqlite3.Connection) -> None:
    """Create a users table
    :param conn: Connection object
    :param statement: a CREATE TABLE statement  
    :return:
    """
    statement = """CREATE TABLE IF NOT EXISTS users (
        id integer PRIMARY KEY AUTOINCREMENT,
        username text NOT NULL,
        password text NOT NULL,
        email text NOT NULL
    );"""
    try:
        cur = conn.cursor()
        cur.execute(statement)
    except Error as e:
        print("[create table] - ", e)
    finally:
        print("[create table] - Successfully created a table")

def create_connections_table(conn: sqlite3.Connection) -> None:
    """Create a users table
    :param conn: Connection object
    :param statement: a CREATE TABLE statement  
    :return:
    """
    statement = """CREATE TABLE IF NOT EXISTS connections (
        id integer PRIMARY KEY AUTOINCREMENT,
        username text NOT NULL,
        socket text NOT NULL
    );"""
    try:
        cur = conn.cursor()
        cur.execute(statement)
    except Error as e:
        print("[create table] - ", e)
    finally:
        print("[create table] - Successfully created a table")

def add_user(conn: sqlite3.Connection, user: tuple):
    """Create a new user into the users table
    :param conn: Connection object
    :param user:
    :return: user id
    """
    sql = """INSERT INTO users(username, password, email)
            VALUES(?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    print(cur.lastrowid)

def main():
    print(warning)
    print("Please, input 'y(yes) or n(no)'")

    database_file = "db/chat.db"
    
    choice = str(input("You sure? Continue?: "))
    if choice == "yes" or choice == "y":
        # create a database connection
        conn = create_connection(database_file)
        with conn:
            # create a table
            if conn is not None:
                create_users_table(conn)
                create_connections_table(conn)
            else:
                print("Error! Cannot create the database connection.")
                
            # create a admin users
            users = []
            users.append(("dryerem19", "Surv16893", "-"))
            users.append(("admin", "admin", "-"))
            users.append(("test", "test", "-"))
            for user in users:
                user_id = add_user(conn, user)

    if choice == "no" or choice == "n":
        print("Right choice!")

if __name__ == "__main__":
    main()