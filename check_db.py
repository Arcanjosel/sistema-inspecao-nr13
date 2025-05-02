import pyodbc
import logging
from datetime import datetime

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("check_db")

def conectar_sql_server():
    """Estabelece conexão com o banco de dados SQL Server."""
    try:
        # Conexão com o SQL Server
        conn_str = 'DRIVER={SQL Server};SERVER=DESKTOP-GUFFT6G\\MSSQLSERVER01;DATABASE=sistema_inspecao_db;Trusted_Connection=yes;'
        logger.info(f"Tentando conectar ao SQL Server com: {conn_str}")
        conn = pyodbc.connect(conn_str)
        logger.info("Conexão estabelecida com sucesso!")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao SQL Server: {str(e)}")
        return None

def verificar_tabela_equipamentos(conn):
    """Verifica a estrutura da tabela equipamentos."""
    try:
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'equipamentos'")
        result = cursor.fetchone()
        
        if result[0] == 0:
            logger.error("A tabela 'equipamentos' não existe!")
            return False
            
        # Lista as colunas da tabela
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'equipamentos'")
        colunas = cursor.fetchall()
        
        logger.info("Colunas na tabela 'equipamentos':")
        for col in colunas:
            logger.info(f"  - {col.COLUMN_NAME} ({col.DATA_TYPE})")
            
        # Colunas esperadas
        colunas_esperadas = {
            'id': 'int',
            'tag': 'nvarchar',
            'categoria': 'nvarchar',
            'empresa_id': 'int',
            'fabricante': 'nvarchar',
            'ano_fabricacao': 'int',
            'pressao_projeto': 'float',
            'pressao_trabalho': 'float',
            'volume': 'float',
            'fluido': 'nvarchar',
            'ativo': 'bit'
        }
        
        # Verificar colunas faltantes
        colunas_faltantes = []
        for coluna, tipo in colunas_esperadas.items():
            if not any(col.COLUMN_NAME.lower() == coluna.lower() for col in colunas):
                colunas_faltantes.append((coluna, tipo))
                
        if colunas_faltantes:
            logger.warning("Colunas faltantes na tabela 'equipamentos':")
            for col, tipo in colunas_faltantes:
                logger.warning(f"  - {col} ({tipo})")
                
        # Verifica se a coluna status existe com outro nome
        status_columns = [col.COLUMN_NAME for col in colunas if col.COLUMN_NAME.lower() in ('status', 'situacao', 'estado')]
        if status_columns:
            logger.info(f"Coluna de status encontrada com nome: {status_columns[0]}")
        
        # Contar registros na tabela
        cursor.execute("SELECT COUNT(*) FROM equipamentos")
        count = cursor.fetchone()[0]
        logger.info(f"A tabela contém {count} registros")
        
        # Verificar primeiro registro (se existir)
        if count > 0:
            cursor.execute("SELECT TOP 1 * FROM equipamentos")
            row = cursor.fetchone()
            
            logger.info("Primeiro registro:")
            for i in range(len(cursor.description)):
                logger.info(f"  {cursor.description[i][0]}: {row[i]}")
                
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar tabela equipamentos: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()

def corrigir_tabela_equipamentos(conn):
    """Corrige a estrutura da tabela equipamentos se necessário."""
    try:
        cursor = conn.cursor()
        
        # Verifica se a coluna 'ativo' existe
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'ativo'")
        if cursor.fetchone()[0] == 0:
            logger.info("Adicionando coluna 'ativo' à tabela 'equipamentos'")
            cursor.execute("ALTER TABLE equipamentos ADD ativo BIT DEFAULT 1")
            conn.commit()
            logger.info("Coluna 'ativo' adicionada com sucesso!")
            
        # Verifica se a coluna 'status' existe
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'status'")
        if cursor.fetchone()[0] > 0:
            # Verifica se a coluna 'ativo' precisa ser preenchida baseada no 'status'
            logger.info("Atualizando coluna 'ativo' baseado no valor de 'status'")
            cursor.execute("UPDATE equipamentos SET ativo = 1 WHERE status = 'ativo' AND (ativo IS NULL OR ativo = 0)")
            cursor.execute("UPDATE equipamentos SET ativo = 0 WHERE status != 'ativo' AND (ativo IS NULL OR ativo = 1)")
            conn.commit()
            
            count_updated = cursor.rowcount
            logger.info(f"Atualizados {count_updated} registros")
            
        return True
            
    except Exception as e:
        logger.error(f"Erro ao corrigir tabela equipamentos: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()

def main():
    """Função principal"""
    logger.info("Iniciando verificação do banco de dados")
    
    # Conectar ao SQL Server
    conn = conectar_sql_server()
    if not conn:
        logger.error("Não foi possível estabelecer conexão com o banco de dados.")
        return
        
    try:
        # Verificar estrutura da tabela
        if verificar_tabela_equipamentos(conn):
            # Corrigir se necessário
            corrigir_tabela_equipamentos(conn)
            
        logger.info("Verificação concluída!")
        
    finally:
        conn.close()
        logger.info("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main() 