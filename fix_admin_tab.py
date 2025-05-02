#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir o problema na aba "Equipamentos por Empresa" na interface de admin.
O erro 'AdminWindow' object has no attribute 'company_equipment_table' ocorre porque
a aba foi adicionada mas não está sendo criada corretamente na inicialização.
"""

import os
import re
import sys
import logging
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("fix_admin_tab")

def backup_file(file_path):
    """Cria uma cópia de backup do arquivo antes de modificá-lo."""
    import shutil
    backup_path = f"{file_path}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup do arquivo criado em: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return False

def fix_admin_ui():
    """Corrige o problema na aba 'Equipamentos por Empresa'."""
    ui_file_path = os.path.join("ui", "admin_ui.py")
    
    if not os.path.exists(ui_file_path):
        logger.error(f"Arquivo não encontrado: {ui_file_path}")
        return False
    
    # Criar backup do arquivo original
    if not backup_file(ui_file_path):
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(ui_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar o método setup_interface para garantir que a aba esteja sendo adicionada corretamente
        setup_pattern = r'def setup_interface\(self\):(.*?)(?=\s{2,}def|\s*$)'
        setup_match = re.search(setup_pattern, content, re.DOTALL)
        
        if setup_match:
            setup_content = setup_match.group(1)
            
            # Verificar se self.company_equipment_tab está sendo definido
            if "self.company_equipment_tab =" not in setup_content:
                # Procurar onde as abas são criadas
                tabs_pattern = r'# Criar abas(.*?)# Adicionar abas ao TabWidget'
                tabs_match = re.search(tabs_pattern, setup_content, re.DOTALL)
                
                if tabs_match:
                    tabs_section = tabs_match.group(1)
                    
                    # Adicionar a criação da aba de equipamentos por empresa
                    company_tab_code = """
            # Aba equipamentos por empresa
            logger.debug("Configurando aba de equipamentos por empresa")
            self.company_equipment_tab = self.create_company_equipment_tab()
"""
                    
                    # Inserir o código após a última aba
                    new_tabs_section = tabs_section + company_tab_code
                    setup_content = setup_content.replace(tabs_section, new_tabs_section)
                    
                    # Procurar onde as abas são adicionadas ao TabWidget
                    add_tabs_pattern = r'# Adicionar abas ao TabWidget(.*?)(?=# Configurar barra inferior|$)'
                    add_tabs_match = re.search(add_tabs_pattern, setup_content, re.DOTALL)
                    
                    if add_tabs_match:
                        add_tabs_section = add_tabs_match.group(1)
                        
                        # Adicionar a nova aba ao TabWidget
                        add_company_tab_code = """
            self.tabs.addTab(self.company_equipment_tab, "")
            logger.debug("Obtendo ícone: equipamentos.png")
            self.tabs.setTabIcon(4, self.get_tab_icon("equipamentos.png"))
"""
                        
                        # Inserir o código após a última adição de aba
                        new_add_tabs_section = add_tabs_section + add_company_tab_code
                        setup_content = setup_content.replace(add_tabs_section, new_add_tabs_section)
                        
                        # Atualizar o conteúdo do método setup_interface
                        content = content.replace(setup_match.group(1), setup_content)
                        logger.info("Método setup_interface atualizado para adicionar a aba 'Equipamentos por Empresa'")
        
        # Verificar se a criação e carregamento do tab está sendo feito no lugar adequado
        init_pattern = r'def __init__\s*\(self, auth_controller\):(.*?)(?=\s{2,}def|\s*$)'
        init_match = re.search(init_pattern, content, re.DOTALL)
        
        if init_match:
            init_content = init_match.group(1)
            
            # Verificar se a aba está sendo adicionada no __init__
            if "self.tabs.addTab(self.create_company_equipment_tab()" in init_content:
                # Remover adição duplicada da aba
                init_content = re.sub(r'\s+self\.tabs\.addTab\(self\.create_company_equipment_tab\(\).*?\n', '', init_content)
                content = content.replace(init_match.group(1), init_content)
                logger.info("Removida adição duplicada da aba no método __init__")
        
        # Corrigir imports
        if "QComboBox" not in content:
            # Adicionar QComboBox ao import de QWidgets
            widgets_import = re.search(r'from PyQt5\.QtWidgets import (.*?)\n', content)
            if widgets_import and "QComboBox" not in widgets_import.group(1):
                new_import = widgets_import.group(1) + ", QComboBox"
                content = content.replace(widgets_import.group(1), new_import)
                logger.info("Adicionado QComboBox às importações")
        
        # Atualizar o arquivo com o conteúdo modificado
        with open(ui_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info("Arquivo ui/admin_ui.py atualizado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de correção para aba 'Equipamentos por Empresa'")
    
    if fix_admin_ui():
        logger.info("Correções aplicadas com sucesso.")
        logger.info("Agora você pode executar o sistema normalmente com 'python main.py'")
    else:
        logger.error("Falha ao aplicar correções. Verifique os logs para mais detalhes.")
        sys.exit(1)
    
    sys.exit(0) 