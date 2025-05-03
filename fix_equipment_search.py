#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para correção da barra de pesquisa e combobox de equipamentos no admin_ui.py
Este script efetua as correções necessárias para resolver o problema de nomes inconsistentes
"""

import os
import re
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Cria um backup do arquivo original"""
    import shutil
    import time
    
    backup_path = f"{file_path}.bak.{int(time.time())}"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Backup criado em: {backup_path}")
    return backup_path

def fix_ui_file(file_path):
    """Corrige o arquivo admin_ui.py para resolver o problema dos comboboxes e barras de pesquisa"""
    if not os.path.isfile(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    # Fazer backup do arquivo original
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Correção 1: Renomear campos na inicialização da UI
    if "self.equipment_search_input" in content:
        logger.info("Corrigindo campo de pesquisa de equipamentos")
        content = content.replace(
            "self.equipment_search_input = QLineEdit()",
            "self.equipment_search_box = QLineEdit()"
        )
        content = content.replace(
            "self.equipment_search_input.setPlaceholderText",
            "self.equipment_search_box.setPlaceholderText"
        )
        content = content.replace(
            "self.equipment_search_input.textChanged.connect",
            "self.equipment_search_box.textChanged.connect"
        )
        content = content.replace(
            "equipment_search_container.addWidget(self.equipment_search_input)",
            "equipment_search_container.addWidget(self.equipment_search_box)"
        )
    
    # Correção 2: Renomear combobox de empresa
    if "self.equipment_company_combo" in content:
        logger.info("Corrigindo combobox de empresas")
        content = content.replace(
            "self.equipment_company_combo = QComboBox()",
            "self.equipment_company_selector = QComboBox()"
        )
        content = content.replace(
            "self.equipment_company_combo.currentIndexChanged.connect",
            "self.equipment_company_selector.currentIndexChanged.connect"
        )
        content = content.replace(
            "equipment_search_container.addWidget(self.equipment_company_combo)",
            "equipment_search_container.addWidget(self.equipment_company_selector)"
        )
    
    # Correção 3: Adicionar chamada para carregar empresas no combobox após a inicialização
    if "equipment_layout.addLayout(equipment_top_container)" in content and "self.load_companies_to_equipment_combobox()" not in content:
        logger.info("Adicionando chamada para carregar empresas no combobox")
        content = content.replace(
            "equipment_layout.addLayout(equipment_top_container)",
            "equipment_layout.addLayout(equipment_top_container)\n            \n            # Carregar empresas no combobox de filtro\n            self.load_companies_to_equipment_combobox()"
        )
    
    # Correção 4: Melhorar método de carregamento de empresas no combobox
    pattern = r'def load_companies_to_equipment_combobox\(self\):.*?(?=def|$)'
    replacement = '''def load_companies_to_equipment_combobox(self):
        """Carrega as empresas no combobox de filtro da aba Equipamentos"""
        try:
            logger.debug("Carregando empresas no combobox de equipamentos")
            self.equipment_company_selector.blockSignals(True)
            self.equipment_company_selector.clear()
            self.equipment_company_selector.addItem("Todas as empresas", None)
            
            # Obter empresas
            companies = self.auth_controller.get_companies()
            logger.debug(f"Obtidas {len(companies)} empresas")
            
            # Adicionar empresas ao combobox
            for company in companies:
                self.equipment_company_selector.addItem(company['nome'], company['id'])
                
            logger.debug("Empresas carregadas com sucesso no combobox de equipamentos")
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no combobox de equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.equipment_company_selector.blockSignals(False)
    
    '''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Correção 5: Melhorar método de filtro por empresa
    pattern = r'def filter_equipment_by_company\(self\):.*?(?=def|$)'
    replacement = '''def filter_equipment_by_company(self):
        """Filtra a tabela de equipamentos pela empresa selecionada no ComboBox"""
        try:
            company_id = self.equipment_company_selector.currentData()
            logger.debug(f"Filtrando equipamentos por empresa ID={company_id}")
            
            for row in range(self.equipment_table.rowCount()):
                item = self.equipment_table.item(row, 2)  # Coluna Empresa
                if company_id is None or (item and int(item.data(Qt.UserRole)) == company_id):
                    self.equipment_table.setRowHidden(row, False)
                else:
                    self.equipment_table.setRowHidden(row, True)
                    
            # Também aplicar o filtro de texto, se houver
            self.filter_equipment(self.equipment_search_box.text())
            logger.debug("Filtro por empresa aplicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos por empresa: {str(e)}")
            logger.error(traceback.format_exc())
    
    '''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Correção 6: Melhorar método de filtro por texto
    pattern = r'def filter_equipment\(self, text\):.*?(?=def|$)'
    replacement = '''def filter_equipment(self, text):
        """Filtra os equipamentos na tabela com base no texto inserido e empresa selecionada"""
        try:
            search_text = text.lower()
            logger.debug(f"Filtrando equipamentos com texto: '{search_text}'")
            
            company_id = self.equipment_company_selector.currentData()
            logger.debug(f"Empresa selecionada ID={company_id}")
            
            for row in range(self.equipment_table.rowCount()):
                should_show = True
                
                # Filtro por empresa
                if company_id is not None:
                    item_empresa = self.equipment_table.item(row, 2)  # Coluna Empresa
                    if not item_empresa or int(item_empresa.data(Qt.UserRole)) != company_id:
                        should_show = False
                        
                # Filtro por texto
                if should_show and search_text:
                    found = False
                    for col in range(self.equipment_table.columnCount()):
                        item = self.equipment_table.item(row, col)
                        if item and search_text in item.text().lower():
                            found = True
                            break
                    should_show = found
                    
                self.equipment_table.setRowHidden(row, not should_show)
                
            logger.debug("Filtro de equipamentos aplicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
    
    '''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Salvar as alterações
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    logger.info(f"Arquivo {file_path} corrigido com sucesso")
    return True

def main():
    """Função principal do script"""
    logger.info("Iniciando correção do arquivo admin_ui.py")
    
    # Caminho para o arquivo admin_ui.py
    ui_file = "ui/admin_ui.py"
    
    # Corrigir o arquivo
    if fix_ui_file(ui_file):
        logger.info("Correção concluída com sucesso!")
        return 0
    else:
        logger.error("Falha ao corrigir o arquivo.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 