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
from PyQt5.QtCore import Qt, pyqtSignal
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
        self.setFixedSize(420, 480)  # Aumentei a altura para acomodar o logo
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Barra superior
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        
        # Botão de configurações
        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(QIcon("icons/settings.png"))
        self.settings_btn.setToolTip("Configurações")
        self.settings_btn.setPopupMode(QToolButton.InstantPopup)
        
        # Menu de configurações
        settings_menu = QMenu()
        theme_action = settings_menu.addAction("🌙 Tema escuro")
        theme_action.setCheckable(True)
        theme_action.setChecked(True)
        theme_action.triggered.connect(self.toggle_theme)
        self.settings_btn.setMenu(settings_menu)
        
        top_bar.addStretch()
        top_bar.addWidget(self.settings_btn)
        layout.addLayout(top_bar)
        
        # Logo da empresa
        logo_label = QLabel()
        logo_pixmap = QPixmap("ui/CTREINA_LOGO.png")
        logo_pixmap = logo_pixmap.scaled(240, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Título
        title_label = QLabel("Sistema de Inspeções NR-13")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setMinimumHeight(40)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Faça login para continuar")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setMinimumHeight(30)
        layout.addWidget(subtitle_label)
        
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
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        # Botão de login
        self.login_button = QPushButton("Entrar")
        self.login_button.setMinimumHeight(36)
        self.login_button.clicked.connect(self.realizar_login)
        
        # Botão de cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.close)
        
        # Botão de debug (emoji de engrenagem)
        self.debug_btn = QPushButton("⚙️")
        self.debug_btn.setToolTip("Debug Usuários")
        self.debug_btn.setMinimumHeight(36)
        self.debug_btn.clicked.connect(self.abrir_debug)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.debug_btn)
        layout.addLayout(buttons_layout)
        
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

    def abrir_debug(self):
        self.debug_window = DebugWindow()
        self.debug_window.show()

    def apply_theme(self):
        if self.is_dark:
            self.setStyleSheet(Styles.get_dark_theme())
            self.settings_btn.menu().actions()[0].setText("🌙 Tema escuro")
        else:
            self.setStyleSheet(Styles.get_light_theme())
            self.settings_btn.menu().actions()[0].setText("☀️ Tema claro")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme() 