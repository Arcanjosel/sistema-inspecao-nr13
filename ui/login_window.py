#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Login do Sistema de Gerenciamento de Inspeções Técnicas
"""
from ui.debug_window import DebugWindow
from ui.styles import Styles
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox,
                            QCheckBox, QToolButton, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(int)  # Sinal emitido quando o login é bem sucedido
    
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.is_dark = True
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowTitle("Login - Sistema de Inspeções NR-13")
        self.setFixedSize(420, 520)  # Aumentei a altura para acomodar o botão de tema na parte inferior
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Logo da empresa com fundo branco
        logo_container = QLabel()
        logo_container.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                min-height: 140px;
            }
        """)
        logo_pixmap = QPixmap("ui/CTREINA_LOGO.png")
        logo_pixmap = logo_pixmap.scaled(350, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_container.setPixmap(logo_pixmap)
        logo_container.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_container)
        
       
        # Espaçador
        layout.addStretch()
        
        # Campo de e-mail
        email_label = QLabel("E-mail:")
        email_label.setFont(QFont("Arial", 11))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu e-mail")
        self.email_input.setMinimumHeight(36)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        
        # Campo de senha
        senha_label = QLabel("Senha:")
        senha_label.setFont(QFont("Arial", 11))
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Digite sua senha")
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setMinimumHeight(36)
        layout.addWidget(senha_label)
        layout.addWidget(self.senha_input)
        
        # Botões de login/cancelar
        buttons_layout = QHBoxLayout()
        
        # Botão de login (usando estilo padrão - azul #007bff)
        self.login_button = QPushButton("Entrar")
        self.login_button.setMinimumHeight(36)
        self.login_button.clicked.connect(self.realizar_login)
        
        # Botão de cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        # Barra inferior com botão de tema
        bottom_bar = QHBoxLayout()
        bottom_bar.setAlignment(Qt.AlignRight)
        
        # Botão de tema (seguindo padrão do app principal)
        self.theme_button = QPushButton()
        self.theme_button.setToolTip("Alternar tema claro/escuro")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setIconSize(QSize(24, 24))
        
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.theme_button)
        layout.addLayout(bottom_bar)
        
        # Centraliza a janela
        self.center_window()
        
    def center_window(self):
        """Centraliza a janela na tela"""
        screen = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        screen.moveCenter(center)
        self.move(screen.topLeft())
        
    def realizar_login(self):
        """Realiza o processo de login"""
        email = self.email_input.text().strip()
        senha = self.senha_input.text().strip()
        
        if not email or not senha:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos.")
            return
            
        sucesso, mensagem, usuario_id = self.auth_controller.login(email, senha)
        
        if sucesso:
            self.login_success.emit(usuario_id)
            self.close()
        else:
            QMessageBox.critical(self, "Erro", mensagem)
            
    def keyPressEvent(self, event):
        """Trata eventos de teclado"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.realizar_login()
        else:
            super().keyPressEvent(event)

    def apply_theme(self):
        """Aplica o tema escuro ou claro à interface"""
        if self.is_dark:
            self.setStyleSheet(Styles.get_dark_theme())
            
            # Estilo para botão de login no tema escuro
            self.login_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            
            # Estilo para botão de cancelar no tema escuro
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #545b62;
                }
            """)
            
            # Estilo para botão de tema no modo escuro (cinza claro)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #aaaaaa;
                    color: #121212;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
                QPushButton:pressed {
                    background-color: #888888;
                }
            """)
            
            # Configura o ícone para o tema escuro
            svg_path = "ui/theme_icon_dark.svg"
            self.setup_theme_icon("black")
            
        else:
            self.setStyleSheet(Styles.get_light_theme())
            
            # Estilo para botão de login no tema claro
            self.login_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            
            # Estilo para botão de cancelar no tema claro
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #545b62;
                }
            """)
            
            # Estilo para botão de tema no modo claro (preto)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #000000;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
                QPushButton:pressed {
                    background-color: #222222;
                }
            """)
            
            # Configura o ícone para o tema claro
            self.setup_theme_icon("white")

    def setup_theme_icon(self, color):
        """Configura o ícone do botão de tema"""
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>"""
        
        svg_bytes = svg_content.encode('utf-8')
        pixmap = QPixmap()
        pixmap.loadFromData(svg_bytes)
        self.theme_button.setIcon(QIcon(pixmap))

    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.apply_theme() 