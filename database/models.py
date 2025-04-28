"""
Módulo contendo os modelos de dados do sistema.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from database.connection import DatabaseConnection

@dataclass
class Usuario:
    """Modelo de dados para usuários do sistema."""
    id: int
    nome: str
    email: str
    senha_hash: str
    tipo_acesso: str  # 'admin' ou 'cliente'
    empresa: Optional[str] = None
    ativo: bool = True

@dataclass
class Equipamento:
    """Modelo de dados para equipamentos sujeitos à NR-13."""
    id: int
    tipo: str  # 'caldeira', 'vaso_pressao', 'tubulacao'
    empresa: str
    localizacao: str
    codigo_projeto: str
    pressao_maxima: float
    temperatura_maxima: float
    data_ultima_inspecao: Optional[datetime] = None
    data_proxima_inspecao: Optional[datetime] = None
    status: str = 'ativo'  # 'ativo', 'inativo', 'manutencao'

@dataclass
class Inspecao:
    """Modelo de dados para inspeções técnicas."""
    id: int
    equipamento_id: int
    data_inspecao: datetime
    tipo_inspecao: str  # 'periodica', 'extraordinaria'
    engenheiro_responsavel: str
    resultado: str  # 'aprovado', 'reprovado', 'condicional'
    recomendacoes: Optional[str] = None
    proxima_inspecao: Optional[datetime] = None

@dataclass
class Relatorio:
    """Modelo de dados para relatórios técnicos."""
    id: int
    inspecao_id: int
    data_emissao: datetime
    link_arquivo: str
    observacoes: Optional[str] = None

class DatabaseModels:
    """Classe responsável por operações CRUD no banco de dados."""
    
    def __init__(self):
        self.db = DatabaseConnection()
        
    def criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela de usuários
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    tipo_acesso VARCHAR(20) NOT NULL,
                    empresa VARCHAR(100),
                    ativo BIT DEFAULT 1
                )
            """)
            
            # Tabela de equipamentos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'equipamentos')
                CREATE TABLE equipamentos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    tipo VARCHAR(20) NOT NULL,
                    empresa VARCHAR(100) NOT NULL,
                    localizacao VARCHAR(200) NOT NULL,
                    codigo_projeto VARCHAR(50) NOT NULL,
                    pressao_maxima FLOAT NOT NULL,
                    temperatura_maxima FLOAT NOT NULL,
                    data_ultima_inspecao DATETIME,
                    data_proxima_inspecao DATETIME,
                    status VARCHAR(20) DEFAULT 'ativo'
                )
            """)
            
            # Tabela de inspeções
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inspecoes')
                CREATE TABLE inspecoes (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    equipamento_id INT NOT NULL,
                    data_inspecao DATETIME NOT NULL,
                    tipo_inspecao VARCHAR(20) NOT NULL,
                    engenheiro_responsavel VARCHAR(100) NOT NULL,
                    resultado VARCHAR(20) NOT NULL,
                    recomendacoes TEXT,
                    proxima_inspecao DATETIME,
                    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
                )
            """)
            
            # Tabela de relatórios
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'relatorios')
                CREATE TABLE relatorios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    inspecao_id INT NOT NULL,
                    data_emissao DATETIME NOT NULL,
                    link_arquivo VARCHAR(255) NOT NULL,
                    observacoes TEXT,
                    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
                )
            """)
            
            conn.commit()
            logger.info("Tabelas criadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            raise
        finally:
            cursor.close() 