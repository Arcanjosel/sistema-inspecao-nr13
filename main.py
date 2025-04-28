#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Gerenciamento de Inspeções Técnicas - NR-13
Autor: [Seu Nome]
Data: [Data]
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.admin_ui import AdminWindow
from ui.client_ui import ClientWindow
from ui.login_window import LoginWindow
from controllers.auth_controller import AuthController
import pyodbc
from ui.debug_window import DebugWindow

# Configuração do logging
logging.basicConfig(
    filename='logs/sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SistemaInspecao:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.auth_controller = AuthController()
        self.window = None
        
    def show_login(self):
        """Exibe a tela de login"""
        self.login_window = LoginWindow(self.auth_controller)
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
        
    def on_login_success(self, usuario_id):
        """Trata o sucesso do login"""
        usuario = self.auth_controller.get_usuario_atual()
        
        if usuario['tipo_acesso'] == 'admin':
            self.window = AdminWindow(self.auth_controller)
        else:
            self.window = ClientWindow(self.auth_controller, usuario_id)
            
        self.window.show()
        
    def run(self):
        """Inicia a aplicação"""
        try:
            self.show_login()
            sys.exit(self.app.exec_())
        except Exception as e:
            logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    sistema = SistemaInspecao()
    sistema.run()

auth = AuthController()
sucesso, mensagem = auth.criar_usuario(
    nome="Administrador",
    email="admin@empresa.com",
    senha="admin123",  # Altere para uma senha forte!
    tipo_acesso="admin"
)
print(mensagem) 