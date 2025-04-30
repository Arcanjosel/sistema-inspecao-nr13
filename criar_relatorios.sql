USE sistema_inspecao_db;
GO

-- Dropando índices existentes
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_data' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    DROP INDEX IX_relatorios_data ON relatorios;
END
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_inspecao' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    DROP INDEX IX_relatorios_tipo_inspecao ON relatorios;
END
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_resultado' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    DROP INDEX IX_relatorios_resultado ON relatorios;
END
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_equipamento' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    DROP INDEX IX_relatorios_tipo_equipamento ON relatorios;
END
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_engenheiro' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    DROP INDEX IX_relatorios_engenheiro ON relatorios;
END
GO

-- Dropando a tabela se ela existir
IF OBJECT_ID('relatorios', 'U') IS NOT NULL
BEGIN
    DROP TABLE relatorios;
END
GO

-- Criando a tabela relatorios com todas as colunas necessárias
CREATE TABLE relatorios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    inspecao_id INT NOT NULL,
    data_emissao DATETIME NOT NULL,
    link_arquivo VARCHAR(255) NOT NULL,
    tipo_inspecao VARCHAR(50),
    resultado_inspecao VARCHAR(50),
    tipo_equipamento VARCHAR(50),
    nome_engenheiro VARCHAR(100),
    observacoes TEXT,
    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
);
GO

-- Criando índices para melhorar performance
CREATE INDEX IX_relatorios_data ON relatorios(data_emissao);
CREATE INDEX IX_relatorios_tipo_inspecao ON relatorios(tipo_inspecao);
CREATE INDEX IX_relatorios_resultado ON relatorios(resultado_inspecao);
CREATE INDEX IX_relatorios_tipo_equipamento ON relatorios(tipo_equipamento);
CREATE INDEX IX_relatorios_engenheiro ON relatorios(nome_engenheiro);
GO

-- Inserindo dados dos relatórios existentes (se houver)
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
    i.id as inspecao_id,
    i.data_inspecao as data_emissao,
    'arquivo_' + CAST(i.id as VARCHAR) + '.pdf' as link_arquivo,
    i.tipo_inspecao as tipo_inspecao,
    i.resultado as resultado_inspecao,
    e.tag as tipo_equipamento,
    u.nome as nome_engenheiro,
    i.recomendacoes as observacoes
FROM inspecoes i
JOIN equipamentos e ON i.equipamento_id = e.id
JOIN usuarios u ON i.engenheiro_id = u.id;
GO 