import pyodbc
import logging
import bcrypt

# --- Configuração ---
SERVER = 'DESKTOP-GUFFT6G\\MSSQLSERVER01'
DATABASE = 'sistema_inspecao_db'
ADMIN_EMAIL = 'admin@empresa.com'
ADMIN_NAME = 'Administrador'
ADMIN_PASSWORD = 'admin123' # Senha padrão

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ensure_admin")

# --- Funções Auxiliares ---
def hash_password(password: str) -> str:
    """Gera o hash da senha usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        logger.warning("Hash de senha inválido encontrado no banco de dados.")
        return False

def connect_db():
    """Conecta ao banco de dados SQL Server"""
    try:
        conn_str = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        logger.info("Conexão com o banco de dados estabelecida.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise

# --- Lógica Principal ---
if __name__ == "__main__":
    logger.info("--- Verificando/Garantindo Usuário Admin ---")
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        admin_password_hash = hash_password(ADMIN_PASSWORD)
        
        # Verificar se o admin existe
        cursor.execute("SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = ?", ADMIN_EMAIL)
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, user_name, current_hash, is_active = admin_user
            logger.info(f"Usuário admin encontrado (ID: {user_id}, Nome: {user_name}).")
            
            needs_update = False
            updates = []
            params = []
            
            # 1. Verificar status
            if not is_active:
                logger.warning("Usuário admin está inativo. Reativando...")
                updates.append("ativo = 1")
                needs_update = True
            else:
                logger.info("Status do admin: Ativo.")
                
            # 2. Verificar senha
            if not check_password(ADMIN_PASSWORD, current_hash):
                logger.warning("Senha do admin não corresponde. Atualizando...")
                updates.append("senha_hash = ?")
                params.append(admin_password_hash)
                needs_update = True
            else:
                logger.info("Senha do admin está correta.")
                
            # 3. Atualizar se necessário
            if needs_update:
                params.append(user_id) # Adiciona o ID para a cláusula WHERE
                update_query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(update_query, params)
                conn.commit()
                logger.info("Usuário admin atualizado com sucesso!")
            else:
                logger.info("Usuário admin já está correto.")
                
        else:
            # Admin não existe, criar
            logger.warning(f"Usuário admin '{ADMIN_EMAIL}' não encontrado. Criando...")
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, empresa, ativo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ADMIN_NAME, ADMIN_EMAIL, admin_password_hash, 'admin', None, 1))
            conn.commit()
            logger.info("Usuário admin criado com sucesso!")
            
        logger.info("--- Verificação/Criação do Admin Concluída ---")
            
    except Exception as e:
        logger.error(f"--- Ocorreu um erro: {e} ---")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Conexão com o banco de dados fechada.") 