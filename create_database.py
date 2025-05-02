#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criação das tabelas do banco de dados do sistema.
Este script cria todas as tabelas necessárias e seus relacionamentos.
"""

import os
import sys
import logging
import pyodbc
import datetime
import hashlib
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("database_setup")

# Configurações do banco de dados
DB_SERVER = "localhost\\SQLEXPRESS"
DB_NAME = "nr13_sistema"
DB_TRUSTED_CONNECTION = "yes"

def conectar_bd():
    """Estabelece uma conexão com o banco de dados SQL Server."""
    try:
        connection_string = f"Driver={{SQL Server}};Server={DB_SERVER};Database={DB_NAME};Trusted_Connection={DB_TRUSTED_CONNECTION};"
        conn = pyodbc.connect(connection_string)
        logger.info(f"Conexão estabelecida com o banco de dados {DB_NAME}")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None

def executar_query(conn, query, params=None):
    """Executa uma query SQL no banco de dados."""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erro ao executar query: {str(e)}")
        logger.error(f"Query: {query}")
        logger.error(traceback.format_exc())
        return False

def criar_tabela_usuarios(conn):
    """Cria a tabela de usuários."""
    query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL,
        tipo VARCHAR(20) NOT NULL DEFAULT 'cliente',  -- 'admin', 'cliente', 'emp'
        empresa VARCHAR(100),
        empresa_id INT,
        ativo BIT DEFAULT 1,
        criado_em DATETIME DEFAULT GETDATE()
    );
    """
    
    if executar_query(conn, query):
        logger.info("Tabela 'usuarios' criada ou já existente")
        return True
    return False

def criar_tabela_equipamentos(conn):
    """Cria a tabela de equipamentos."""
    query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='equipamentos' AND xtype='U')
    CREATE TABLE equipamentos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        tag VARCHAR(50) NOT NULL,
        categoria VARCHAR(50) NOT NULL,
        empresa_id INT NOT NULL,
        fabricante VARCHAR(100),
        ano_fabricacao INT,
        pressao_projeto FLOAT,
        pressao_trabalho FLOAT,
        volume FLOAT,
        fluido VARCHAR(100),
        frequencia_manutencao INT DEFAULT 180,
        data_ultima_manutencao DATE,
        ativo BIT DEFAULT 1,
        criado_em DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (empresa_id) REFERENCES usuarios(id)
    );
    """
    
    if executar_query(conn, query):
        logger.info("Tabela 'equipamentos' criada ou já existente")
        return True
    return False

def criar_tabela_inspecoes(conn):
    """Cria a tabela de inspeções."""
    query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='inspecoes' AND xtype='U')
    CREATE TABLE inspecoes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        tipo VARCHAR(50) NOT NULL,
        equipamento_id INT NOT NULL,
        data_realizacao DATE NOT NULL,
        data_proxima DATE NOT NULL,
        resultado VARCHAR(50) NOT NULL,
        recomendacoes VARCHAR(500),
        empresa_id INT NOT NULL,
        criado_em DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
        FOREIGN KEY (empresa_id) REFERENCES usuarios(id)
    );
    """
    
    if executar_query(conn, query):
        logger.info("Tabela 'inspecoes' criada ou já existente")
        return True
    return False

def criar_tabela_relatorios(conn):
    """Cria a tabela de relatórios."""
    query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='relatorios' AND xtype='U')
    CREATE TABLE relatorios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        inspecao_id INT NOT NULL,
        numero VARCHAR(50) NOT NULL,
        data_emissao DATE NOT NULL,
        observacoes VARCHAR(500),
        empresa_id INT NOT NULL,
        criado_em DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id),
        FOREIGN KEY (empresa_id) REFERENCES usuarios(id)
    );
    """
    
    if executar_query(conn, query):
        logger.info("Tabela 'relatorios' criada ou já existente")
        return True
    return False

def criar_usuario_admin(conn):
    """Cria o usuário administrador padrão."""
    # Verificar se o usuário admin já existe
    check_query = "SELECT COUNT(*) FROM usuarios WHERE email = ?"
    cursor = conn.cursor()
    cursor.execute(check_query, ["admin@empresa.com"])
    count = cursor.fetchone()[0]
    
    if count > 0:
        logger.info("Usuário admin já existe")
        return True
    
    # Senha criptografada (admin123)
    senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
    
    insert_query = """
    INSERT INTO usuarios (nome, email, senha, tipo, empresa, ativo)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    
    params = ["Administrador", "admin@empresa.com", senha_hash, "admin", "Administração", 1]
    
    if executar_query(conn, insert_query, params):
        logger.info("Usuário admin criado com sucesso")
        return True
    return False

