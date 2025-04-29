"""
Controlador responsável pela autenticação e gerenciamento de usuários.
"""
import bcrypt
import logging
from typing import Optional, Tuple
from database.connection import DatabaseConnection
from database.models import Usuario
import traceback

logger = logging.getLogger(__name__)

class AuthController:
    """
    Controlador responsável por operações de autenticação e gerenciamento de usuários.
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        
    def _hash_password(self, password: str) -> str:
        """Gera o hash da senha usando bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
    def _check_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[int]]:
        """
        Realiza o login do usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Tuple[bool, str, Optional[int]]: (sucesso, mensagem, usuario_id)
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, nome, email, senha_hash, tipo_acesso, empresa, ativo 
                FROM usuarios 
                WHERE email = ? AND ativo = 1
                """,
                (email,)
            )
            user_data = cursor.fetchone()
            
            if not user_data:
                return False, "Usuário não encontrado ou inativo", None
                
            if not self._check_password(password, user_data[3]):
                return False, "Senha incorreta", None
                
            # Salva o usuário atual para uso posterior
            self.usuario_atual = {
                'id': user_data[0],
                'nome': user_data[1],
                'email': user_data[2],
                'senha_hash': user_data[3],
                'tipo_acesso': user_data[4],
                'empresa': user_data[5],
                'ativo': user_data[6]
            }
            return True, "Login realizado com sucesso", user_data[0]
            
        except Exception as e:
            logger.error(f"Erro ao realizar login: {str(e)}")
            return False, f"Erro ao realizar login: {str(e)}", None
            
        finally:
            cursor.close()
            
    def criar_usuario(self, nome: str, email: str, senha: str, tipo_acesso: str, empresa: Optional[str] = None) -> Tuple[bool, str]:
        """
        Cria um novo usuário no sistema.
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            senha: Senha do usuário
            tipo_acesso: Tipo de acesso do usuário ('admin' ou 'cliente')
            empresa: Nome da empresa (opcional)
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Verifica se o email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "Email já cadastrado"
            
            senha_hash = self._hash_password(senha)
            
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, empresa)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nome, email, senha_hash, tipo_acesso, empresa)
            )
            
            conn.commit()
            return True, "Usuário criado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            return False, f"Erro ao criar usuário: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_usuario_atual(self) -> Optional[dict]:
        """
        Retorna os dados do usuário atual.
        
        Returns:
            Optional[dict]: Dados do usuário ou None se não houver usuário logado
        """
        return getattr(self, 'usuario_atual', None)
            
    def alterar_senha(self, email: str, nova_senha: str) -> bool:
        """
        Altera a senha de um usuário.
        
        Args:
            email: Email do usuário
            nova_senha: Nova senha
            
        Returns:
            bool: True se senha alterada com sucesso
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            nova_senha_hash = self._hash_password(nova_senha)
            
            cursor.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
                (nova_senha_hash, email)
            )
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            
    def desativar_usuario(self, email: str) -> bool:
        """
        Desativa um usuário no sistema.
        
        Args:
            email: Email do usuário
            
        Returns:
            bool: True se usuário desativado com sucesso
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE usuarios SET ativo = 0 WHERE email = ?",
                (email,)
            )
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desativar usuário: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()

    def get_all_users(self) -> list[dict]:
        """Retorna todos os usuários do sistema"""
        try:
            logger.debug("Buscando todos os usuários")
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, empresa
                FROM usuarios
                ORDER BY nome
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'nome': row[1],
                    'email': row[2],
                    'tipo_acesso': row[3],
                    'empresa': row[4]
                })
                
            logger.debug(f"Encontrados {len(users)} usuários")
            return users
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()

    def get_all_engineers(self) -> list[dict]:
        """Retorna todos os engenheiros cadastrados no sistema"""
        try:
            logger.debug("Buscando todos os engenheiros")
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, empresa
                FROM usuarios
                WHERE tipo_acesso = 'engenheiro'
                ORDER BY nome
            """)
            
            engineers = []
            for row in cursor.fetchall():
                engineers.append({
                    'id': row[0],
                    'nome': row[1],
                    'email': row[2],
                    'empresa': row[3]
                })
                
            logger.debug(f"Encontrados {len(engineers)} engenheiros")
            return engineers
            
        except Exception as e:
            logger.error(f"Erro ao buscar engenheiros: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close() 