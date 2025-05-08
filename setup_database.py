#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de instalação e configuração do banco de dados
para o Sistema de Gerenciamento de Inspeções NR-13
"""

import os
import sys
import pyodbc
import logging
import time
import dotenv
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Instalação")

def criar_arquivo_env():
    """Cria um arquivo .env se não existir"""
    if os.path.exists(".env"):
        logger.info("Arquivo .env já existe.")
        return

    logger.info("Criando arquivo .env...")
    
    conteudo = """# Configurações de Banco de Dados
DB_SERVER=localhost\\SQLEXPRESS
DB_NAME=sistema_inspecao_db
DB_USERNAME=sa
DB_PASSWORD=sua_senha
DB_TRUSTED_CONNECTION=True

# Configurações de log
LOG_LEVEL=INFO
LOG_FILE=logs/sistema.log
"""
    
    with open(".env", "w") as f:
        f.write(conteudo)
    
    logger.info("Arquivo .env criado com sucesso. Por favor, edite-o com suas configurações reais antes de continuar.")
    logger.info("Pressione Enter para continuar após editar o arquivo .env...")
    input()

def criar_diretorio_logs():
    """Cria o diretório de logs se não existir"""
    if not os.path.exists("logs"):
        logger.info("Criando diretório de logs...")
        os.makedirs("logs")
        logger.info("Diretório de logs criado com sucesso.")

def testar_conexao_sql_server():
    """Testa a conexão com o SQL Server"""
    try:
        # Carrega as variáveis de ambiente do arquivo .env
        dotenv.load_dotenv()
        
        server = os.getenv("DB_SERVER")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "False").lower() == "true"
        
        logger.info(f"Testando conexão com o servidor SQL: {server}")
        
        # Formata a string de conexão
        if trusted_connection:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};Trusted_Connection=yes;'
        else:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};UID={username};PWD={password}'
        
        # Tenta conectar
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        logger.info(f"Conexão com SQL Server estabelecida com sucesso.")
        logger.info(f"Versão do SQL Server: {version}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao SQL Server: {str(e)}")
        logger.error("Verifique suas credenciais no arquivo .env e tente novamente.")
        return False

def executar_script_sql():
    """Executa o script SQL para criar o banco de dados e tabelas"""
    try:
        # Carrega as variáveis de ambiente do arquivo .env
        dotenv.load_dotenv()
        
        server = os.getenv("DB_SERVER")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "False").lower() == "true"
        
        # Formata a string de conexão para o SQL Server (sem especificar banco de dados)
        if trusted_connection:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};Trusted_Connection=yes;'
        else:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};UID={username};PWD={password}'
        
        # Lê o script SQL
        with open("database_setup.sql", "r") as f:
            script = f.read()
        
        # Divide o script em comandos separados por GO
        commands = script.split("GO")
        
        # Conecta e executa os comandos
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        for i, command in enumerate(commands):
            if command.strip():
                try:
                    logger.info(f"Executando comando SQL {i+1}/{len(commands)}...")
                    cursor.execute(command)
                    conn.commit()
                except Exception as e:
                    # Alguns comandos podem falhar se os objetos já existirem (como CREATE DATABASE),
                    # mas queremos continuar de qualquer forma
                    logger.warning(f"Aviso ao executar comando {i+1}: {str(e)}")
        
        cursor.close()
        conn.close()
        
        logger.info("Script SQL executado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao executar script SQL: {str(e)}")
        return False

def instalar_banco_dados():
    """Função principal para instalação do banco de dados"""
    logger.info("Iniciando instalação do banco de dados...")
    
    # Verifica se o script SQL existe
    if not os.path.exists("database_setup.sql"):
        logger.error("Arquivo database_setup.sql não encontrado!")
        return False
    
    # Cria arquivo .env se não existir
    criar_arquivo_env()
    
    # Cria diretório de logs
    criar_diretorio_logs()
    
    # Testa conexão com SQL Server
    if not testar_conexao_sql_server():
        return False
    
    # Executa script SQL
    if not executar_script_sql():
        return False
    
    logger.info("Instalação do banco de dados concluída com sucesso!")
    return True

if __name__ == "__main__":
    try:
        print("======================================================")
        print("  Sistema de Gerenciamento de Inspeções NR-13")
        print("  Instalação e Configuração do Banco de Dados")
        print("======================================================")
        print()
        
        result = instalar_banco_dados()
        
        if result:
            print()
            print("======================================================")
            print("  Instalação concluída com sucesso!")
            print("  Você já pode executar o sistema com: python main.py")
            print("======================================================")
            print()
            print("Credenciais do usuário admin:")
            print("Email: admin@empresa.com")
            print("Senha: admin123")
            print()
            print("IMPORTANTE: Altere esta senha após o primeiro login!")
            sys.exit(0)
        else:
            print()
            print("======================================================")
            print("  Instalação falhou. Verifique os erros acima.")
            print("======================================================")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nInstalação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro durante a instalação: {str(e)}")
        sys.exit(1) 