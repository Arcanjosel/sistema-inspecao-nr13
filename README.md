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

---

## Funcionalidades

- Autenticação de usuários (admin e cliente)
- Cadastro e gerenciamento de usuários
- Cadastro e gerenciamento de equipamentos
- Registro e consulta de inspeções técnicas
- Emissão e consulta de relatórios
- Notificações e logs
- Interface gráfica moderna (PyQt5)
- Tema claro/escuro
- Botões CRUD padronizados com ícones SVG
- Atualização automática das tabelas a cada 5 segundos
- Suporte multi-usuário com sincronização em tempo real
- Janela de debug para visualização e cadastro rápido de usuários

---

## Requisitos

- Python 3.11+
- SQL Server 2017 ou superior
- [pyodbc](https://pypi.org/project/pyodbc/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [PyQt5](https://pypi.org/project/PyQt5/)

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

---

## Configuração do Banco de Dados

1. **Crie o banco de dados e as tabelas** no SQL Server:

   ```sql
   CREATE DATABASE sistema_inspecao_db;
   GO

   USE sistema_inspecao_db;
   GO

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

   CREATE TABLE equipamentos (
       id INT IDENTITY(1,1) PRIMARY KEY,
       tipo VARCHAR(20) NOT NULL,
       empresa VARCHAR(100) NOT NULL,
       localizacao VARCHAR(200) NOT NULL,
       codigo_projeto VARCHAR(50) NOT NULL,
       pressao_maxima FLOAT NOT NULL,
       temperatura_maxima FLOAT NOT NULL,
       data_ultima_inspecao DATETIME NULL,
       data_proxima_inspecao DATETIME NULL,
       status VARCHAR(20) DEFAULT 'ativo'
   );
   GO

   CREATE TABLE inspecoes (
       id INT IDENTITY(1,1) PRIMARY KEY,
       equipamento_id INT NOT NULL,
       data_inspecao DATETIME NOT NULL,
       tipo_inspecao VARCHAR(20) NOT NULL,
       engenheiro_responsavel VARCHAR(100) NOT NULL,
       resultado VARCHAR(20) NOT NULL,
       recomendacoes TEXT NULL,
       proxima_inspecao DATETIME NULL,
       FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
   );
   GO

   CREATE TABLE relatorios (
       id INT IDENTITY(1,1) PRIMARY KEY,
       inspecao_id INT NOT NULL,
       data_emissao DATETIME NOT NULL,
       link_arquivo VARCHAR(255) NOT NULL,
       observacoes TEXT NULL,
       FOREIGN KEY (inspecao_id) REFERENCES inspecoes(id)
   );
   GO
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

**O sistema não cria um usuário admin automaticamente.**  
Você pode criar o primeiro usuário admin de duas formas:

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
- Permite visualizar todos os usuários cadastrados e criar novos usuários (admin ou cliente) rapidamente.

---

## Estrutura do Projeto

```
seu-repo/
│
├── main.py
├── requirements.txt
├── .env
├── logs/
│   └── sistema.log
├── controllers/
│   ├── auth_controller.py
│   ├── equipment_controller.py
│   ├── inspection_controller.py
│   └── report_controller.py
├── database/
│   ├── connection.py
│   └── models.py
├── ui/
│   ├── admin_ui.py
│   ├── client_ui.py
│   ├── login_window.py
│   └── debug_window.py
│   ├── CTREINA_LOGO.png
│   ├── CTREINA_LOGO_FIT.png
│   ├── user.png
│   ├── equipamentos.png
│   ├── inspecoes.png
│   └── relatorios.png
└── ...
```

---

## Estrutura do Banco de Dados

- **usuarios:** id, nome, email, senha_hash, tipo_acesso, empresa, ativo
- **equipamentos:** id, tipo, empresa, localizacao, codigo_projeto, pressao_maxima, temperatura_maxima, data_ultima_inspecao, data_proxima_inspecao, status
- **inspecoes:** id, equipamento_id, data_inspecao, tipo_inspecao, engenheiro_responsavel, resultado, recomendacoes, proxima_inspecao
- **relatorios:** id, inspecao_id, data_emissao, link_arquivo, observacoes

---

## Sistema de Atualização em Tempo Real

O sistema implementa um mecanismo robusto de atualização em tempo real, permitindo que múltiplos usuários trabalhem simultaneamente sem conflitos de dados.

### Características principais:

- **Timer de Atualização:** Todas as tabelas são atualizadas automaticamente a cada 5 segundos através de um QTimer configurado na inicialização da aplicação.

- **Sincronização Forçada:** Cada controlador (AuthController, EquipmentController, InspectionController, ReportController) possui um método `force_sync()` que garante a sincronização com o banco de dados.

- **Atualização Após Operações CRUD:** Todas as operações de criação, edição e exclusão de registros forçam uma sincronização com o banco de dados e atualizam todas as tabelas relacionadas.

- **Manutenção do Estado da Interface:** Durante a atualização das tabelas, o sistema preserva a aba atual e, quando possível, a linha selecionada.

- **Conexão Persistente:** O sistema utiliza um padrão Singleton para gerenciar a conexão com o banco de dados, garantindo a reutilização da conexão e evitando vazamentos de recursos.

### Como funciona:

1. Quando um usuário realiza alterações (adicionar, editar ou excluir registros), o método `force_sync()` é chamado automaticamente.

2. A cada 5 segundos, o método `refresh_all_tables()` é executado, realizando:
   - Sincronização forçada com todos os controladores
   - Recarregamento de todas as tabelas com dados atualizados
   - Preservação da aba atual para não interromper o trabalho do usuário

3. Se ocorrerem erros de conexão, o sistema tentará reconectar automaticamente ao banco de dados.

Este sistema garante que todos os usuários sempre vejam dados atualizados e que as alterações de um usuário sejam rapidamente refletidas para os demais.

---

## Interface Gráfica

### Recursos da Interface

- **Temas Claro/Escuro:** O sistema suporta alternância entre tema claro e escuro através do botão de tema na barra inferior.
- **Botões CRUD Padronizados:** Todos os botões de ação (Adicionar, Editar, Excluir, Ativar/Desativar, Visualizar) seguem um padrão visual consistente com ícones SVG.
- **Ícones SVG:** Utilizados na interface para melhor escalabilidade e adaptação ao tema.
- **Tabelas Responsivas:** Todas as tabelas se adaptam ao tamanho da janela e possuem cores alternadas para melhor visualização.
- **Abas com Ícones:** A navegação entre as diferentes seções (Usuários, Equipamentos, Inspeções, Relatórios) é feita através de abas com ícones intuitivos.

### Cores dos Botões CRUD

- **Adicionar:** Verde (#28a745)
- **Editar:** Azul (#007bff)
- **Excluir:** Vermelho (#dc3545)
- **Ativar/Desativar:** Cinza (#6c757d)
- **Visualizar:** Ciano (#17a2b8)
- **Tema:** Preto/Cinza Claro (dependendo do tema atual)

### Espaçamento e Layout

- Os botões possuem espaçamento uniforme de 5 pixels entre si para melhor usabilidade.
- Layout com margens adequadas e espaçamento entre os elementos para melhor organização visual.

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