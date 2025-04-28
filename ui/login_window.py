#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Login do Sistema de Gerenciamento de Inspeções Técnicas
"""
from ui.debug_window import DebugWindow
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox,
                            QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

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
        self.setFixedSize(420, 420)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)
        
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
        
        # Switch de tema
        self.theme_switch = QPushButton("🌙 Tema escuro")
        self.theme_switch.setCheckable(True)
        self.theme_switch.setChecked(True)
        self.theme_switch.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_switch)
        
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
        
        # Configurações adicionais
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #212529;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #80bdff;
                outline: none;
            }
        """)
        
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
            self.setStyleSheet("""
                QMainWindow { background-color: #181a1b; }
                QLabel { color: #f1f1f1; }
                QLineEdit {
                    background-color: #232629;
                    color: #f1f1f1;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLineEdit:focus { border: 1.5px solid #007bff; }
                QPushButton {
                    background-color: #232629;
                    color: #f1f1f1;
                    border: 1px solid #444;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #33373a; }
            """)
            self.theme_switch.setText("🌙 Tema escuro")
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #f8f9fa; }
                QLabel { color: #212529; }
                QLineEdit {
                    background-color: #fff;
                    color: #212529;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLineEdit:focus { border: 1.5px solid #007bff; }
                QPushButton {
                    background-color: #e9ecef;
                    color: #212529;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #dee2e6; }
            """)
            self.theme_switch.setText("☀️ Tema claro")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme() 