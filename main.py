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
from controllers.auth_controller import AuthController

# Configuração do logging
logging.basicConfig(
    filename='logs/sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Função principal que inicia a aplicação.
    """
    try:
        app = QApplication(sys.argv)
        
        # Inicializa o controlador de autenticação
        auth_controller = AuthController()
        
        # Tela de login será implementada aqui
        # Por enquanto, vamos iniciar com a tela de admin para testes
        window = AdminWindow(auth_controller)
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 