#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para atualizar a tabela de equipamentos, adicionando campos de manutenção.
"""

import logging
import sys
from database.models import DatabaseModels
from controllers.equipment_controller import EquipmentController

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("update_equipment_table")

def main():
    """Função principal para atualizar a tabela de equipamentos."""
    try:
        logger.info("Iniciando atualização da tabela de equipamentos")
        
        # Inicializar controlador
        db_models = DatabaseModels()
        equipment_controller = EquipmentController(db_models)
        
        # Atualizar estrutura da tabela
        success, message = equipment_controller.atualizar_tabela_equipamentos()
        
        if success:
            logger.info(f"Atualização concluída com sucesso: {message}")
            return True
        else:
            logger.error(f"Falha na atualização: {message}")
            return False
            
    except Exception as e:
        logger.error(f"Erro durante a atualização: {str(e)}")
        return False
        
if __name__ == "__main__":
    if main():
        logger.info("Script executado com sucesso!")
        sys.exit(0)
    else:
        logger.error("Falha na execução do script!")
        sys.exit(1) 