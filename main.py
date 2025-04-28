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
from database.models import DatabaseModels

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
        self.login_window = None
        self.is_dark = True
        logger.info("Sistema inicializado")
        
    def show_login(self):
        """Exibe a tela de login"""
        try:
            self.login_window = LoginWindow(self.auth_controller)
            self.login_window.login_success.connect(self.on_login_success)
            self.login_window.show()
            logger.info("Janela de login exibida")
        except Exception as e:
            logger.error(f"Erro ao mostrar janela de login: {str(e)}")
            raise
        
    def on_login_success(self, usuario_id):
        """Trata o sucesso do login"""
        try:
            logger.info(f"Login bem sucedido para usuário ID: {usuario_id}")
            usuario = self.auth_controller.get_usuario_atual()
            
            if self.login_window:
                self.is_dark = self.login_window.is_dark
                self.login_window.close()
                self.login_window = None
            
            if usuario['tipo_acesso'] == 'admin':
                self.window = AdminWindow(self.auth_controller)
            else:
                # Busca a empresa do usuário
                db_models = DatabaseModels()
                conn = db_models.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT empresa FROM usuarios WHERE id = ?", (usuario_id,))
                row = cursor.fetchone()
                company = row[0] if row else ""
                cursor.close()
                
                self.window = ClientWindow(self.auth_controller, usuario_id, company)
                
            self.window.is_dark = self.is_dark
            self.window.apply_theme()
            self.window.show()
            logger.info(f"Janela principal exibida para usuário: {usuario['tipo_acesso']}")
        except Exception as e:
            logger.error(f"Erro ao processar login: {str(e)}")
            raise
        
    def run(self):
        """Inicia a aplicação"""
        try:
            logger.info("Iniciando aplicação")
            self.show_login()
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
            return 1

if __name__ == "__main__":
    try:
        sistema = SistemaInspecao()
        sys.exit(sistema.run())
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1)

auth = AuthController()
sucesso, mensagem = auth.criar_usuario(
    nome="Administrador",
    email="admin@empresa.com",
    senha="admin123",  # Altere para uma senha forte!
    tipo_acesso="admin"
)
print(mensagem) 