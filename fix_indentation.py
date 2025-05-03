#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir o erro de indentação no arquivo admin_ui.py na linha 1950.
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

def fix_indentation(file_path):
    """Corrige o erro de indentação no arquivo admin_ui.py"""
    if not os.path.isfile(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    # Fazer backup do arquivo original
    backup_file(file_path)
    
    # Ler o conteúdo do arquivo
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Procura o padrão do erro (linha com "if success:" seguida de uma linha sem a indentação correta)
    for i in range(len(lines) - 1):
        # Verifica se a linha atual contém "if success:" e a linha seguinte não está indentada corretamente
        if "if success:" in lines[i]:
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            next_line_indent = len(lines[i+1]) - len(lines[i+1].lstrip())
            
            # Se a indentação da próxima linha for igual ou menor, corrigir
            if next_line_indent <= current_indent:
                # Adiciona 4 espaços de indentação ao início da próxima linha
                lines[i+1] = ' ' * (current_indent + 4) + lines[i+1].lstrip()
                
                # Verifica as próximas linhas até encontrar uma linha com indentação menor ou igual à linha do if
                j = i + 2
                while j < len(lines):
                    line_indent = len(lines[j]) - len(lines[j].lstrip())
                    if line_indent <= current_indent:
                        # Se a indentação for menor ou igual, saímos do bloco e paramos
                        break
                    
                    # Se a indentação for igual à linha do "if success:" + 4, está correto, continuar
                    elif line_indent == current_indent + 4:
                        j += 1
                        continue
                    
                    # Se a indentação for menor que a linha do "if success:" + 4, precisa corrigir
                    elif line_indent < current_indent + 4:
                        lines[j] = ' ' * (current_indent + 4) + lines[j].lstrip()
                    
                    j += 1
    
    # Escrever o conteúdo modificado de volta no arquivo
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    logger.info(f"Arquivo {file_path} corrigido com sucesso")
    return True

def main():
    """Função principal do script"""
    logger.info("Iniciando correção do erro de indentação no arquivo admin_ui.py")
    
    # Caminho para o arquivo admin_ui.py
    ui_file = "ui/admin_ui.py"
    
    # Corrigir o arquivo
    if fix_indentation(ui_file):
        logger.info("Correção concluída com sucesso!")
        return 0
    else:
        logger.error("Falha ao corrigir o arquivo.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 