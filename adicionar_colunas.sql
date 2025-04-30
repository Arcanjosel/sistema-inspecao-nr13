USE sistema_inspecao_db;
GO

-- Adicionando colunas que faltam na tabela equipamentos
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('equipamentos') AND name = 'tag')
BEGIN
    ALTER TABLE equipamentos ADD tag VARCHAR(50);
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('equipamentos') AND name = 'categoria')
BEGIN
    ALTER TABLE equipamentos ADD categoria VARCHAR(50);
END
GO

-- Atualizando registros existentes para preencher tag e categoria
UPDATE equipamentos 
SET tag = ISNULL(tag, tipo),
    categoria = CASE 
        WHEN pressao_maxima > 0 THEN 'Vaso de Pressão'
        ELSE 'Equipamento Geral'
    END
WHERE tag IS NULL OR categoria IS NULL;
GO

-- Adicionando colunas que faltam na tabela inspecoes
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('inspecoes') AND name = 'prazo_proxima_inspecao')
BEGIN
    ALTER TABLE inspecoes ADD prazo_proxima_inspecao DATETIME;
END
GO

-- Atualizando registros existentes para preencher prazo_proxima_inspecao
UPDATE inspecoes 
SET prazo_proxima_inspecao = ISNULL(prazo_proxima_inspecao, data_proxima_inspecao)
WHERE prazo_proxima_inspecao IS NULL;
GO

-- Adicionando colunas que faltam na tabela relatorios
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('relatorios') AND name = 'tipo_inspecao')
BEGIN
    ALTER TABLE relatorios ADD tipo_inspecao VARCHAR(50);
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('relatorios') AND name = 'resultado_inspecao')
BEGIN
    ALTER TABLE relatorios ADD resultado_inspecao VARCHAR(50);
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('relatorios') AND name = 'tipo_equipamento')
BEGIN
    ALTER TABLE relatorios ADD tipo_equipamento VARCHAR(50);
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('relatorios') AND name = 'nome_engenheiro')
BEGIN
    ALTER TABLE relatorios ADD nome_engenheiro VARCHAR(100);
END
GO

-- Atualizando registros existentes com informações das inspeções
UPDATE r
SET 
    r.tipo_inspecao = i.tipo,
    r.resultado_inspecao = i.resultado,
    r.tipo_equipamento = e.tipo,
    r.nome_engenheiro = u.nome
FROM relatorios r
JOIN inspecoes i ON r.inspecao_id = i.id
JOIN equipamentos e ON i.equipamento_id = e.id
JOIN usuarios u ON i.engenheiro_id = u.id
WHERE r.tipo_inspecao IS NULL 
   OR r.resultado_inspecao IS NULL 
   OR r.tipo_equipamento IS NULL 
   OR r.nome_engenheiro IS NULL;
GO

-- Adicionando índices para melhorar performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_equipamentos_tag' AND object_id = OBJECT_ID('equipamentos'))
BEGIN
    CREATE INDEX IX_equipamentos_tag ON equipamentos(tag);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_equipamentos_categoria' AND object_id = OBJECT_ID('equipamentos'))
BEGIN
    CREATE INDEX IX_equipamentos_categoria ON equipamentos(categoria);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inspecoes_data' AND object_id = OBJECT_ID('inspecoes'))
BEGIN
    CREATE INDEX IX_inspecoes_data ON inspecoes(data_inspecao);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_data' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    CREATE INDEX IX_relatorios_data ON relatorios(data_emissao);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_inspecao' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    CREATE INDEX IX_relatorios_tipo_inspecao ON relatorios(tipo_inspecao);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_resultado' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    CREATE INDEX IX_relatorios_resultado ON relatorios(resultado_inspecao);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_tipo_equipamento' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    CREATE INDEX IX_relatorios_tipo_equipamento ON relatorios(tipo_equipamento);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_relatorios_engenheiro' AND object_id = OBJECT_ID('relatorios'))
BEGIN
    CREATE INDEX IX_relatorios_engenheiro ON relatorios(nome_engenheiro);
END
GO 