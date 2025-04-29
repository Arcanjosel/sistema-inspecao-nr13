from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(int, str)  # Emite usuario_id e tipo_acesso
    debug_requested = pyqtSignal()  # Sinal para abrir janela de debug
    
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowTitle("Login - Sistema de Inspeção NR-13")
        self.setMinimumSize(300, 200)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Campos de login
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Botão de login
        login_btn = QPushButton("Entrar")
        login_btn.clicked.connect(self.try_login)
        layout.addWidget(login_btn)
        
        # Botão de debug (apenas em desenvolvimento)
        debug_btn = QPushButton("Debug")
        debug_btn.clicked.connect(self.debug_requested.emit)
        layout.addWidget(debug_btn)
        
    def try_login(self):
        """Tenta realizar o login com as credenciais fornecidas"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            result = self.auth_controller.login(username, password)
            if result:
                usuario_id, tipo_acesso = result
                self.login_success.emit(usuario_id, tipo_acesso)
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos")
        except Exception as e:
            logger.error(f"Erro ao tentar login: {str(e)}")
            QMessageBox.critical(self, "Erro", "Ocorreu um erro ao tentar fazer login") 