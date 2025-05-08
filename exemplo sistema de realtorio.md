# Gerador de Laudos NR-13

Sistema web para geração de laudos técnicos e certificados de inspeção conforme a Norma Regulamentadora 13 (NR-13) - Portaria MTP nº 1.846/2022.

## 📋 Sobre o Projeto

O Gerador de Laudos NR-13 é uma aplicação web desenvolvida para facilitar a criação de laudos técnicos e certificados para equipamentos sob pressão, sem a necessidade de cadastro ou login. A aplicação segue rigorosamente as exigências técnicas da NR-13, que regulamenta a inspeção de caldeiras, vasos de pressão e tubulações.

## ✅ Funcionalidades Principais

### Geração de Laudos Técnicos
- **Tipos de equipamentos suportados:**
  - Vasos de Pressão (Grupos 1 a 5)
  - Caldeiras (Categorias A, B e C)
  - Tubulações (Categorias I, II e III)
  - Tanques metálicos (com diâmetro externo > 3m e capacidade > 20.000L)

- **Informações completas:**
  - Dados do cliente
  - Especificações do equipamento
  - Detalhes da inspeção
  - Resultados técnicos
  - Recomendações específicas
  - Conclusões
  - Dados do profissional responsável
  - Documentação completa conforme NR-13

### Geração de Certificados de Válvulas
- Certificados para válvulas de segurança (PSV)
- Certificados para válvulas redutoras de pressão (PRV)
- Certificados para outros tipos de válvulas

### Recursos Avançados
- **Classificação automática de fluidos** (Classes A e B conforme subitem 13.5.1.1.1)
- **Classificação automática de equipamentos** baseada em parâmetros técnicos
- **Cálculo automático de categorias de risco** conforme NR-13
- **Cálculo de vida remanescente** com base no tipo e idade do equipamento
- **Checklist interativo** para verificação de conformidade com a NR-13
- **Recomendações específicas** por categoria de equipamento e tipo de fluido
- **Determinação automática do prazo de validade** do laudo conforme categoria
- **Alertas para avaliação de integridade** em equipamentos com mais de 25 anos
- **Suporte para estabelecimentos com SPIE** (prazos estendidos)
- **Guia informativo** sobre as categorias da NR-13 e prazos de inspeção
- **Geração de PDF** formatado e pronto para impressão

## 🚀 Como Usar

1. Acesse a página inicial do sistema
2. Escolha entre criar um laudo técnico ou um certificado de válvula
3. Preencha o formulário com as informações necessárias
4. Utilize o botão "Preencher Automaticamente" para gerar análises técnicas com base nos dados informados
5. Use o "Checklist de Conformidade" para verificar os requisitos da NR-13
6. Revise as informações e clique em "Gerar Laudo PDF" ou "Gerar Certificado PDF"
7. Faça o download do documento gerado em formato PDF

## 📋 Páginas Disponíveis

- **Página Inicial:** Visão geral do sistema com acesso às principais funcionalidades
- **Formulário de Laudo:** Interface completa para criação de laudos técnicos NR-13
- **Formulário de Certificado:** Interface para criação de certificados de válvulas
- **Checklist de Conformidade:** Ferramenta para verificação dos requisitos da NR-13
- **Classificador de Equipamentos:** Calculadora para determinar categorias e prazos
- **Avaliação de Integridade:** Módulo específico para equipamentos com mais de 25 anos

## 🛠️ Plano de Desenvolvimento

Estamos seguindo os seguintes passos para a implementação do sistema:

1. ✅ **Atualização das Categorias**
   - Categorias exatas conforme NR-13 atual (Portaria MTP nº 1.846/2022)
   - Classificação de fluidos Classes A e B conforme subitem 13.5.1.1.1

2. ✅ **Ampliação de Equipamentos Cobertos**
   - Suporte para todos os equipamentos da norma, incluindo tanques metálicos

3. ✅ **Documentação Completa**
   - Campos para registro de segurança conforme exigências da NR-13
   - Documentação de prontuário completo dos equipamentos

4. ✅ **Prazos de Inspeção**
   - Alertas automáticos baseados nos prazos máximos de inspeções periódicas
   - Opções para estabelecimentos com SPIE (prazos estendidos)

5. ✅ **Avaliação de Integridade**
   - Módulo específico para equipamentos com mais de 25 anos

6. ✅ **Verificação de Conformidade**
   - Checklist automático para verificação de todos os itens obrigatórios da NR-13
   - Verificação dos dispositivos de segurança obrigatórios

7. ✅ **Relatórios Completos**
   - Relatórios incluindo todas as informações exigidas pela norma
   - Campo para registro das condições que possam constituir risco grave e iminente

8. ✅ **Informações de Profissionais**
   - Campo específico para informações do Profissional Legalmente Habilitado (PLH)
   - Opção para registro de certificação conforme Anexo III da NR-13

9. 🔄 **Implementação da Interface do Usuário** (Em andamento)
   - Interface de Checklist Interativo 
   - Classificador de Equipamentos
   - Módulo de Avaliação de Integridade
   - Sistema de Alertas
   - Formulários específicos por tipo de equipamento

10. ⏳ **Testes e Validação** (Próxima etapa)
    - Testes com profissionais da área
    - Validação de conformidade com a NR-13

## ⚠️ Informações Importantes

- O sistema gera documentos técnicos sem necessidade de cadastro
- Todos os laudos são gerados conforme os requisitos da NR-13
- A aplicação calcula automaticamente a categoria de risco e prazos recomendados
- Certifique-se de preencher corretamente as informações técnicas do equipamento
- O sistema é uma ferramenta auxiliar e não substitui o conhecimento técnico do profissional habilitado

## 🔧 Tecnologias Utilizadas

- Python (FastAPI)
- SQLAlchemy para ORM
- ReportLab para geração de PDFs
- HTML/CSS/JavaScript para interface web

## 📝 Observações

Este sistema foi desenvolvido para auxiliar profissionais habilitados na criação de documentos técnicos conformes com a NR-13. Os usuários são responsáveis pela precisão das informações fornecidas e pela adequação dos documentos gerados às exigências legais e normativas aplicáveis. 