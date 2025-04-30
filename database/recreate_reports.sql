USE sistema_inspecao_db;
GO

-- Primeiro remove os índices se existirem
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_data' AND object_id = OBJECT_ID('relatorios'))
    DROP INDEX IX_relatorios_data ON relatorios;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_inspecao' AND object_id = OBJECT_ID('relatorios'))
    DROP INDEX IX_relatorios_tipo_inspecao ON relatorios;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_resultado' AND object_id = OBJECT_ID('relatorios'))
    DROP INDEX IX_relatorios_resultado ON relatorios;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_equipamento' AND object_id = OBJECT_ID('relatorios'))
    DROP INDEX IX_relatorios_tipo_equipamento ON relatorios;
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_engenheiro' AND object_id = OBJECT_ID('relatorios'))
    DROP INDEX IX_relatorios_engenheiro ON relatorios;
GO

-- Remove a tabela se existir
IF OBJECT_ID('relatorios', 'U') IS NOT NULL
    DROP TABLE relatorios;
GO

-- Cria a tabela com todas as colunas necessárias
CREATE TABLE relatorios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    inspecao_id INT NOT NULL,
    data_emissao DATETIME NOT NULL,
    link_arquivo VARCHAR(255) NOT NULL,
    tipo_inspecao VARCHAR(50) NULL,
    resultado_inspecao VARCHAR(50) NULL,
    tipo_equipamento VARCHAR(50) NULL,
    nome_engenheiro VARCHAR(100) NULL,
    observacoes TEXT NULL,
    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
);
GO

-- Cria os índices
CREATE INDEX IX_relatorios_data ON relatorios(data_emissao);
CREATE INDEX IX_relatorios_tipo_inspecao ON relatorios(tipo_inspecao) WHERE tipo_inspecao IS NOT NULL;
CREATE INDEX IX_relatorios_resultado ON relatorios(resultado_inspecao) WHERE resultado_inspecao IS NOT NULL;
CREATE INDEX IX_relatorios_tipo_equipamento ON relatorios(tipo_equipamento) WHERE tipo_equipamento IS NOT NULL;
CREATE INDEX IX_relatorios_engenheiro ON relatorios(nome_engenheiro) WHERE nome_engenheiro IS NOT NULL;
GO

-- Popula a tabela com dados das inspeções existentes
INSERT INTO relatorios (
    inspecao_id,
    data_emissao,
    link_arquivo,
    tipo_inspecao,
    resultado_inspecao,
    tipo_equipamento,
    nome_engenheiro,
    observacoes
)
SELECT 
    i.id,
    i.data_inspecao,
    'arquivo_' + CAST(i.id as VARCHAR) + '.pdf',
    i.tipo_inspecao,
    i.resultado,
    e.tag,
    u.nome,
    i.recomendacoes
FROM inspecoes i
JOIN equipamentos e ON i.equipamento_id = e.id
JOIN usuarios u ON i.engenheiro_id = u.id;
GO 