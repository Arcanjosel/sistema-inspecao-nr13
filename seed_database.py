import pyodbc
import logging
import bcrypt
from datetime import datetime, timedelta, date
import random

# --- Configuração ---
SERVER = 'DESKTOP-GUFFT6G\\MSSQLSERVER01'
DATABASE = 'sistema_inspecao_db'
ADMIN_EMAIL = 'admin@empresa.com' # Email do admin a ser preservado

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("seed_db")

# --- Funções Auxiliares ---
def hash_password(password: str) -> str:
    """Gera o hash da senha usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def connect_db():
    """Conecta ao banco de dados SQL Server"""
    try:
        conn_str = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        logger.info("Conexão com o banco de dados estabelecida.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise # Re-levanta a exceção para parar o script se não conectar

def clear_data(conn):
    """Limpa os dados das tabelas, preservando o admin."""
    cursor = conn.cursor()
    try:
        logger.info("Limpando dados antigos...")
        # Ordem de exclusão para respeitar chaves estrangeiras
        cursor.execute("DELETE FROM relatorios")
        cursor.execute("DELETE FROM inspecoes")
        cursor.execute("DELETE FROM equipamentos")
        # Excluir todos os usuários EXCETO o admin
        cursor.execute("DELETE FROM usuarios WHERE email != ?", ADMIN_EMAIL)
        conn.commit()
        logger.info("Dados antigos limpos com sucesso (exceto admin).")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao limpar dados: {e}")
        raise
    finally:
        cursor.close()

def populate_data(conn):
    """Popula o banco de dados com dados de exemplo."""
    cursor = conn.cursor()
    try:
        logger.info("Iniciando população do banco de dados...")

        # --- 1. Clientes (Empresas) ---
        logger.info("Populando clientes (empresas)...")
        clientes = [
            ('Empresa Alpha', 'cliente.alpha@email.com', hash_password('senha123'), 'cliente', 'Empresa Alpha LTDA'),
            ('Beta Soluções', 'cliente.beta@email.com', hash_password('senha123'), 'cliente', 'Beta Soluções Industriais'),
            ('Gama Indústria', 'cliente.gama@email.com', hash_password('senha123'), 'cliente', 'Gama Indústria e Comércio')
        ]
        cursor.executemany("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, empresa)
            VALUES (?, ?, ?, ?, ?)
        """, clientes)
        conn.commit()
        logger.info(f"{len(clientes)} clientes inseridos.")
        
        # Obter IDs dos clientes inseridos
        cursor.execute("SELECT id, nome FROM usuarios WHERE tipo_acesso = 'cliente'")
        cliente_ids = {row.nome: row.id for row in cursor.fetchall()}
        logger.info(f"IDs dos clientes obtidos: {cliente_ids}")

        # --- 2. Engenheiros ---
        logger.info("Populando engenheiros...")
        engenheiros = [
            ('Carlos Silva', 'carlos.eng@email.com', hash_password('senha123'), 'eng', None),
            ('Ana Pereira', 'ana.eng@email.com', hash_password('senha123'), 'eng', None),
            ('João Souza', 'joao.eng@email.com', hash_password('senha123'), 'eng', None)
        ]
        cursor.executemany("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, empresa)
            VALUES (?, ?, ?, ?, ?)
        """, engenheiros)
        conn.commit()
        logger.info(f"{len(engenheiros)} engenheiros inseridos.")

        # Obter IDs dos engenheiros
        cursor.execute("SELECT id, nome FROM usuarios WHERE tipo_acesso = 'eng'")
        engenheiro_ids = {row.nome: row.id for row in cursor.fetchall()}
        logger.info(f"IDs dos engenheiros obtidos: {engenheiro_ids}")

        # --- 3. Equipamentos ---
        logger.info("Populando equipamentos...")
        equipamentos = [
            # Empresa Alpha
            ('VP-AL-001', 'Vaso de Pressão', cliente_ids['Empresa Alpha'], 'Fabricante X', 2018, 15.0, 12.0, 5.5, 'Ar Comprimido'),
            ('CAL-AL-001', 'Caldeira', cliente_ids['Empresa Alpha'], 'Fabricante Y', 2020, 10.0, 8.5, 20.0, 'Vapor d\'água'),
            ('TUB-AL-001', 'Tubulação', cliente_ids['Empresa Alpha'], 'Fabricante X', 2018, 20.0, 18.0, 0.5, 'Óleo Térmico'),
            # Beta Soluções
            ('VP-BT-001', 'Vaso de Pressão', cliente_ids['Beta Soluções'], 'Fabricante Z', 2019, 12.5, 10.0, 8.0, 'Nitrogênio'),
            ('TAN-BT-001', 'Tanque', cliente_ids['Beta Soluções'], 'Fabricante Y', 2021, 5.0, 4.0, 50.0, 'Água'),
            # Gama Indústria
            ('VP-GM-001', 'Vaso de Pressão', cliente_ids['Gama Indústria'], 'Fabricante X', 2017, 18.0, 15.0, 12.0, 'Ar Comprimido'),
            ('VP-GM-002', 'Vaso de Pressão', cliente_ids['Gama Indústria'], 'Fabricante Z', 2022, 14.0, 11.5, 6.0, 'Oxigênio')
        ]
        cursor.executemany("""
            INSERT INTO equipamentos (tag, categoria, empresa_id, fabricante, ano_fabricacao, 
                                    pressao_projeto, pressao_trabalho, volume, fluido, ativo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'ativo')
        """, equipamentos)
        conn.commit()
        logger.info(f"{len(equipamentos)} equipamentos inseridos.")

        # Obter IDs dos equipamentos
        cursor.execute("SELECT id, tag FROM equipamentos")
        equipamento_ids = {row.tag: row.id for row in cursor.fetchall()}
        logger.info(f"IDs dos equipamentos obtidos: {equipamento_ids}")

        # --- 4. Inspeções ---
        logger.info("Populando inspeções...")
        inspecoes = []
        tipos_inspecao = ["Visual", "Ultrassom", "Periódica", "Inicial"]
        # Encurtar resultados para segurança
        resultados = ["Aprovado", "Reprovado", "Pendente", "Aprov c/ Restr."] 
        today = datetime.now().date()

        for tag, eq_id in equipamento_ids.items():
            # Adiciona 1 a 3 inspeções por equipamento
            for i in range(random.randint(1, 3)):
                eng_nome, eng_id = random.choice(list(engenheiro_ids.items()))
                data_inspecao = today - timedelta(days=random.randint(10, 365*2))
                tipo = random.choice(tipos_inspecao)
                resultado = random.choice(resultados)
                # --- Encurtar a recomendação --- 
                recomendacao = f"Rec {i+1} p/ {tag}. Verif {random.choice(['vals', 'solda', 'manom'])}."
                inspecoes.append((
                    eq_id, eng_id, data_inspecao.strftime('%Y-%m-%d'), tipo, resultado, recomendacao
                ))
        
        # A query continua usando CONVERT para a data
        cursor.executemany("""
            INSERT INTO inspecoes (equipamento_id, engenheiro_id, data_inspecao, tipo_inspecao, resultado, recomendacoes)
            VALUES (?, ?, CONVERT(datetime, ?, 120), ?, ?, ?)
        """, inspecoes)
        conn.commit()
        logger.info(f"{len(inspecoes)} inspeções inseridas.")

        # Obter IDs das inspeções
        cursor.execute("SELECT id, equipamento_id, tipo_inspecao, data_inspecao FROM inspecoes")
        # Ler as datas como estão (o driver deve retornar objetos date/datetime ou strings)
        inspecao_ids = []
        for row in cursor.fetchall():
            data_lida = row.data_inspecao
            # Tenta converter para date se for string ou datetime
            if isinstance(data_lida, str):
                try:
                    data_obj = datetime.strptime(data_lida.split()[0], '%Y-%m-%d').date()
                except:
                    logger.warning(f"Não foi possível converter a data string '{data_lida}' para date. Usando data atual.")
                    data_obj = today # Fallback
            elif isinstance(data_lida, datetime):
                 data_obj = data_lida.date()
            else:
                data_obj = data_lida # Assumindo que já é date ou None
                
            if data_obj is None: # Handle None case
                 logger.warning(f"Data de inspeção lida como None para ID {row.id}. Usando data atual.")
                 data_obj = today
                 
            inspecao_ids.append((row.id, row.equipamento_id, row.tipo_inspecao, data_obj))
            
        logger.info(f"Total de {len(inspecao_ids)} IDs de inspeção obtidos.")

        # --- 5. Relatórios ---
        logger.info("Populando relatórios...")
        relatorios = []
        for insp_id, eq_id, tipo_insp, data_insp in inspecao_ids:
            if not isinstance(data_insp, date): 
                 logger.warning(f"Skipping relatório para inspeção {insp_id} devido a data inválida: {data_insp}")
                 continue
            if random.random() < 0.7:
                data_emissao = data_insp + timedelta(days=random.randint(1, 10))
                arquivo = f"relatorios/REL_{eq_id}_{insp_id}_{data_emissao.strftime('%Y%m%d')}.pdf" # Caminho fictício
                # --- Encurtar observações --- 
                observacoes = f"Obs relatório insp {tipo_insp} de {data_insp.strftime('%d/%m')}."
                relatorios.append((
                    insp_id, data_emissao.strftime('%Y-%m-%d'), arquivo, observacoes
                ))

        # A query continua usando CONVERT para a data
        cursor.executemany("""
            INSERT INTO relatorios (inspecao_id, data_emissao, link_arquivo, observacoes)
            VALUES (?, CONVERT(datetime, ?, 120), ?, ?)
        """, relatorios)
        conn.commit()
        logger.info(f"{len(relatorios)} relatórios inseridos.")

        logger.info("População do banco de dados concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao popular dados: {e}")
        raise
    finally:
        cursor.close()

# --- Execução Principal ---
if __name__ == "__main__":
    logger.info("--- Iniciando Script de População do Banco de Dados ---")
    conn = None
    try:
        conn = connect_db()
        clear_data(conn)
        populate_data(conn)
        logger.info("--- Script concluído com sucesso! ---")
    except Exception as e:
        logger.error(f"--- Ocorreu um erro durante a execução do script: {e} ---")
    finally:
        if conn:
            conn.close()
            logger.info("Conexão com o banco de dados fechada.") 