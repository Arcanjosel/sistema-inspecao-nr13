#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a interface principal do sistema
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from ui.admin_ui import AdminWindow
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.inspection_ui import InspectionTab

# Configuração do logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/teste_ui.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona um handler para mostrar logs no console também
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

class FakeAuthController(AuthController):
    """Controller de autenticação falso para testes"""
    
    def __init__(self):
        super().__init__()
        self._usuario_atual = {
            'id': 1,
            'nome': 'Administrador de Teste',
            'email': 'admin@teste.com',
            'tipo_acesso': 'admin',
            'empresa': 'Empresa de Teste'
        }
    
    def usuario_logado(self):
        return self._usuario_atual
    
    def verificar_tipo_acesso(self, tipo_requerido):
        return self._usuario_atual and self._usuario_atual.get('tipo_acesso') == tipo_requerido

if __name__ == "__main__":
    try:
        logger.info("=== INICIANDO TESTE DE INTERFACE ===")
        
        # Cria a aplicação
        app = QApplication(sys.argv)
        
        # Criar controlador de autenticação fake para bypassar login
        auth_controller = FakeAuthController()
        
        # Cria a janela admin
        admin_window = AdminWindow(auth_controller)
        
        # Garante que a aba de inspeções seja inicializada corretamente
        if not hasattr(admin_window, 'inspection_tab') or not isinstance(admin_window.inspection_tab, InspectionTab):
            # Criar e configurar a aba de inspeções manualmente
            admin_window.inspection_tab = InspectionTab(
                parent=admin_window,
                auth_controller=admin_window.auth_controller,
                equipment_controller=admin_window.equipment_controller,
                inspection_controller=admin_window.inspection_controller
            )
            
            # Encontrar o índice da aba de inspeções (geralmente é o índice 2)
            inspection_tab_index = 2
            if admin_window.tabs.count() > inspection_tab_index:
                # Remover o widget antigo e adicionar o novo
                admin_window.tabs.removeTab(inspection_tab_index)
                admin_window.tabs.insertTab(inspection_tab_index, admin_window.inspection_tab, "Inspeções")
                admin_window.tabs.setTabIcon(inspection_tab_index, admin_window.get_tab_icon("inspecoes.png"))
        
        # Mostra a janela
        admin_window.show()
        
        # Executa o loop de eventos
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicativo: {str(e)}")
        import traceback
        logger.error(traceback.format_exc()) 