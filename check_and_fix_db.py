import pyodbc
import logging
import traceback
from database.connection import DatabaseConnection
import sys

# Configuração básica do logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_and_fix_database():
    """Verifica e corrige problemas no banco de dados."""
    try:
        # Obtém a conexão com o banco de dados
        connection = DatabaseConnection()
        conn = connection.get_connection()
        
        if conn is None:
            logger.error("Não foi possível conectar ao banco de dados")
            return
            
        cursor = conn.cursor()
        
        # Verificar se a coluna 'ativo' existe na tabela 'equipamentos'
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'ativo'
        """)
        
        if cursor.fetchone()[0] == 0:
            logger.info("Coluna 'ativo' não encontrada na tabela 'equipamentos'. Adicionando...")
            cursor.execute("ALTER TABLE equipamentos ADD ativo BIT DEFAULT 1")
        
        # Verificar se os campos NR-13 existem na tabela 'equipamentos'
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'categoria_nr13'
        """)
        
        if cursor.fetchone()[0] == 0:
            logger.info("Campos NR-13 não encontrados na tabela 'equipamentos'. Adicionando...")
            # Adicionar campos NR-13 com VARCHAR(100) para evitar truncamento
            cursor.execute("ALTER TABLE equipamentos ADD categoria_nr13 VARCHAR(100)")
            cursor.execute("ALTER TABLE equipamentos ADD pmta VARCHAR(100)")
            cursor.execute("ALTER TABLE equipamentos ADD placa_identificacao VARCHAR(100)")
            cursor.execute("ALTER TABLE equipamentos ADD numero_registro VARCHAR(100)")
        else:
            # Verificar o tamanho atual das colunas e aumentar se necessário
            cursor.execute("""
                SELECT CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'categoria_nr13'
            """)
            current_length = cursor.fetchone()[0]
            
            if current_length < 100:
                logger.info(f"Aumentando o tamanho das colunas NR-13 de {current_length} para 100...")
                cursor.execute("ALTER TABLE equipamentos ALTER COLUMN categoria_nr13 VARCHAR(100)")
                cursor.execute("ALTER TABLE equipamentos ALTER COLUMN pmta VARCHAR(100)")
                cursor.execute("ALTER TABLE equipamentos ALTER COLUMN placa_identificacao VARCHAR(100)")
                cursor.execute("ALTER TABLE equipamentos ALTER COLUMN numero_registro VARCHAR(100)")
        
        # Comitar as alterações
        conn.commit()
        logger.info("Verificação e correção do banco de dados concluídas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao verificar e corrigir o banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("Iniciando verificação e correção do banco de dados...")
    check_and_fix_database()
    logger.info("Processo concluído.")
    sys.exit(0) 