"""
Controlador responsável pela autenticação e gerenciamento de usuários.
"""
import bcrypt
import logging
from typing import Optional
from database.connection import DatabaseConnection
from database.models import Usuario

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
        
    def login(self, email: str, password: str) -> Optional[Usuario]:
        """
        Realiza o login do usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Usuario: Objeto do usuário se autenticação bem sucedida
            None: Se autenticação falhar
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ? AND ativo = 1",
                (email,)
            )
            user_data = cursor.fetchone()
            
            if user_data and self._check_password(password, user_data.senha_hash):
                return Usuario(
                    id=user_data.id,
                    nome=user_data.nome,
                    email=user_data.email,
                    senha_hash=user_data.senha_hash,
                    tipo=user_data.tipo,
                    empresa=user_data.empresa,
                    ativo=user_data.ativo
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao realizar login: {str(e)}")
            raise
            
        finally:
            cursor.close()
            
    def criar_usuario(self, nome: str, email: str, senha: str, tipo: str, empresa: Optional[str] = None) -> bool:
        """
        Cria um novo usuário no sistema.
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            senha: Senha do usuário
            tipo: Tipo do usuário ('admin' ou 'cliente')
            empresa: Nome da empresa (opcional)
            
        Returns:
            bool: True se usuário criado com sucesso
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            senha_hash = self._hash_password(senha)
            
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, tipo, empresa)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nome, email, senha_hash, tipo, empresa)
            )
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            
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