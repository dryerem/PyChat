import threading
import socket
import time
import json
import sqlite3
import os

import manage as man

from datetime import datetime

from models.requests import RequestInfo
from models.requests import Request
from models.requests import AuthRequest
from models.requests import MessageRequest

from models.response import AuthResponse

clients = []

# TODO: REFACT ALL

class Server:
    def __init__(self, address:tuple=None, host:str=None, port:int=None, db_conn=None, debug:bool=False):
        """Create server.
        :param address: The server address (host, port). Leave None if host and port not None
        :param host: The server host (port). Leave None if address not None
        :param port: The server port (port). Leave None if address not None    
        :param debug: enabled printing errors, if debug is True
        """
        print(f"[DEBUG] - Debuggind enabled: {debug}")
        if address is not None: self.address = address
        elif host is not None and port is not None: self.address = (host, port)
        self.debug = debug
        self.db_conn = db_conn
        self.db_curs = db_conn.cursor()
        self.server = self.create_server()

        self.threads = []
        self.connections = []

    def create_server(self) -> socket.socket:
        """
        Create the server.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.address)
        sock.listen()
        if self.debug:
            print(f"[DEBUG] - Server has been started on {self.address}")
        return sock

    def listen_server(self) -> None:
        while True:
            conn, addr = self.server.accept()
            if self.debug: print(f'[DEBUG] - New connection from: {addr}')
            self.connections.append(conn)
            th = threading.Thread(target=self.recv, args=(conn, addr, ), daemon=True)
            th.start()
            self.threads.append(th)

    def recv(self, conn, addr):
        # TODO: Вынести всю обработку запросов в отдельный модуль
        if self.debug:
            print(f'[DEBUG] - Listening a new messages from {addr}.')
        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                self.client_disconnect(conn)
                break
            else:
                if not data:
                    if self.debug: print(f'[DEBUG] - Client {addr} disconnected.')
                    self.client_disconnect(conn)
                    break
                else:
                    raw = json.loads(data.decode('utf-8'))
                    print(raw)
                    request = Request(**raw)
                    if request.request[0].type_request == "AuthRequest":
                        data = AuthRequest(**request.data[0])
                        if self.trying_authorization(data) is True:
                            self.add_new_connection(conn, data.login) # add a new connection

                            r_type = RequestInfo(type_request="AuthResponse", request_ts=f"{datetime.now()}")
                            r_data = AuthResponse(access=True)
                            request = Request(request=[r_type], data=[r_data])
                            self.send_request(conn, request.json())

                    elif request.request[0].type_request == "MessageRequest":
                        data = MessageRequest(**request.data[0])
                        if data.to == "all":
                            # self.db_curs.execute(f'SELECT socket from connections where socket != "{str(conn)}"')
                            # all_clients = self.db_curs.fetchall()
                            for client in clients:
                                if client != conn:
                                    r_type = RequestInfo(type_request="MessageRequest", request_ts=f"{datetime.now()}")
                                    r_data = MessageRequest(from_=data.from_, to="all", message=data.message)
                                    request = Request(request=[r_type], data=[r_data])
                                    self.send_request(client, request.json())                               

    def send_request(self, conn, request):
        conn.send(request.encode("utf-8"))

    def client_disconnect(self, conn):
        clients.remove(conn)
        conn.close()

    def trying_authorization(self, auth_data) -> bool:
        """This function check data authorization.
        :param auth_data: auth data
        :return: True if authorization success, False otherwise
        """
        try:
            self.db_curs.execute('SELECT username FROM users WHERE username = "{}"'.format(auth_data.login))
            result_username = self.db_curs.fetchall()[0][0]
            self.db_curs.execute('SELECT password FROM users WHERE password = "{}"'.format(auth_data.password))
            result_password = self.db_curs.fetchall()[0][0]
        except IndexError:
            return False
        else:
            return True

    def add_new_connection(self, client_socket: socket.socket, username: str) -> None:
        """This function add a client socket to 'clients' list.
        :param client_socket: client socket object
        :param username: client username
        """
        clients.append(client_socket)

    def started(self) -> tuple:
        """Return the server address.
        """
        return self.address


if __name__ == "__main__":
    db_filename = "db/chat.db"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_file_path = os.path.join(current_dir, db_filename)

    db_conn = None
    if os.path.isfile(database_file_path) is True:
        db_conn = man.create_connection(database_file_path)
        if db_conn:
            print(f'[*] - Successfully connected to database: [{db_filename}] at {datetime.now()}')
        else:
            print("[*] - Failure to connect to database. Server shutdown.")
            sys.exit(1)

    server = Server(address=("127.0.0.1", 8888), db_conn=db_conn, debug=True)
    server.listen_server()
