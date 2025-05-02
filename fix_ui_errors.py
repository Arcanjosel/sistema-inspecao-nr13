#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir os erros na interface de usuário relacionados à aba 'Equipamentos por Empresa'.
Este script modifica o arquivo admin_ui.py para adicionar os métodos necessários.
"""

import os
import re
import sys
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("fix_ui")

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
    """Corrige os erros na classe AdminWindow."""
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
        
        # Verificar se o método company_changed já existe
        if "def company_changed" not in content:
            # Encontrar a posição para inserir o método (após load_equipment_by_company)
            load_equipment_by_company_match = re.search(r'def load_equipment_by_company\s*\(.*?\):.*?(?=\s{2,}def|\s*$)', content, re.DOTALL)
            
            if load_equipment_by_company_match:
                # Inserir o método company_changed após load_equipment_by_company
                end_pos = load_equipment_by_company_match.end()
                
                company_changed_method = """
    def company_changed(self, index):
        # Chamado quando a empresa selecionada é alterada
        try:
            # Obter o ID da empresa selecionada
            company_id = self.company_selector.currentData()
            
            # Atualizar a tabela de equipamentos
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao mudar empresa selecionada: {str(e)}")
            logger.error(traceback.format_exc())
            
    def add_equipment_to_company(self):
        # Adiciona um novo equipamento à empresa selecionada
        try:
            # Verificar se uma empresa está selecionada
            company_id = self.company_selector.currentData()
            if company_id is None:
                QMessageBox.warning(self, "Atenção", "Selecione uma empresa primeiro.")
                return
                
            # Reutilizar o método existente, mas pré-configurar a empresa
            modal = EquipmentModal(self, self.is_dark)
            
            # Carregar apenas a empresa selecionada no modal
            company_data = {
                'id': company_id,
                'nome': self.company_selector.currentText()
            }
            modal.load_company_options([company_data])
            
            if modal.exec() == QDialog.Accepted:
                equipment_data = modal.get_data()
                
                # Garantir que o ID da empresa está correto
                equipment_data['empresa_id'] = company_id
                
                # Criar o equipamento
                success, message = self.equipment_controller.criar_equipamento(
                    tag=equipment_data['tag'],
                    categoria=equipment_data['categoria'],
                    empresa_id=equipment_data['empresa_id'],
                    fabricante=equipment_data['fabricante'],
                    ano_fabricacao=equipment_data['ano_fabricacao'],
                    pressao_projeto=equipment_data['pressao_projeto'],
                    pressao_trabalho=equipment_data['pressao_trabalho'],
                    volume=equipment_data['volume'],
                    fluido=equipment_data['fluido']
                )
                
                # Força a sincronização
                self.equipment_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_equipment_by_company(company_id)
                    # Atualizar também a aba de equipamentos geral
                    self.load_equipment()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao adicionar equipamento à empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar equipamento: {str(e)}")
            
    def edit_company_equipment(self):
        # Edita o equipamento selecionado na aba de empresa
        try:
            # Obter o ID do equipamento selecionado
            selected_row = self.company_equipment_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para editar.")
                return
                
            # Obter o ID do equipamento (armazenado no UserRole da coluna Tag)
            item = self.company_equipment_table.item(selected_row, 0)
            if not item:
                QMessageBox.warning(self, "Erro", "Falha ao obter o equipamento selecionado.")
                return
                
            equipment_id = item.data(Qt.UserRole)
            
            # Reusar o método existente
            self.edit_equipment(equipment_id)
            
            # Atualizar a tabela após a edição
            company_id = self.company_selector.currentData()
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao editar equipamento da empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao editar equipamento: {str(e)}")
            
    def delete_company_equipment(self):
        # Remove o equipamento selecionado na aba de empresa
        try:
            # Obter o ID do equipamento selecionado
            selected_row = self.company_equipment_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para remover.")
                return
                
            # Obter o ID do equipamento (armazenado no UserRole da coluna Tag)
            item = self.company_equipment_table.item(selected_row, 0)
            if not item:
                QMessageBox.warning(self, "Erro", "Falha ao obter o equipamento selecionado.")
                return
                
            equipment_id = item.data(Qt.UserRole)
            
            # Reutilizar o método existente
            self.delete_equipment(equipment_id)
            
            # Atualizar a tabela após a remoção
            company_id = self.company_selector.currentData()
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao remover equipamento da empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao remover equipamento: {str(e)}")
            
    def load_companies_to_combobox(self):
        # Carrega as empresas no combobox de seleção
        try:
            self.company_selector.clear()
            
            # Adicionar item padrão
            self.company_selector.addItem("Selecione uma empresa", None)
            
            # Obter empresas
            companies = self.auth_controller.get_companies()
            
            # Adicionar cada empresa ao combobox
            for company in companies:
                self.company_selector.addItem(company['nome'], company['id'])
                
            logger.debug(f"Carregadas {len(companies)} empresas no combobox")
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no combobox: {str(e)}")
            logger.error(traceback.format_exc())
