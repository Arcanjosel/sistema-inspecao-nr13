#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a aba de inspeções isoladamente
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from database.models import DatabaseModels
from ui.inspection_ui import InspectionTab

# Configuração do logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/teste_inspecao.log',
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

class TesteWindow(QMainWindow):
    """Janela para testar a aba de inspeções"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste da Aba de Inspeções")
        self.setGeometry(100, 100, 1024, 768)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Inicializa o banco de dados
        self.db_models = DatabaseModels()
        
        # Cria a aba de inspeções
        self.inspection_tab = InspectionTab(self.db_models, False)
        
        # Adiciona ao layout
        main_layout.addWidget(self.inspection_tab)

if __name__ == "__main__":
    try:
        logger.info("=== INICIANDO TESTE DA ABA DE INSPEÇÕES ===")
        
        # Inicializa a aplicação
        app = QApplication(sys.argv)
        
        # Cria e exibe a janela
        janela = TesteWindow()
        janela.show()
        
        # Executa o loop de eventos
        sys.exit(app.exec_())
        
    except Exception as e:
        import traceback
        logger.error(f"Erro fatal: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERRO FATAL: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1) 