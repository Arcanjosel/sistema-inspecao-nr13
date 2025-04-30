-- Criação do banco de dados
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'sistema_inspecao_db')
BEGIN
    CREATE DATABASE sistema_inspecao_db;
END
GO

USE sistema_inspecao_db;
GO

-- Tabela de usuários
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_acesso VARCHAR(20) NOT NULL,
    empresa VARCHAR(100),
    ativo BIT DEFAULT 1
);
GO

-- Tabela de equipamentos
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
);
GO

-- Tabela de inspeções
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

-- Tabela de relatórios
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'relatorios')
CREATE TABLE relatorios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    inspecao_id INT NOT NULL,
    data_emissao DATETIME NOT NULL,
    link_arquivo VARCHAR(255) NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
);
GO

-- Inserir usuário admin inicial (senha: admin123)
IF NOT EXISTS (SELECT * FROM usuarios WHERE email = 'admin@sistema.com')
BEGIN
    INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso)
    VALUES ('Administrador', 'admin@sistema.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewqhrPtk.6.CS1.e', 'admin');
END
GO 