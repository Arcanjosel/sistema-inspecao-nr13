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
from database.migrations import executar_migracoes
from PyQt5.QtCore import pyqtSignal

# Configuração do logging
logging.basicConfig(
    filename='logs/sistema.log',
    level=logging.DEBUG,  # Aumentei o nível para DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona um handler para mostrar logs no console também
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

class SistemaInspecao:
    def __init__(self):
        logger.debug("Iniciando construtor do SistemaInspecao")
        try:
            logger.debug("Criando QApplication")
            self.app = QApplication(sys.argv)
            logger.debug("QApplication criado com sucesso")
            
            logger.debug("Criando AuthController")
            self.auth_controller = AuthController()
            logger.debug("AuthController criado com sucesso")
            
            self.window = None
            self.login_window = None
            self.is_dark = True
            logger.info("Sistema inicializado com sucesso")
        except Exception as e:
            logger.error(f"ERRO no construtor de SistemaInspecao: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
    def show_login(self):
        """Exibe a tela de login"""
        try:
            logger.debug("Criando janela de login")
            self.login_window = LoginWindow(self.auth_controller)
            logger.debug("Conectando sinal de login_success")
            self.login_window.login_success.connect(self.on_login_success)
            logger.debug("Exibindo janela de login")
            self.login_window.show()
            logger.info("Janela de login exibida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao mostrar janela de login: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
            
            # Conectar sinal de logout
            self.window.logout_requested.connect(self.handle_logout)
                
            self.window.is_dark = self.is_dark
            self.window.apply_theme()
            self.window.show()
            logger.info(f"Janela principal exibida para usuário: {usuario['tipo_acesso']}")
        except Exception as e:
            logger.error(f"Erro ao processar login: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        
    def handle_logout(self):
        """Fecha a janela atual e mostra a tela de login."""
        logger.info("Logout solicitado.")
        if self.window:
            self.window.close()
            self.window = None
            logger.info("Janela principal fechada.")
        self.show_login()
        logger.info("Retornando para a tela de login.")
        
    def run(self):
        """Inicia a aplicação"""
        try:
            logger.info("Iniciando aplicação")
            
            # Importações para depuração
            logger.debug("Verificando imports")
            import ui.login_window
            logger.debug("Import login_window OK")
            import ui.admin_ui
            logger.debug("Import admin_ui OK")
            import ui.client_ui
            logger.debug("Import client_ui OK")
            import ui.modals
            logger.debug("Import modals OK")
            
            # Verificar se estamos no ambiente correto
            import os
            logger.debug(f"Diretório atual: {os.getcwd()}")
            
            # Exibe a tela de login
            logger.debug("Chamando show_login()")
            self.show_login()
            logger.debug("show_login() executado com sucesso")
            
            logger.info("Executando o loop de eventos da aplicação")
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            print(f"ERRO FATAL: {str(e)}")
            print(traceback.format_exc())
            return 1

if __name__ == "__main__":
    try:
        # Tenta criar o diretório de logs se não existir
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        logger.info("=== INICIANDO APLICAÇÃO ===")
        
        # Inicializa o banco de dados
        logger.info("Inicializando banco de dados")
        db_models = DatabaseModels()
        db_models.criar_tabelas()
        
        # Executa as migrações pendentes
        logger.info("Executando migrações do banco de dados")
        executar_migracoes()
        
        # Cria o usuário admin se não existir
        logger.info("Verificando usuário admin")
        auth = AuthController()
        sucesso, mensagem = auth.criar_usuario(
            nome="Administrador",
            email="admin@empresa.com",
            senha="admin123",  # Altere para uma senha forte!
            tipo_acesso="admin"
        )
        logger.info(f"Resultado da criação do admin: {mensagem}")
        
        # Inicia a aplicação
        logger.info("Criando instância do sistema")
        sistema = SistemaInspecao()
        logger.info("Executando a aplicação")
        codigo_saida = sistema.run()
        
        logger.info(f"Aplicação encerrada com código {codigo_saida}")
        sys.exit(codigo_saida)
        
    except Exception as e:
        import traceback
        logger.error(f"Erro fatal: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERRO FATAL: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1) 