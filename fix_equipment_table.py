#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir o erro 'AdminWindow' object has no attribute 'company_equipment_table'
Este script corrige especificamente o problema de inicialização da tabela de equipamentos por empresa.
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

logger = logging.getLogger("fix_equipment_table")

def backup_file(file_path):
    """Cria uma cópia de backup do arquivo antes de modificá-lo."""
    import shutil
    backup_path = f"{file_path}.bak.{int(time.time())}"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup do arquivo criado em: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return False

def fix_admin_ui():
    """Corrige o problema de inicialização da tabela company_equipment_table."""
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
        
        # Verificar e corrigir o método create_company_equipment_tab
        create_tab_pattern = r'def create_company_equipment_tab\(self\):(.*?)return company_equipment_tab'
        create_tab_match = re.search(create_tab_pattern, content, re.DOTALL)
        
        if create_tab_match:
            create_tab_content = create_tab_match.group(1)
            
            # Verificar se a tabela está sendo definida como atributo de classe
            if "self.company_equipment_table =" not in create_tab_content:
                # Substituir a criação da tabela para definir como atributo de classe
                old_table_code = "company_equipment_table = QTableWidget()"
                new_table_code = "self.company_equipment_table = QTableWidget()"
                
                if old_table_code in create_tab_content:
                    create_tab_content = create_tab_content.replace(old_table_code, new_table_code)
                    logger.info("Corrigida a definição da tabela como atributo de classe")
                else:
                    # Se não encontrou o padrão exato, tenta um mais genérico
                    table_pattern = r'(\s+)([a-zA-Z_]+)? ?= ?QTableWidget\(\)'
                    table_match = re.search(table_pattern, create_tab_content)
                    if table_match:
                        indent = table_match.group(1)
                        create_tab_content = re.sub(
                            table_pattern, 
                            f"{indent}self.company_equipment_table = QTableWidget()", 
                            create_tab_content, 
                            count=1
                        )
                        logger.info("Corrigida a definição da tabela como atributo de classe (padrão genérico)")
            
            # Garantir que a tabela de equipamentos por empresa é exposta corretamente
            if "self.company_equipment_table" not in content:
                # Adicionar uma inicialização segura no __init__
                init_pattern = r'def __init__\s*\(self, auth_controller\):(.*?)\s{8}(?=\w)'
                init_match = re.search(init_pattern, content, re.DOTALL)
                
                if init_match:
                    init_content = init_match.group(1)
                    # Adicionar inicialização da tabela como None
                    if "self.company_equipment_table = None" not in init_content:
                        new_init_content = init_content.rstrip() + "\n        # Inicialização segura da tabela de equipamentos por empresa\n        self.company_equipment_table = None\n        "
                        content = content.replace(init_content, new_init_content)
                        logger.info("Adicionada inicialização segura da tabela no __init__")
            
            # Atualizar o conteúdo do método create_company_equipment_tab
            content = content.replace(create_tab_match.group(1), create_tab_content)
        else:
            # Se não encontrou o método, vamos criar um do zero
            company_equipment_tab_method = """
    def create_company_equipment_tab(self):
        # Cria e configura a aba 'Equipamentos por Empresa'
        try:
            # Criar widget da aba
            company_equipment_tab = QWidget()
            tab_layout = QVBoxLayout(company_equipment_tab)
            
            # Área superior - seleção de empresa
            top_container = QHBoxLayout()
            
            # Label para seleção de empresa
            company_label = QLabel("Selecione a Empresa:")
            company_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            top_container.addWidget(company_label)
            
            # ComboBox para seleção de empresa
            self.company_selector = QComboBox()
            self.company_selector.setMinimumWidth(250)
            self.company_selector.setMinimumHeight(36)
            self.company_selector.currentIndexChanged.connect(self.company_changed)
            
            # Carregar empresas no combobox
            self.load_companies_to_combobox()
            
            top_container.addWidget(self.company_selector)
            top_container.addStretch()
            
            # Botões de ação para equipamentos
            buttons_container = QHBoxLayout()
            
            # Botão Adicionar Equipamento
            self.add_company_equipment_button = self.create_crud_button("add", "Adicionar", self.add_equipment_to_company)
            buttons_container.addWidget(self.add_company_equipment_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Editar Equipamento
            self.edit_company_equipment_button = self.create_crud_button("edit", "Editar", self.edit_company_equipment)
            buttons_container.addWidget(self.edit_company_equipment_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Remover Equipamento
            self.remove_company_equipment_button = self.create_crud_button("delete", "Remover", self.delete_company_equipment)
            buttons_container.addWidget(self.remove_company_equipment_button)
            
            buttons_container.addStretch()
            
            # Tabela de equipamentos da empresa - IMPORTANTE: usar self. para torná-la um atributo da classe
            self.company_equipment_table = QTableWidget()
            self.company_equipment_table.setColumnCount(9)  # Sem a coluna de Empresa
            self.company_equipment_table.setHorizontalHeaderLabels([
                "Tag", "Categoria", "Fabricante", "Ano Fabricação", 
                "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido", "Status"
            ])
            self.company_equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.company_equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.company_equipment_table.setSelectionMode(QTableWidget.SingleSelection)
            self.company_equipment_table.setAlternatingRowColors(True)
            self.company_equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.company_equipment_table.verticalHeader().setVisible(False)
            
            # Adicionar elementos ao layout da aba
            tab_layout.addLayout(top_container)
            tab_layout.addLayout(buttons_container)
            tab_layout.addWidget(self.company_equipment_table)
            
            return company_equipment_tab
            
        except Exception as e:
            logger.error(f"Erro ao criar aba 'Equipamentos por Empresa': {str(e)}")
            logger.error(traceback.format_exc())
            # Retorna um widget vazio em caso de erro
            return QWidget()
    """
            
            # Adicionar o método após o método logout
            logout_pattern = r'def logout\(self\):(.*?)(?=\s{4}def|\s*$)'
            logout_match = re.search(logout_pattern, content, re.DOTALL)
            
            if logout_match:
                content = content.replace(
                    logout_match.group(0), 
                    logout_match.group(0) + company_equipment_tab_method
                )
                logger.info("Adicionado método create_company_equipment_tab do zero")
            
        # Verificar e corrigir o método load_equipment_by_company
        load_equip_pattern = r'def load_equipment_by_company\(self, company_id=None\):(.*?)(?=\s{4}def|\s*$)'
        load_equip_match = re.search(load_equip_pattern, content, re.DOTALL)
        
        if load_equip_match:
            load_equip_content = load_equip_match.group(1)
            
            # Adicionar verificação de existência da tabela
            if "if not hasattr(self, 'company_equipment_table')" not in load_equip_content:
                # Adicionar verificação no início do método
                first_line_pattern = r'(\s+)try:'
                first_line_match = re.search(first_line_pattern, load_equip_content)
                
                if first_line_match:
                    indent = first_line_match.group(1)
                    check_code = f"{indent}# Verificar se a tabela existe\n{indent}if not hasattr(self, 'company_equipment_table') or self.company_equipment_table is None:\n{indent}    logger.warning(\"Tabela de equipamentos por empresa não foi inicializada. Inicializando...\")\n{indent}    self.company_equipment_table = QTableWidget()\n{indent}    self.company_equipment_table.setColumnCount(9)\n{indent}    self.company_equipment_table.setHorizontalHeaderLabels([\n{indent}        \"Tag\", \"Categoria\", \"Fabricante\", \"Ano Fabricação\", \n{indent}        \"Pressão Projeto\", \"Pressão Trabalho\", \"Volume\", \"Fluido\", \"Status\"\n{indent}    ])\n\n"
                    
                    new_load_equip_content = re.sub(first_line_pattern, check_code + first_line_match.group(0), load_equip_content, count=1)
                    content = content.replace(load_equip_content, new_load_equip_content)
                    logger.info("Adicionada verificação de existência da tabela em load_equipment_by_company")
        else:
            # Se não encontrou o método, criar do zero
            load_equip_method = """
    def load_equipment_by_company(self, company_id=None):
        # Carrega os equipamentos de uma empresa específica na tabela
        # Verificar se a tabela existe
        if not hasattr(self, 'company_equipment_table') or self.company_equipment_table is None:
            logger.warning("Tabela de equipamentos por empresa não foi inicializada. Inicializando...")
            self.company_equipment_table = QTableWidget()
            self.company_equipment_table.setColumnCount(9)
            self.company_equipment_table.setHorizontalHeaderLabels([
                "Tag", "Categoria", "Fabricante", "Ano Fabricação", 
                "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido", "Status"
            ])
        
        try:
            logger.debug(f"Carregando equipamentos para empresa ID={company_id}")
            if company_id is None:
                # Se nenhuma empresa for selecionada, limpa a tabela
                self.company_equipment_table.setRowCount(0)
                return
                
            # Obter todos os equipamentos
            all_equipment = self.equipment_controller.get_all_equipment()
            
            # Filtrar apenas os da empresa selecionada
            company_equipment = [e for e in all_equipment if e.get('empresa_id') == company_id]
            
            # Configurar a tabela
            self.company_equipment_table.setRowCount(len(company_equipment))
            
            for i, item in enumerate(company_equipment):
                # Armazena o ID como dados do item (invisível para o usuário)
                equip_id = item.get('id', '')
                
                # Tag
                tag_item = QTableWidgetItem(item.get('tag', ''))
                tag_item.setData(Qt.UserRole, equip_id)  # Armazena o ID como dado do item
                tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)  # Remove a flag de editável
                self.company_equipment_table.setItem(i, 0, tag_item)
                
                # Resto dos campos - todos configurados como não editáveis
                categoria_item = QTableWidgetItem(item.get('categoria', ''))
                categoria_item.setFlags(categoria_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 1, categoria_item)
                
                fabricante_item = QTableWidgetItem(item.get('fabricante', ''))
                fabricante_item.setFlags(fabricante_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 2, fabricante_item)
                
                ano_item = QTableWidgetItem(str(item.get('ano_fabricacao', '')))
                ano_item.setFlags(ano_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 3, ano_item)
                
                pressao_projeto_item = QTableWidgetItem(str(item.get('pressao_projeto', '')))
                pressao_projeto_item.setFlags(pressao_projeto_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 4, pressao_projeto_item)
                
                pressao_trabalho_item = QTableWidgetItem(str(item.get('pressao_trabalho', '')))
                pressao_trabalho_item.setFlags(pressao_trabalho_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 5, pressao_trabalho_item)
                
                volume_item = QTableWidgetItem(str(item.get('volume', '')))
                volume_item.setFlags(volume_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 6, volume_item)
                
                fluido_item = QTableWidgetItem(item.get('fluido', ''))
                fluido_item.setFlags(fluido_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 7, fluido_item)
                
                # Status
                status = "Ativo" if item.get('ativo', 1) else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 8, status_item)
            
            logger.debug(f"Carregados {len(company_equipment)} equipamentos da empresa na tabela")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos por empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos por empresa: {str(e)}")
    """
            
            # Adicionar o método após o método create_company_equipment_tab
            create_tab_pattern = r'def create_company_equipment_tab\(self\):(.*?)(?=\s{4}def|\s*$)'
            create_tab_match = re.search(create_tab_pattern, content, re.DOTALL)
            
            if create_tab_match:
                content = content.replace(
                    create_tab_match.group(0), 
                    create_tab_match.group(0) + load_equip_method
                )
                logger.info("Adicionado método load_equipment_by_company do zero")
        
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
    import time
    logger.info("Iniciando script de correção para a tabela de equipamentos por empresa")
    
    if fix_admin_ui():
        logger.info("Correções aplicadas com sucesso.")
        logger.info("Agora você pode executar o sistema normalmente com 'python main.py'")
    else:
        logger.error("Falha ao aplicar correções. Verifique os logs para mais detalhes.")
        sys.exit(1)
    
    sys.exit(0) 