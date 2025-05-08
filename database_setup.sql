-- Script de instalação do banco de dados para o Sistema de Gerenciamento de Inspeções NR-13
-- Este script cria o banco de dados, tabelas e um usuário administrador inicial

-- Criação do banco de dados
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'sistema_inspecao_db')
BEGIN
    CREATE DATABASE sistema_inspecao_db;
END
GO

USE sistema_inspecao_db;
GO

-- Criação da tabela de usuários com suporte para engenheiros (campo CREA)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_acesso VARCHAR(20) NOT NULL,
    empresa VARCHAR(100),
    ativo BIT DEFAULT 1,
    crea VARCHAR(50)  -- Campo para armazenar o número do CREA de engenheiros
);
GO

-- Criação da tabela de equipamentos
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'equipamentos')
CREATE TABLE equipamentos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    categoria VARCHAR(50),
    tag VARCHAR(20),
    empresa VARCHAR(100) NOT NULL,
    localizacao VARCHAR(200) NOT NULL,
    codigo_projeto VARCHAR(50) NOT NULL,
    pressao_maxima FLOAT NOT NULL,
    temperatura_maxima FLOAT NOT NULL,
    fabricante VARCHAR(100),
    ano_fabricacao INT,
    pressao_projeto FLOAT,
    pressao_trabalho FLOAT,
    volume FLOAT,
    fluido VARCHAR(50),
    categoria_nr13 VARCHAR(20),
    pmta VARCHAR(50),
    placa_identificacao VARCHAR(50),
    numero_registro VARCHAR(50),
    data_ultima_inspecao DATETIME,
    data_proxima_inspecao DATETIME,
    status VARCHAR(20) DEFAULT 'ativo'
);
GO

-- Criação da tabela de inspeções com referência a engenheiros
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
    engenheiro_id INT,
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
    FOREIGN KEY (engenheiro_id) REFERENCES usuarios(id)
);
GO

-- Criação da tabela de relatórios
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'relatorios')
CREATE TABLE relatorios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    inspecao_id INT NOT NULL,
    data_emissao DATE NOT NULL,
    link_arquivo VARCHAR(255) NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
);
GO

-- Inserção de um usuário administrador padrão
-- Email: admin@empresa.com
-- Senha: admin123 (hash bcrypt)
IF NOT EXISTS (SELECT * FROM usuarios WHERE email = 'admin@empresa.com')
BEGIN
    -- Hash bcrypt da senha 'admin123'
    INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, ativo)
    VALUES ('Administrador', 'admin@empresa.com', '$2b$12$5SxQH.i5zMZM3xN9qIbTueT.pYfUT2hBNCIyjTuLYK9rEJEWKlhX.', 'admin', 1);
    
    PRINT 'Usuário administrador criado com sucesso!';
    PRINT 'Email: admin@empresa.com';
    PRINT 'Senha: admin123';
END
ELSE
BEGIN
    PRINT 'Usuário administrador já existe.';
END
GO

-- Índices para melhorar o desempenho das consultas
CREATE INDEX IF NOT EXISTS idx_equipamentos_empresa ON equipamentos(empresa);
CREATE INDEX IF NOT EXISTS idx_inspecoes_equipamento ON inspecoes(equipamento_id);
CREATE INDEX IF NOT EXISTS idx_inspecoes_data ON inspecoes(data_inspecao);
CREATE INDEX IF NOT EXISTS idx_relatorios_inspecao ON relatorios(inspecao_id);
GO

PRINT 'Script de instalação concluído com sucesso!'
GO 