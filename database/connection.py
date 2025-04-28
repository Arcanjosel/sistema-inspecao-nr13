"""
Módulo responsável pela conexão com o banco de dados SQL Server.
"""
import os
import pyodbc
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Classe responsável por gerenciar a conexão com o banco de dados.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa a conexão com o banco de dados."""
        try:
            load_dotenv()
            
            server = os.getenv('DB_SERVER')
            database = os.getenv('DB_NAME')
            username = os.getenv('DB_USERNAME')
            password = os.getenv('DB_PASSWORD')
            trusted_connection = os.getenv('DB_TRUSTED_CONNECTION', 'False').lower() == 'true'
            
            if trusted_connection:
                self.connection_string = (
                    f"DRIVER={{SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                self.connection_string = (
                    f"DRIVER={{SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password}"
                )
            
            logger.info(f"Tentando conectar ao banco de dados: {server}/{database}")
            self.conn = pyodbc.connect(self.connection_string)
            logger.info("Conexão com o banco de dados estabelecida com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            raise

    def get_connection(self):
        """Retorna a conexão com o banco de dados."""
        return self.conn

    def close_connection(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco de dados fechada") 