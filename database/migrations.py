#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migrações para atualizar o banco de dados
"""

from database.connection import DatabaseConnection
import logging
import traceback

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def adicionar_campo_crea():
    """Adiciona o campo CREA à tabela de usuários se não existir"""
    logger.info("Verificando se é necessário adicionar o campo CREA à tabela de usuários")
    
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se a tabela existe
        cursor.execute("""
            IF EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
            SELECT 1 ELSE SELECT 0
        """)
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            logger.info("Tabela usuários não existe, nada a fazer")
            return
            
        # Verifica se o campo já existe
        cursor.execute("""
            IF COL_LENGTH('usuarios', 'crea') IS NOT NULL
            SELECT 1 ELSE SELECT 0
        """)
        campo_existe = cursor.fetchone()[0]
        
        if campo_existe:
            logger.info("Campo CREA já existe na tabela usuários")
            return
            
        # Adiciona o campo
        logger.info("Adicionando campo CREA à tabela usuários")
        cursor.execute("""
            ALTER TABLE usuarios
            ADD crea VARCHAR(50) NULL
        """)
        
        conn.commit()
        logger.info("Campo CREA adicionado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar campo CREA: {str(e)}")
        logger.error(traceback.format_exc())
        conn.rollback()
        raise
    finally:
        cursor.close()

def executar_migracoes():
    """Executa todas as migrações pendentes"""
    try:
        logger.info("Iniciando migrações do banco de dados")
        
        # Adicionar campo CREA
        adicionar_campo_crea()
        
        logger.info("Migrações concluídas com sucesso")
    except Exception as e:
        logger.error(f"Erro durante as migrações: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    executar_migracoes() 