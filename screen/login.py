from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QPushButton, QWidget


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super(LoginScreen, self).__init__(parent)
        self.layout = QVBoxLayout()
        #self.layout.addStretch()
        self.layout.setSpacing(16)
        
        self.login_field = QLineEdit()
        self.password_field = QLineEdit()
        self.auth_button = QPushButton("Login in")

        self.build_ui()

    def build_ui(self):
        """
        initialize ui
        """
        self.login_field.setPlaceholderText("Enter your username...")
        self.password_field.setPlaceholderText("Enter your password...")

        self.layout.addWidget(self.login_field)
        self.layout.addWidget(self.password_field)
        self.layout.addWidget(self.auth_button)

        self.setLayout(self.layout)