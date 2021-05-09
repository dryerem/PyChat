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


from managers.db_manager import DatabaseManager

from managers.request_manager import AuthStatus
from managers.request_manager import TypesRequests
from managers.request_manager import RequestManager


class Server:
    def __init__(self, address:tuple=None, host:str=None, port:int=None, db_conn=None, debug:bool=False):
        """Create server.
        :param address: The server address (host, port). Leave None if host and port not None
        :param host: The server host (port). Leave None if address not None
        :param port: The server port (port). Leave None if address not None    
        :param debug: enabled printing errors, if debug is True
        """
        if address is not None: self.address = address
        elif host is not None and port is not None: self.address = (host, port)
        
        self.debug = debug
        self.server = self.create_server()
        self.db_conn = db_conn
        self.db_curs = db_conn.cursor()
        self.threads = []


        self.connections = []
        self.clients = []

    def create_server(self) -> socket.socket:
        """
        Create the socket object.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.address)
        sock.listen()
        return sock

    def run_server(self) -> None:
        if self.debug:
            print(f"[SERVER DEBUG] - Server has been running on: {self.address}")
        while True:
            client_socket, client_address = self.server.accept()
            if self.debug: print(f'[SERVER DEBUG] - New connection from: {client_address}')
            self.connections.append(client_socket)

            th = threading.Thread(target=self.recv, args=(client_socket, client_address), daemon=True)
            th.start()
            self.threads.append(th)

    def recv(self, client_connect, client_address):
        while True:
            try:
                data = client_connect.recv(1024)
            except ConnectionResetError:
                self.client_disconnect(client_connect, client_address)
                break
            else:
                if not data:
                    self.client_disconnect(client_connect, client_address)
                    break
                else:
                    self.response(client_connect, data)

                    '''
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
                            for client in clients:
                                if client != conn:
                                    r_type = RequestInfo(type_request="MessageRequest", request_ts=f"{datetime.now()}")
                                    r_data = MessageRequest(from_=data.from_, to="all", message=data.message)
                                    request = Request(request=[r_type], data=[r_data])
                                    self.send_request(client, request.json())           
                    '''    

    def response(self, client_connection, request):
        """This method create a responce and return it.
        """
        manager = RequestManager(request)

        if manager.type_request() == TypesRequests.AUTH:
            if self.trying_authorization(manager.data_request()) is True:
                self.clients.append(client_connection)
                self.send_response(client_connection, manager.create_response(manager.auth_response(AuthStatus.SUCCESS)))

        elif manager.type_request() == TypesRequests.MESSAGE:
            if manager.data_request().to == "all":
                for client in self.clients:
                    if client != client_connection:
                        self.send_response(client, request.decode("utf-8"))     

    def send_response(self, client_conn, request):
        client_conn.send(request.encode("utf-8"))

    def client_disconnect(self, client_conn: socket.socket, client_address: tuple):
        if self.debug is True:
            print(f'[SERVER DEBUG] - Client {client_address} disconnected.')

        if client_conn in self.clients:
            self.clients.remove(client_conn)
        self.connections.remove(client_conn)
        client_conn.close()

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
    server.run_server()
