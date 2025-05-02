#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir problemas no modal de equipamentos e garantir que
a associação com a empresa seja feita corretamente.
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

logger = logging.getLogger("fix_equipment")

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

def fix_equipment_modal():
    """Corrige o modal de equipamentos para garantir associação correta com a empresa."""
    modals_file_path = os.path.join("ui", "modals.py")
    
    if not os.path.exists(modals_file_path):
        logger.error(f"Arquivo não encontrado: {modals_file_path}")
        return False
    
    # Criar backup do arquivo original
    if not backup_file(modals_file_path):
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(modals_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Corrigir o método get_data da classe EquipmentModal
        get_data_pattern = r'def get_data\(self\):(.*?)return data'
        get_data_match = re.search(get_data_pattern, content, re.DOTALL)
        
        if get_data_match:
            get_data_content = get_data_match.group(1)
            
            # Verificar se o campo empresa_id está sendo incluído corretamente
            if "empresa_id" not in get_data_content or "currentData" not in get_data_content:
                # Substituir o método get_data por uma versão corrigida
                new_get_data = """
    def get_data(self):
        # Retorna os dados do formulário
        # Verificar se a empresa foi selecionada
        empresa_id = self.empresa_input.currentData()
        
        # Se não houver empresa selecionada, tentar obter do primeiro item
        if empresa_id is None and self.empresa_input.count() > 0:
            empresa_id = self.empresa_input.itemData(0)
            logger.debug(f"Usando primeira empresa disponível: ID={empresa_id}")
        
        data = {
            'tag': self.tag_input.text().strip(),
            'categoria': self.categoria_input.currentText(),
            'empresa_id': empresa_id,
            'fabricante': self.fabricante_input.text().strip(),
            'ano_fabricacao': int(self.ano_fabricacao_input.text()) if self.ano_fabricacao_input.text().strip() else None,
            'pressao_projeto': float(self.pressao_projeto_input.text()) if self.pressao_projeto_input.text().strip() else None,
            'pressao_trabalho': float(self.pressao_trabalho_input.text()) if self.pressao_trabalho_input.text().strip() else None,
            'volume': float(self.volume_input.text()) if self.volume_input.text().strip() else None,
            'fluido': self.fluido_input.text().strip()
        }
        
        logger.debug(f"Dados do equipamento: {data}")
        return data"""
                
                # Substituir o método no conteúdo
                content = re.sub(get_data_pattern, new_get_data, content, flags=re.DOTALL)
                logger.info("Método get_data atualizado na classe EquipmentModal")
        
        # Verificar a inicialização da combobox de empresas
        init_pattern = r'def __init__\s*\(self, parent=None, is_dark=False\):(.*?)self.setup_ui\(\)'
        init_match = re.search(init_pattern, content, re.DOTALL)
        
        if init_match:
            init_content = init_match.group(1)
            
            # Verificar inicialização do controlador de autenticação
            if "self.auth_controller = AuthController()" not in init_content:
                # Adicionar importação se necessário
                if "from controllers.auth_controller import AuthController" not in content:
                    imports_end = content.find("\n\n", content.find("import"))
                    content = content[:imports_end] + "\nfrom controllers.auth_controller import AuthController" + content[imports_end:]
                    logger.info("Adicionada importação do AuthController")
                
                # Adicionar inicialização do controlador
                new_init = init_content + "        self.auth_controller = AuthController()\n        "
                content = content.replace(init_content, new_init)
                logger.info("Adicionada inicialização do AuthController na classe EquipmentModal")
        
        # Verificar e corrigir o método setup_ui para usar ComboBox para empresas
        setup_ui_pattern = r'def setup_ui\(self\):(.*?)(?=\s{2,}def|\s*$)'
        setup_ui_match = re.search(setup_ui_pattern, content, re.DOTALL)
        
        if setup_ui_match:
            setup_ui_content = setup_ui_match.group(1)
            
            # Verificar se empresa_input é um QComboBox
            if "self.empresa_input = QLineEdit" in setup_ui_content:
                # Substituir QLineEdit por QComboBox
                new_empresa_widget = """        # Empresa (ComboBox)
        empresa_label = QLabel("Empresa:")
        empresa_label.setStyleSheet(label_style)
        self.empresa_input = QComboBox()
        self.empresa_input.setMinimumHeight(30)
        self.load_company_options()
        form_layout.addRow(empresa_label, self.empresa_input)"""
                
                # Substituir no conteúdo
                content = content.replace("        # Empresa\n        empresa_label = QLabel(\"Empresa:\")\n        empresa_label.setStyleSheet(label_style)\n        self.empresa_input = QLineEdit()\n        self.empresa_input.setMinimumHeight(30)\n        form_layout.addRow(empresa_label, self.empresa_input)", new_empresa_widget)
                logger.info("Substituído QLineEdit por QComboBox para o campo empresa_input")
                
                # Adicionar método load_company_options
                if "def load_company_options" not in content:
                    load_companies_method = """
    def load_company_options(self, companies=None):
        # Carrega as opções de empresas no combobox
        try:
            self.empresa_input.clear()
            
            # Se já recebemos a lista de empresas, usamos ela
            if not companies:
                # Caso contrário, buscamos do controlador de autenticação
                companies = self.auth_controller.get_companies()
            
            # Adicionar cada empresa ao combobox
            for company in companies:
                self.empresa_input.addItem(company['nome'], company['id'])
                
            logger.debug(f"Carregadas {len(companies)} empresas no combobox do modal")
            
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no combobox do modal: {str(e)}")
            logger.error(traceback.format_exc())
"""
                    
                    # Adicionar o método após setup_ui
                    end_pos = setup_ui_match.end()
                    content = content[:end_pos] + load_companies_method + content[end_pos:]
                    logger.info("Adicionado método load_company_options à classe EquipmentModal")
        
        # Verificar método validate
        validate_pattern = r'def validate\(self\):(.*?)return True'
        validate_match = re.search(validate_pattern, content, re.DOTALL)
        
        if validate_match:
            validate_content = validate_match.group(1)
            
            # Verificar se validação da empresa está presente
            if "empresa_id" not in validate_content:
                # Adicionar validação da empresa
                new_validation = """        # Validar tag
        if not self.tag_input.text().strip():
            QMessageBox.warning(self, "Validação", "O campo Tag é obrigatório")
            return False
            
        # Validar empresa
        if self.empresa_input.currentData() is None:
            QMessageBox.warning(self, "Validação", "Selecione uma empresa válida")
            return False
        
        # Validar categoria
        if not self.categoria_input.currentText():
            QMessageBox.warning(self, "Validação", "Selecione uma categoria")
            return False"""
                
                # Substituir no conteúdo
                content = content.replace("        # Validar tag\n        if not self.tag_input.text().strip():\n            QMessageBox.warning(self, \"Validação\", \"O campo Tag é obrigatório\")\n            return False\n        \n        # Validar categoria\n        if not self.categoria_input.currentText():\n            QMessageBox.warning(self, \"Validação\", \"Selecione uma categoria\")\n            return False", new_validation)
                logger.info("Adicionada validação para o campo empresa_id")
        
        # Atualizar o arquivo com o conteúdo modificado
        with open(modals_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info("Arquivo ui/modals.py atualizado com sucesso")
        
        # Corrigir também o controlador de equipamentos
        equipment_controller_path = os.path.join("controllers", "equipment_controller.py")
        if os.path.exists(equipment_controller_path):
            # Fazer backup
            if not backup_file(equipment_controller_path):
                return False
            
            # Ler conteúdo
            with open(equipment_controller_path, 'r', encoding='utf-8') as file:
                eq_content = file.read()
            
            # Verificar o método criar_equipamento
            criar_pattern = r'def criar_equipamento\(self,.*?empresa_id.*?\):(.*?)return True, "Equipamento criado com sucesso"'
            criar_match = re.search(criar_pattern, eq_content, re.DOTALL)
            
            if criar_match:
                criar_content = criar_match.group(1)
                
                # Verificar se há debug para empresa_id
                if "empresa_id" not in criar_content or "Empresa ID:" not in criar_content:
                    # Adicionar log para empresa_id
                    log_line = "            logger.debug(f\"Criar equipamento: {tag} | Empresa ID: {empresa_id}\")"
                    
                    # Encontrar onde adicionar o log
                    new_content = criar_content.replace("            logger.debug(f\"Criar equipamento: {tag}\")", log_line)
                    
                    # Atualizar o conteúdo
                    eq_content = eq_content.replace(criar_content, new_content)
                    logger.info("Adicionado log de debug para empresa_id em criar_equipamento")
                
                # Verificar se empresa_id está sendo usado na query SQL
                if "empresa_id = ?" not in criar_content:
                    # Corrigir a query para usar empresa_id
                    old_query = "INSERT INTO equipamentos (tag, categoria, empresa, fabricante, ano_fabricacao, pressao_projeto, pressao_trabalho, volume, fluido) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    new_query = "INSERT INTO equipamentos (tag, categoria, empresa_id, fabricante, ano_fabricacao, pressao_projeto, pressao_trabalho, volume, fluido) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    
                    # Atualizar o conteúdo
                    eq_content = eq_content.replace(old_query, new_query)
                    logger.info("Corrigida query SQL em criar_equipamento para usar empresa_id")
            
            # Atualizar o arquivo
            with open(equipment_controller_path, 'w', encoding='utf-8') as file:
                file.write(eq_content)
            
            logger.info("Arquivo controllers/equipment_controller.py atualizado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de correção do modal de equipamentos")
    
    if fix_equipment_modal():
        logger.info("Correções aplicadas com sucesso.")
        logger.info("Agora você pode executar o sistema normalmente com 'python main.py'")
    else:
        logger.error("Falha ao aplicar correções. Verifique os logs para mais detalhes.")
        sys.exit(1)
    
    sys.exit(0) 