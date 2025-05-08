#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar diretamente o gerador de laudos NR-13
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# Configuração do logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/laudos.log',
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

if __name__ == "__main__":
    try:
        logger.info("=== INICIANDO GERADOR DE LAUDOS NR-13 ===")
        
        # Inicializa a aplicação
        app = QApplication(sys.argv)
        
        # Importa os módulos necessários
        from ui.laudo_window import LaudoWindow
        
        # Cria e exibe a janela
        janela = LaudoWindow()
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