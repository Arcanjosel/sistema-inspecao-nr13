#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir o erro AttributeError relacionado a 'report_inspecao_combo'
na geração de relatórios a partir de inspeções na interface de admin.
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

logger = logging.getLogger("fix_report_gen")

def backup_file(file_path):
    """Cria uma cópia de backup do arquivo antes de modificá-lo."""
    import shutil
    import time # Adicionado import time
    backup_path = f"{file_path}.bak.{int(time.time())}" # Adiciona timestamp ao backup
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup do arquivo criado em: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return False

def fix_admin_ui():
    """Corrige o método generate_report_from_inspection."""
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
        
        # Verificar o método generate_report_from_inspection
        gen_report_pattern = r'def generate_report_from_inspection\(self, inspection_id\):.*?try:(.*?)QMessageBox\.critical\(self, "Erro", f"Erro inesperado: {str\(e\)}"\)'
        gen_report_match = re.search(gen_report_pattern, content, re.DOTALL)
        
        if gen_report_match:
            gen_report_content = gen_report_match.group(1)
            
            # Verificar se o acesso ao combo box está incorreto
            if "self.report_inspecao_combo" in gen_report_content:
                # Substituir o método por uma versão corrigida
                new_gen_report_method = """
    def generate_report_from_inspection(self, inspection_id):
        # Abre o modal de relatório pré-preenchido com a inspeção selecionada.
        try:
            logger.info(f"Gerando relatório para a inspeção ID: {inspection_id}")
            
            # Obter detalhes da inspeção
            inspection = self.inspection_controller.get_inspection_by_id(inspection_id)
            if not inspection:
                QMessageBox.warning(self, "Atenção", f"Inspeção com ID {inspection_id} não encontrada.")
                return
                
            logger.debug(f"Inspeção {inspection_id} encontrada")
            
            # Criar o modal de relatório
            modal = ReportModal(self, self.is_dark)
            
            # Carregar apenas a inspeção relevante no combobox do modal
            # Formatar a data para exibição amigável
            try:
                data_realizacao = datetime.strptime(inspection['data_realizacao'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                data_realizacao = inspection['data_realizacao'] # Usar a string original se o formato for inesperado
            
            # Montar texto de exibição para o combo
            display_text = f"ID {inspection['id']} - {inspection['tipo']} em {data_realizacao} (Eq: {inspection.get('tag_equipamento', 'N/A')})"
            
            # Limpar e adicionar a inspeção ao combo do modal
            modal.inspecao_combo.clear()
            modal.inspecao_combo.addItem(display_text, inspection_id) # userData é o ID da inspeção
            modal.inspecao_combo.setCurrentIndex(0) # Selecionar a única opção
            modal.inspecao_combo.setEnabled(False) # Desabilitar para não mudar
            
            # Pré-preencher data de emissão (data atual)
            modal.data_input.setDate(QDate.currentDate())
            
            # Abrir o modal
            if modal.exec() == QDialog.Accepted:
                report_data = modal.get_data()
                
                # Garantir que o ID da inspeção está correto (caso o combo fosse editável)
                report_data['inspecao_id'] = inspection_id 
                
                logger.debug(f"Dados do relatório para salvar: {report_data}")
                
                # Criar o relatório usando o controlador
                success, message = self.report_controller.create_report(
                    inspecao_id=report_data['inspecao_id'],
                    data_emissao=report_data['data_emissao'],
                    observacoes=report_data['observacoes'],
                    link_arquivo=report_data.get('link_arquivo') # Usar get para segurança
                )
                
                self.report_controller.force_sync() # Força a sincronização
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_reports() # Recarregar a tabela de relatórios
                else:
                    QMessageBox.critical(self, "Erro", message)
            else:
                logger.info("Criação de relatório cancelada pelo usuário.")
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório a partir da inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
"""
                
                # Usar um padrão que capture o método inteiro de forma mais robusta
                method_pattern = r'(def generate_report_from_inspection\(self, inspection_id\):.*?)\n\s{4}(?=def|class|@|"""|#|$)' # Procura pelo fim do método
                
                # Substituir o método antigo pelo novo no conteúdo do arquivo
                content = re.sub(method_pattern, new_gen_report_method.strip() + "\n", content, flags=re.DOTALL)
                logger.info("Método generate_report_from_inspection corrigido para usar o modal corretamente.")
            else:
                logger.info("Método generate_report_from_inspection já parece estar correto.")
        else:
            logger.warning("Não foi possível encontrar o método generate_report_from_inspection no arquivo.")
        
        # Adicionar importações necessárias se estiverem faltando
        required_imports = [
            "from PyQt5.QtCore import QDate",
            "from PyQt5.QtWidgets import QDialog, QMessageBox",
            "from ui.modals import ReportModal",
            "from datetime import datetime"
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            # Encontrar a última linha de importação
            last_import_match = list(re.finditer(r"^import |^from .* import .*", content, re.MULTILINE))[-1]
            insert_pos = last_import_match.end()
            
            # Construir string de importações faltantes
            imports_to_add = "\n" + "\n".join(missing_imports) + "\n"
            
            # Inserir as importações
            content = content[:insert_pos] + imports_to_add + content[insert_pos:]
            logger.info(f"Adicionadas importações faltantes: {missing_imports}")
        
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
    logger.info("Iniciando script de correção para geração de relatório a partir de inspeção")
    
    if fix_admin_ui():
        logger.info("Correções aplicadas com sucesso.")
        logger.info("Agora você pode executar o sistema normalmente com 'python main.py'")
    else:
        logger.error("Falha ao aplicar correções. Verifique os logs para mais detalhes.")
        sys.exit(1)
    
    sys.exit(0) 