"""
                
                # Inserir o método no arquivo
                content = content[:end_pos] + company_changed_method + content[end_pos:]
                logger.info("Método company_changed adicionado ao arquivo")
        
        # Verificar e corrigir o método create_company_equipment_tab
        if "def create_company_equipment_tab" not in content:
            # Encontrar a posição para inserir o método (antes de load_equipment_by_company)
            logout_match = re.search(r'def logout\s*\(.*?\):.*?(?=\s{2,}def|\s*$)', content, re.DOTALL)
            
            if logout_match:
                # Inserir o método create_company_equipment_tab após logout
                end_pos = logout_match.end()
                
                create_tab_method = """
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
            
            # Tabela de equipamentos da empresa
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
                
                # Inserir o método no arquivo
                content = content[:end_pos] + create_tab_method + content[end_pos:]
                logger.info("Método create_company_equipment_tab adicionado ao arquivo")
        
        # Adicionar o método load_equipment_by_company se necessário
        if "def load_equipment_by_company" not in content:
            # Encontrar a posição para inserir o método (após create_company_equipment_tab)
            create_tab_match = re.search(r'def create_company_equipment_tab\s*\(.*?\):.*?(?=\s{2,}def|\s*$)', content, re.DOTALL)
            
            if create_tab_match:
                # Inserir o método load_equipment_by_company após create_company_equipment_tab
                end_pos = create_tab_match.end()
                
                load_equipment_method = """
    def load_equipment_by_company(self, company_id=None):
        # Carrega os equipamentos de uma empresa específica na tabela
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
                
                # Inserir o método no arquivo
                content = content[:end_pos] + load_equipment_method + content[end_pos:]
                logger.info("Método load_equipment_by_company adicionado ao arquivo")
        
        # Corrigir o método apply_theme para incluir a nova tabela
        apply_theme_pattern = r'def apply_theme\s*\(.*?\):(.*?)(?=\s{2,}def|\s*$)'
        apply_theme_match = re.search(apply_theme_pattern, content, re.DOTALL)
        
        if apply_theme_match:
            apply_theme_content = apply_theme_match.group(1)
            
            # Verificar se a tabela company_equipment_table já está incluída
            if "company_equipment_table" not in apply_theme_content:
                # Adicionar a tabela nos lugares apropriados
                tables_dark_pattern = r'(self.user_table.setStyleSheet\(table_style\).*?)(?=\s+# Ativa cores alternadas)'
                tables_light_pattern = r'(self.user_table.setStyleSheet\(table_style\).*?)(?=\s+# Ativa cores alternadas)'
                
                # Para o modo escuro
                dark_tables = re.search(tables_dark_pattern, apply_theme_content, re.DOTALL)
                if dark_tables:
                    new_dark_tables = dark_tables.group(1) + "\n                self.company_equipment_table.setStyleSheet(table_style)"
                    apply_theme_content = apply_theme_content.replace(dark_tables.group(1), new_dark_tables)
                
                # Para o modo escuro - cores alternadas
                dark_alt_pattern = r'(self.user_table.setAlternatingRowColors\(True\).*?)(?=\s+else)'
                dark_alt = re.search(dark_alt_pattern, apply_theme_content, re.DOTALL)
                if dark_alt:
                    new_dark_alt = dark_alt.group(1) + "\n                self.company_equipment_table.setAlternatingRowColors(True)"
                    apply_theme_content = apply_theme_content.replace(dark_alt.group(1), new_dark_alt)
                
                # Para o modo claro
                light_tables = re.search(tables_light_pattern, apply_theme_content, re.DOTALL)
                if light_tables:
                    new_light_tables = light_tables.group(1) + "\n                self.company_equipment_table.setStyleSheet(table_style)"
                    apply_theme_content = apply_theme_content.replace(light_tables.group(1), new_light_tables)
                
                # Para o modo claro - cores alternadas
                light_alt_pattern = r'(self.user_table.setAlternatingRowColors\(True\).*?)(?=\s+# Atualiza os ícones)'
                light_alt = re.search(light_alt_pattern, apply_theme_content, re.DOTALL)
                if light_alt:
                    new_light_alt = light_alt.group(1) + "\n                self.company_equipment_table.setAlternatingRowColors(True)"
                    apply_theme_content = apply_theme_content.replace(light_alt.group(1), new_light_alt)
                
                # Atualizar o ícone da nova aba
                icons_pattern = r'(self.tabs.setTabIcon\(3, self.get_tab_icon\("relatorios.png"\)\).*?)(?=\s+# Atualiza o botão)'
                icons = re.search(icons_pattern, apply_theme_content, re.DOTALL)
                if icons:
                    new_icons = icons.group(1) + "\n            self.tabs.setTabIcon(4, self.get_tab_icon(\"equipamentos.png\"))  # Ícone para a aba de Equipamentos por Empresa"
                    apply_theme_content = apply_theme_content.replace(icons.group(1), new_icons)
                
                # Atualizar o conteúdo do método apply_theme
                content = content.replace(apply_theme_match.group(1), apply_theme_content)
                logger.info("Método apply_theme atualizado para incluir a nova tabela")
        
        # Atualizar o arquivo com o conteúdo modificado
        with open(ui_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info("Arquivo ui/admin_ui.py atualizado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de correção da interface de usuário")
    
    if fix_admin_ui():
        logger.info("Correções aplicadas com sucesso.")
        logger.info("Agora você pode executar o sistema normalmente com 'python main.py'")
    else:
        logger.error("Falha ao aplicar correções. Verifique os logs para mais detalhes.")
        sys.exit(1)
    
    sys.exit(0) 