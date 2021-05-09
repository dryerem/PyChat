import sys
import json

from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, QMetaObject, Qt, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QStackedWidget

from screen.login import LoginScreen
from network.client import ClientWorker, Client

from network.models.requests import RequestInfo
from network.models.requests import Request
from network.models.requests import AuthRequest
from network.models.requests import MessageRequest

from network.models.response import AuthResponse


class MainWindow(QMainWindow):
    def __init__(self, window_width=None, window_height=None):
        super(MainWindow, self).__init__()
        if window_width != None and window_height != None:
            self.window_width = window_width
            self.window_height = window_height
            self.resize(window_width, window_height)
            
        self.stack_of_widget = QStackedWidget()
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.username = ""

        # ui widgets
        self.message_visable_field = QTextEdit()
        self.message_input_field = QTextEdit()
        self.send_message = QPushButton("Send my message!")

        self.login_screen = LoginScreen()
        self.login_screen.auth_button.clicked.connect(self.login_button_click)

        # show all widgets
        self.build_ui()

    def build_ui(self):
        self.message_visable_field.setFont(QFont("Roboto", 12))
        self.message_visable_field.setReadOnly(True)

        self.message_input_field.setFont(QFont("Roboto", 11))
        self.message_input_field.setPlaceholderText("Input your message here...")
        self.message_input_field.setMinimumHeight(50)
        self.message_input_field.setMaximumHeight(50)

        self.send_message.setFont(QFont("Roboto", 11))
        self.send_message.clicked.connect(self.send_message_button_clicked)

        self.main_layout.addWidget(self.message_visable_field)
        self.main_layout.addWidget(self.message_input_field)
        self.main_layout.addWidget(self.send_message)
        
        self.central_widget.setLayout(self.main_layout)
        self.stack_of_widget.addWidget(self.login_screen)
        self.setMaximumSize(self.minimumSize())
        self.stack_of_widget.addWidget(self.central_widget)
        self.setCentralWidget(self.stack_of_widget)


    def send_message_button_clicked(self):
        """
        send a client message to the server, and append to the list message.
        """
        message = self.message_input_field.toPlainText()
        if message != '':
            # send message to the server
            r_type = RequestInfo(type_request="MessageRequest", request_ts=f"{datetime.now()}")
            r_data = MessageRequest(from_=self.username, to="all", message=message)
            request = Request(request=[r_type], data=[r_data])
            client_worker.send(request.json())
            self.message_visable_field.append('You: ' + message)
        self.message_input_field.clear()

    def login_button_click(self):
        self.username = self.login_screen.login_field.text()
        r_type = RequestInfo(type_request="AuthRequest", request_ts=f"{datetime.now()}")
        r_data = AuthRequest(login=f"{self.username}", password=f"{self.login_screen.password_field.text()}")
        request = Request(request=[r_type], data=[r_data])
        client_worker.send(request.json())

    @Slot(str)
    def recieved_message_handler(self, message):
        msg = json.loads(message)
        print(msg)
        response = Request(**msg)
        if response.request[0].type_request == "AuthResponse":
            data = AuthResponse(**response.data[0])
            if data.access is True:
                self.show_main_screen()

        elif response.request[0].type_request == "MessageRequest":
            data = MessageRequest(**response.data[0])
            if data.to == "all":
                self.message_visable_field.append(f"[{data.from_}]: {data.message}")

    def show_main_screen(self):
        self.stack_of_widget.setCurrentWidget(self.central_widget)
        self.setMinimumSize(self.window_width, self.window_height)
        self.resize(self.minimumSize())

    def closeEvent(self, event):
        client_worker.close()
        network_thread.exit()
        network_thread.wait(500)
        if network_thread.isRunning() is True:
            network_thread.terminate()

def main():
    # initialize
    app = QApplication([])

    # create connection to the server
    client = Client(address=('127.0.0.1', 8888), debug=True)
    client.client_connect()

    # create a main window
    window = MainWindow(window_width=400, window_height=600)
    window.setWindowTitle("Python chat")

    # waiting for messages
    global client_worker, network_thread  # TODO: refactor this
    network_thread = QThread()
    network_thread.setTerminationEnabled(True)
    client_worker = ClientWorker(client_socket=client.client())
    client_worker.recieved_message.connect(window.recieved_message_handler)
    client_worker.moveToThread(network_thread)
    network_thread.started.connect(client_worker.start)
    network_thread.start()
    
    window.show()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())