def popular_dados_exemplo(conn):
    """Popula o banco de dados com alguns dados de exemplo."""
    # Criar empresas (usuários tipo cliente)
    empresas = [
        ["Petrobras S.A.", "petrobras@cliente.com", "Petrobras", "cliente"],
        ["Vale S.A.", "vale@cliente.com", "Vale", "cliente"],
        ["Braskem", "braskem@cliente.com", "Braskem", "cliente"]
    ]
    
    empresa_ids = []
    
    for empresa in empresas:
        try:
            # Verificar se a empresa já existe
            check_query = "SELECT id FROM usuarios WHERE email = ?"
            cursor = conn.cursor()
            cursor.execute(check_query, [empresa[1]])
            result = cursor.fetchone()
            
            if result:
                empresa_ids.append(result[0])
                logger.info(f"Empresa {empresa[0]} já existe, ID: {result[0]}")
                continue
            
            # Senha criptografada (senha123)
            senha_hash = hashlib.sha256("senha123".encode()).hexdigest()
            
            insert_query = """
            INSERT INTO usuarios (nome, email, senha, tipo, empresa, ativo)
            VALUES (?, ?, ?, ?, ?, ?);
            SELECT SCOPE_IDENTITY();
            """
            
            params = [empresa[0], empresa[1], senha_hash, empresa[3], empresa[2], 1]
            
            cursor = conn.cursor()
            cursor.execute(insert_query, params)
            novo_id = cursor.fetchone()[0]
            conn.commit()
            
            empresa_ids.append(novo_id)
            logger.info(f"Empresa {empresa[0]} criada com ID: {novo_id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar empresa {empresa[0]}: {str(e)}")
    
    # Adicionar alguns equipamentos para cada empresa
    if empresa_ids:
        equipamentos = [
            # Para a primeira empresa
            ["V-1001", "Vaso de Pressão", fabricante, 2015, 15.5, 14.2, 10000, "Hidrocarboneto"] 
            for fabricante in ["Confab", "CBC", "Bardella"]
        ] + [
            # Para a segunda empresa
            ["P-2001", "Tubulação", fabricante, 2018, 25.0, 22.5, 0, "Água"] 
            for fabricante in ["Tenaris", "Vallourec", "V&M"]
        ] + [
            # Para a terceira empresa
            ["C-3001", "Caldeira", fabricante, 2020, 40.0, 35.0, 5000, "Vapor"] 
            for fabricante in ["Mitsubishi", "CBC", "Alstom"]
        ]
        
        equipamento_ids = []
        
        # Distribuir equipamentos pelas empresas
        for i, equip in enumerate(equipamentos):
            empresa_idx = min(i // 3, len(empresa_ids) - 1)  # Distribui 3 equipamentos por empresa
            empresa_id = empresa_ids[empresa_idx]
            
            try:
                # Verificar se o equipamento já existe
                check_query = "SELECT id FROM equipamentos WHERE tag = ? AND empresa_id = ?"
                cursor = conn.cursor()
                cursor.execute(check_query, [equip[0], empresa_id])
                result = cursor.fetchone()
                
                if result:
                    equipamento_ids.append(result[0])
                    logger.info(f"Equipamento {equip[0]} já existe, ID: {result[0]}")
                    continue
                
                insert_query = """
                INSERT INTO equipamentos (tag, categoria, empresa_id, fabricante, ano_fabricacao, pressao_projeto, pressao_trabalho, volume, fluido, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                SELECT SCOPE_IDENTITY();
                """
                
                params = [equip[0], equip[1], empresa_id, equip[2], equip[3], equip[4], equip[5], equip[6], equip[7], 1]
                
                cursor = conn.cursor()
                cursor.execute(insert_query, params)
                novo_id = cursor.fetchone()[0]
                conn.commit()
                
                equipamento_ids.append(novo_id)
                logger.info(f"Equipamento {equip[0]} criado com ID: {novo_id}")
                
            except Exception as e:
                logger.error(f"Erro ao criar equipamento {equip[0]}: {str(e)}")
        
        # Adicionar inspeções para cada equipamento
        if equipamento_ids:
            inspecoes = []
            hoje = datetime.date.today()
            
            # Criar algumas inspeções para cada equipamento
            for i, equip_id in enumerate(equipamento_ids):
                empresa_idx = min(i // 3, len(empresa_ids) - 1)
                empresa_id = empresa_ids[empresa_idx]
                
                # Inspeção periódica (1 ano atrás)
                data_insp = hoje - datetime.timedelta(days=365)
                data_prox = hoje + datetime.timedelta(days=365)
                inspecoes.append(["Periódica", equip_id, data_insp, data_prox, "Aprovado", "Sem recomendações específicas", empresa_id])
                
                # Inspeção extraordinária (6 meses atrás)
                data_insp = hoje - datetime.timedelta(days=180)
                data_prox = hoje + datetime.timedelta(days=550)
                inspecoes.append(["Extraordinária", equip_id, data_insp, data_prox, "Aprovado com Restrições", "Realizar manutenção preventiva no prazo de 3 meses", empresa_id])
            
            inspecao_ids = []
            
            for insp in inspecoes:
                try:
                    insert_query = """
                    INSERT INTO inspecoes (tipo, equipamento_id, data_realizacao, data_proxima, resultado, recomendacoes, empresa_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    SELECT SCOPE_IDENTITY();
                    """
                    
                    cursor = conn.cursor()
                    cursor.execute(insert_query, insp)
                    novo_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    inspecao_ids.append(novo_id)
                    logger.info(f"Inspeção tipo {insp[0]} criada com ID: {novo_id}")
                    
                except Exception as e:
                    logger.error(f"Erro ao criar inspeção: {str(e)}")
            
            # Adicionar relatórios para cada inspeção
            if inspecao_ids:
                relatorios = []
                
                for i, insp_id in enumerate(inspecao_ids):
                    empresa_idx = min((i // 6), len(empresa_ids) - 1)  # 6 = 2 inspeções x 3 equipamentos por empresa
                    empresa_id = empresa_ids[empresa_idx]
                    
                    # Data de emissão (1 dia após a inspeção)
                    data_insp = inspecoes[i][2]
                    data_emissao = data_insp + datetime.timedelta(days=1)
                    
                    numero = f"REL-{data_insp.year}-{insp_id:04d}"
                    relatorios.append([insp_id, numero, data_emissao, f"Relatório de inspeção {inspecoes[i][0]} realizada em {data_insp.strftime('%d/%m/%Y')}", empresa_id])
                
                for rel in relatorios:
                    try:
                        insert_query = """
                        INSERT INTO relatorios (inspecao_id, numero, data_emissao, observacoes, empresa_id)
                        VALUES (?, ?, ?, ?, ?);
                        """
                        
                        cursor = conn.cursor()
                        cursor.execute(insert_query, rel)
                        conn.commit()
                        
                        logger.info(f"Relatório {rel[1]} criado com sucesso")
                        
                    except Exception as e:
                        logger.error(f"Erro ao criar relatório: {str(e)}")
    
    return True

def main():
    """Função principal do script."""
    logger.info("Iniciando configuração do banco de dados")
    
    # Conectar ao banco de dados
    conn = conectar_bd()
    if not conn:
        logger.error("Falha ao conectar ao banco de dados. Verifique as configurações e tente novamente.")
        return False
    
    try:
        # Criar tabelas
        if not criar_tabela_usuarios(conn):
            logger.error("Falha ao criar tabela de usuários")
            return False
        
        if not criar_tabela_equipamentos(conn):
            logger.error("Falha ao criar tabela de equipamentos")
            return False
        
        if not criar_tabela_inspecoes(conn):
            logger.error("Falha ao criar tabela de inspeções")
            return False
        
        if not criar_tabela_relatorios(conn):
            logger.error("Falha ao criar tabela de relatórios")
            return False
        
        # Criar usuário admin
        if not criar_usuario_admin(conn):
            logger.warning("Não foi possível criar o usuário admin")
        
        # Popular com dados de exemplo
        pergunta = input("Deseja popular o banco de dados com dados de exemplo? (s/n): ")
        if pergunta.lower() in ['s', 'sim', 'y', 'yes']:
            if not popular_dados_exemplo(conn):
                logger.warning("Não foi possível popular o banco de dados com dados de exemplo")
        
        logger.info("Configuração do banco de dados concluída com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro na configuração do banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        resultado = main()
        if resultado:
            logger.info("Script executado com sucesso!")
            logger.info("Credenciais do administrador: email=admin@empresa.com, senha=admin123")
            sys.exit(0)
        else:
            logger.error("Falha na execução do script!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        sys.exit(2)
    except Exception as e:
        logger.critical(f"Erro não tratado: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(3) 