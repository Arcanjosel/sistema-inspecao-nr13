# Sistema de Gerenciamento de Inspeções Técnicas NR-13

Sistema desktop em Python para gestão de inspeções de vasos de pressão, caldeiras e equipamentos conforme a NR-13, com autenticação, controle de usuários, equipamentos, inspeções, relatórios e notificações.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Execução](#execução)
- [Usuário Administrador Inicial](#usuário-administrador-inicial)
- [Janela de Debug](#janela-de-debug)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Sistema de Atualização em Tempo Real](#sistema-de-atualização-em-tempo-real)
- [Interface Gráfica](#interface-gráfica)
- [Dicas de Manutenção](#dicas-de-manutenção)
- [Licença](#licença)
- [Controle de Manutenção de Equipamentos](#controle-de-manutenção-de-equipamentos)
- [Geração de Laudos Técnicos](#geração-de-laudos-técnicos)
- [Migrações de Banco de Dados](#migrações-de-banco-de-dados)

---

## Funcionalidades

- Autenticação de usuários (admin, cliente e engenheiros)
- Cadastro e gerenciamento de usuários
- Cadastro e gerenciamento de engenheiros com registro CREA
- Cadastro e gerenciamento de equipamentos
- Registro e consulta de inspeções técnicas
- Emissão e consulta de relatórios
- Geração de laudos técnicos em PDF conforme NR-13
- Notificações e logs
- Interface gráfica moderna (PyQt5)
- Tema claro/escuro
- Botões CRUD padronizados com ícones SVG
- Atualização automática das tabelas a cada 5 segundos
- Suporte multi-usuário com sincronização em tempo real
- Janela de debug para visualização e cadastro rápido de usuários
- Sistema de migração automática do banco de dados

---

## Requisitos

- Python 3.11+
- SQL Server 2017 ou superior
- [pyodbc](https://pypi.org/project/pyodbc/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [reportlab](https://pypi.org/project/reportlab/) (para geração de PDFs)

---

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o script de instalação do banco de dados:
   ```bash
   python setup_database.py
   ```
   Ou use diretamente o script SQL no arquivo `database_setup.sql`.

---

## Configuração do Banco de Dados

1. **Execute o script `database_setup.sql` no SQL Server:**

Este script criará:
- O banco de dados `sistema_inspecao_db`
- Todas as tabelas necessárias com suas respectivas colunas
- Um usuário administrador padrão para testes

A estrutura atual do banco de dados inclui:
- Tabela de usuários com suporte a engenheiros (campo CREA)
- Tabela de equipamentos com informações técnicas
- Tabela de inspeções com vínculo a engenheiros
- Tabela de relatórios

Ou use a instalação automática com o script Python:
```bash
python setup_database.py
```

---

## Configuração do Ambiente

1. **Crie um arquivo `.env` na raiz do projeto** com o seguinte conteúdo:

   ```
   DB_SERVER=SEU_SERVIDOR_SQL
   DB_NAME=sistema_inspecao_db
   DB_USERNAME=seu_usuario
   DB_PASSWORD=sua_senha
   DB_TRUSTED_CONNECTION=False

   # Configurações de e-mail (opcional)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=seu_email@gmail.com
   SMTP_PASSWORD=sua_senha_de_app
   FROM_EMAIL=seu_email@gmail.com

   # Outras configurações...
   LOG_LEVEL=INFO
   LOG_FILE=logs/sistema.log
   ```

2. **Crie a pasta de logs:**
   ```bash
   mkdir logs
   ```

---

## Execução

Execute o sistema sempre pelo arquivo principal:

```bash
python main.py
```

---

## Usuário Administrador Inicial

O script de instalação cria automaticamente um usuário administrador padrão:
- **Email:** admin@empresa.com
- **Senha:** admin123

Recomendamos alterar esta senha imediatamente após o primeiro login.

Alternativamente, você pode criar o primeiro usuário admin de duas formas:

### 1. Pela janela de debug (recomendado para testes)

- Na tela de login, clique no botão ⚙️ (engrenagem).
- Preencha os campos do formulário, escolha o tipo "admin" e clique em "Cadastrar Usuário".

### 2. Pelo Python shell

```python
from controllers.auth_controller import AuthController
auth = AuthController()
sucesso, mensagem = auth.criar_usuario(
    nome="Administrador",
    email="admin@empresa.com",
    senha="admin123",  # Altere para uma senha forte!
    tipo_acesso="admin"
)
print(mensagem)
```

---

## Janela de Debug

- Acesse pela tela de login, clicando no botão ⚙️.
- Permite visualizar todos os usuários cadastrados e criar novos usuários (admin, cliente ou engenheiro) rapidamente.

---

## Estrutura do Projeto

```
seu-repo/
│
├── main.py
├── requirements.txt
├── .env
├── database_setup.sql
├── setup_database.py
├── logs/
│   └── sistema.log
├── controllers/
│   ├── auth_controller.py
│   ├── equipment_controller.py
│   ├── inspection_controller.py
│   └── report_controller.py
│   └── engineer_controller.py
├── database/
│   ├── connection.py
│   ├── models.py
│   └── migrations.py
├── ui/
│   ├── admin_ui.py
│   ├── client_ui.py
│   ├── login_window.py
│   ├── inspection_ui.py
│   ├── laudo_window.py
│   └── debug_window.py
│   ├── CTREINA_LOGO.png
│   ├── CTREINA_LOGO_FIT.png
│   ├── user.png
│   ├── equipamentos.png
│   ├── inspecoes.png
│   └── relatorios.png
└── utils/
    └── pdf_generator.py
```

---

## Estrutura do Banco de Dados

- **usuarios:** id, nome, email, senha_hash, tipo_acesso, empresa, ativo, crea
- **equipamentos:** id, tipo, empresa, localizacao, codigo_projeto, pressao_maxima, temperatura_maxima, data_ultima_inspecao, data_proxima_inspecao, status
- **inspecoes:** id, equipamento_id, data_inspecao, tipo_inspecao, engenheiro_responsavel, resultado, recomendacoes, proxima_inspecao, engenheiro_id
- **relatorios:** id, inspecao_id, data_emissao, link_arquivo, observacoes

---

## Sistema de Atualização em Tempo Real

O sistema implementa um mecanismo robusto de atualização em tempo real, permitindo que múltiplos usuários trabalhem simultaneamente sem conflitos de dados.

Os dados são sincronizados regularmente, garantindo que as alterações feitas por um usuário sejam refletidas para todos os outros usuários do sistema.

---

## Geração de Laudos Técnicos

O sistema agora suporta a geração de laudos técnicos em PDF conforme a NR-13. Para gerar um laudo:

1. Selecione uma inspeção na aba "Inspeções"
2. Clique no botão "GERAR LAUDO TÉCNICO"
3. Preencha os dados complementares no formulário
4. Clique em "Gerar PDF"

O laudo técnico incluirá:
- Informações do equipamento inspecionado
- Dados do engenheiro responsável com número CREA
- Resultados da inspeção
- Recomendações técnicas
- Datas de inspeção e próxima inspeção

---

## Migrações de Banco de Dados

O sistema agora inclui um mecanismo de migração automática do banco de dados. Quando novas funcionalidades são adicionadas que requerem alterações no esquema do banco de dados, o sistema automaticamente atualiza o banco durante a inicialização.

As migrações disponíveis incluem:
- Adição de campo CREA na tabela de usuários para engenheiros

Para executar manualmente as migrações:
```python
from database.migrations import executar_migracoes
executar_migracoes()
```

---

## Dicas de Manutenção

- Sempre execute o sistema pelo `main.py`.
- Para evitar erros de importação, mantenha a estrutura de pastas.
- Se mudar o nome de alguma coluna no banco, atualize todos os SELECTs e dicionários no código.
- Use a janela de debug para verificar rapidamente os usuários cadastrados.
- Consulte os logs em `logs/sistema.log` para depuração de erros.
- Ao adicionar novos botões CRUD, use o método `create_crud_button` para manter a consistência visual.
- Para adicionar novos ícones SVG, inclua-os no dicionário `self.icons` na classe `AdminWindow`.
- Para implementar novas operações de banco de dados, siga o padrão dos controladores existentes, sempre usando o método `force_sync()` após operações de escrita.
- Evite realizar operações de banco de dados diretamente na UI; sempre utilize os controladores apropriados.
- Se precisar aumentar ou diminuir a frequência de atualização das tabelas, ajuste o valor do timer em `self.refresh_timer.start(5000)` na inicialização da classe `AdminWindow`.

---

## Licença

Este projeto é open-source e pode ser adaptado conforme a necessidade da sua empresa ou cliente.

## Controle de Manutenção de Equipamentos

O sistema agora inclui funcionalidades para controle de manutenção dos equipamentos:

### Funcionalidades

- Visualização da data da última manutenção
- Cálculo automático da próxima manutenção necessária baseado na frequência definida
- Alerta visual com código de cores:
  - Vermelho: Manutenção atrasada
  - Amarelo: Manutenção necessária em menos de 30 dias
  - Normal: Manutenção em dia

### Como Registrar uma Manutenção

1. Na aba "Equipamentos", selecione o equipamento desejado
2. Clique no botão "Registrar Manutenção"
3. Preencha a data da manutenção
4. Defina a frequência em dias (padrão: 180 dias)
5. Adicione observações se necessário
6. Clique em "Registrar"

### Preparação da Base de Dados

Antes de utilizar esta funcionalidade, execute o script para atualizar a estrutura da tabela de equipamentos:

```bash
python update_equipment_table.py
``` 