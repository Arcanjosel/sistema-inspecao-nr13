-- Tabela de Relatórios para o sistema de inspeção NR-13
-- Esta tabela armazena informações sobre relatórios de inspeção gerados no sistema

-- Remover a tabela de relatórios se ela já existir
DROP TABLE IF EXISTS relatorios;

-- Criar a tabela de relatórios com uma estrutura mais robusta
CREATE TABLE relatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspecao_id INTEGER NOT NULL,
    equipamento_id INTEGER NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    data_emissao DATETIME NOT NULL,
    data_validade DATETIME,
    tipo_relatorio VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pendente',
    conformidade BOOLEAN DEFAULT 0,
    nivel_risco VARCHAR(50),
    link_arquivo VARCHAR(255),
    observacoes TEXT,
    recomendacoes TEXT,
    responsavel_id INTEGER NOT NULL,
    assinatura_digital VARCHAR(255),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    criado_por INTEGER,
    modificado_por INTEGER,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id),
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
    FOREIGN KEY (criado_por) REFERENCES usuarios(id),
    FOREIGN KEY (modificado_por) REFERENCES usuarios(id)
);

-- Índices para melhorar a performance de consultas
CREATE INDEX idx_relatorios_inspecao ON relatorios(inspecao_id);
CREATE INDEX idx_relatorios_equipamento ON relatorios(equipamento_id);
CREATE INDEX idx_relatorios_responsavel ON relatorios(responsavel_id);
CREATE INDEX idx_relatorios_data_emissao ON relatorios(data_emissao);
CREATE INDEX idx_relatorios_status ON relatorios(status);
CREATE INDEX idx_relatorios_conformidade ON relatorios(conformidade);

-- Trigger para atualizar a data de modificação
CREATE TRIGGER atualizar_data_modificacao_relatorios
AFTER UPDATE ON relatorios
FOR EACH ROW
BEGIN
    UPDATE relatorios 
    SET data_modificacao = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Comentários explicando os campos
-- id: Identificador único do relatório
-- inspecao_id: ID da inspeção relacionada ao relatório
-- equipamento_id: ID do equipamento inspecionado
-- titulo: Título descritivo do relatório
-- data_emissao: Data em que o relatório foi emitido
-- data_validade: Data em que o relatório expira (opcional)
-- tipo_relatorio: Tipo de relatório (ex: Visual, Ultrassom, Radiografia, etc.)
-- status: Status do relatório (Pendente, Em Análise, Aprovado, Rejeitado, etc.)
-- conformidade: Indica se o equipamento está em conformidade com as normas (1 = Sim, 0 = Não)
-- nivel_risco: Nível de risco identificado (Baixo, Médio, Alto, Crítico)
-- link_arquivo: Caminho para o arquivo do relatório
-- observacoes: Observações gerais sobre o relatório
-- recomendacoes: Recomendações para correção de não conformidades
-- responsavel_id: ID do usuário responsável pelo relatório
-- assinatura_digital: Hash ou referência à assinatura digital do responsável
-- data_criacao: Data e hora de criação do registro
-- data_modificacao: Data e hora da última modificação do registro
-- criado_por: ID do usuário que criou o registro
-- modificado_por: ID do usuário que modificou o registro por último
-- ativo: Indica se o registro está ativo (1) ou excluído logicamente (0) 