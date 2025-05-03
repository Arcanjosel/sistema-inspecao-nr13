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
        self.connection = None
        self._ensure_connection()
        
    def _ensure_connection(self):
        """Garante que a conexão com o banco de dados está ativa"""
        try:
            if self.connection is None or self.connection.closed:
                self.connection = self.db.get_connection()
                logger.debug("Nova conexão com o banco de dados estabelecida")
            # Teste simples para verificar se a conexão está ativa
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            logger.debug("Conexão com o banco de dados está ativa")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {str(e)}")
            # Tenta reconectar
            try:
                self.connection = self.db.get_connection()
                logger.debug("Reconexão com o banco de dados estabelecida")
                return True
            except Exception as e2:
                logger.error(f"Falha ao reconectar: {str(e2)}")
                return False
                
    def force_sync(self):
        """Força a sincronização com o banco de dados"""
        try:
            if self._ensure_connection():
                # Forçar commit de quaisquer transações pendentes
                self.connection.commit()
                logger.debug("Sincronização forçada com o banco de dados realizada com sucesso")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao forçar sincronização: {str(e)}")
            return False
        
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
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
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
            if 'cursor' in locals():
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
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
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
            
            # Força a sincronização
            self.force_sync()
            
            return True, "Usuário criado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao criar usuário: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def atualizar_usuario(self, user_id: int, nome: str, email: str, tipo_acesso: str, empresa: Optional[str] = None, senha: Optional[str] = None) -> Tuple[bool, str]:
        """
        Atualiza os dados de um usuário existente.
        
        Args:
            user_id: ID do usuário a ser atualizado
            nome: Novo nome do usuário
            email: Novo email do usuário
            tipo_acesso: Novo tipo de acesso ('admin', 'cliente', 'eng')
            empresa: Nome da empresa (opcional)
            senha: Nova senha (opcional, atualizada apenas se fornecida)
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
            cursor = conn.cursor()
            
            # Verifica se o email já existe para outro usuário
            cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                return False, "Email já está sendo usado por outro usuário"
            
            # Constrói a query de atualização
            update_fields = []
            params = []
            
            # Sempre atualiza esses campos
            update_fields.append("nome = ?")
            params.append(nome)
            
            update_fields.append("email = ?")
            params.append(email)
            
            update_fields.append("tipo_acesso = ?")
            params.append(tipo_acesso)
            
            update_fields.append("empresa = ?")
            params.append(empresa)
            
            # Atualiza a senha apenas se fornecida
            if senha:
                senha_hash = self._hash_password(senha)
                update_fields.append("senha_hash = ?")
                params.append(senha_hash)
            
            # Adiciona o ID do usuário como último parâmetro
            params.append(user_id)
            
            # Constrói e executa a query
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            # Verifica se algum registro foi atualizado
            if cursor.rowcount == 0:
                return False, "Nenhum usuário foi atualizado"
            
            # Força a sincronização
            self.force_sync()
            
            return True, "Usuário atualizado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar usuário: {str(e)}"
            
        finally:
            if 'cursor' in locals():
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
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
            cursor = conn.cursor()
            
            nova_senha_hash = self._hash_password(nova_senha)
            
            cursor.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
                (nova_senha_hash, email)
            )
            
            # Força a sincronização
            self.force_sync()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            return False
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def desativar_usuario(self, user_id: int) -> bool:
        """
        Desativa um usuário no sistema.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se usuário desativado com sucesso
        """
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE usuarios SET ativo = 0 WHERE id = ?",
                (user_id,)
            )
            
            # Força a sincronização
            self.force_sync()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desativar usuário: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            return False
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def reativar_usuario(self, user_id: int) -> bool:
        """
        Reativa um usuário no sistema.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se usuário reativado com sucesso
        """
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE usuarios SET ativo = 1 WHERE id = ?",
                (user_id,)
            )
            
            # Força a sincronização
            self.force_sync()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reativar usuário: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            return False
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_all_users(self) -> list[dict]:
        """Retorna todos os usuários do sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug("Buscando todos os usuários")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, empresa, ativo
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
                    'empresa': row[4],
                    'ativo': bool(row[5])
                })
                
            logger.debug(f"Encontrados {len(users)} usuários")
            return users
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            if 'cursor' in locals():
                cursor.close()

    def get_all_engineers(self) -> list[dict]:
        """Retorna todos os engenheiros cadastrados no sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug("Buscando todos os engenheiros")
            conn = self.connection
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
            if 'cursor' in locals():
                cursor.close()

    def get_engineers(self):
        """Retorna todos os usuários com perfil de engenheiro"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug("Buscando todos os engenheiros")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, ativo
                FROM usuarios
                WHERE tipo_acesso = 'eng' AND ativo = 1
                ORDER BY nome
            """)
            
            engineers = []
            for row in cursor.fetchall():
                engineers.append({
                    'id': row[0],
                    'nome': row[1],
                    'email': row[2],
                    'tipo_acesso': row[3],
                    'ativo': row[4]
                })
                
            logger.debug(f"Encontrados {len(engineers)} engenheiros")
            return engineers
            
        except Exception as e:
            logger.error(f"Erro ao buscar engenheiros: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            if 'cursor' in locals():
                cursor.close()

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Retorna os dados de um usuário específico pelo ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Optional[dict]: Dados do usuário ou None se não encontrado
        """
        if not user_id:
            logger.warning("ID do usuário não fornecido")
            return None
            
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Buscando usuário com ID {user_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, empresa, ativo
                FROM usuarios
                WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhum usuário encontrado com ID {user_id}")
                return None
                
            # Criar dicionário com os dados do usuário
            user = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'tipo_acesso': row[3],
                'empresa': row[4],
                'ativo': bool(row[5])
            }
            
            logger.debug(f"Usuário {user_id} encontrado: {user['nome']}")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
        finally:
            if 'cursor' in locals():
                cursor.close()

    def get_companies(self) -> list[dict]:
        """Retorna uma lista de todos os usuários marcados como cliente (empresa)."""
        try:
            self._ensure_connection()
            logger.debug("Buscando todas as empresas (usuários tipo 'cliente')")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, empresa 
                FROM usuarios 
                WHERE tipo_acesso = 'cliente' AND ativo = 1 
                ORDER BY nome
            """)
            
            empresas = []
            for row in cursor.fetchall():
                # Usar o campo 'empresa' se existir, senão usar 'nome'
                nome_empresa = row[2] if row[2] else row[1]
                if not nome_empresa:
                    nome_empresa = f"Cliente ID {row[0]}" # Fallback
                    
                empresas.append({
                    'id': row[0], # O ID do usuário cliente é o ID da empresa
                    'nome': nome_empresa
                })
                
            logger.debug(f"Encontradas {len(empresas)} empresas (clientes)")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas: {str(e)}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if 'cursor' in locals():
                cursor.close() 
                
    def get_company_id_by_name(self, company_name: str) -> Optional[int]:
        """
        Retorna o ID da empresa com base no nome.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Optional[int]: ID da empresa ou None se não encontrada
        """
        if not company_name:
            logger.warning("Nome da empresa não fornecido")
            return None
            
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Buscando empresa com nome {company_name}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Tentar encontrar pelo campo 'empresa' primeiro
            cursor.execute("""
                SELECT TOP 1 id FROM usuarios 
                WHERE (empresa = ? OR nome = ?) AND tipo_acesso = 'cliente' AND ativo = 1
            """, (company_name, company_name))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhuma empresa encontrada com o nome {company_name}")
                return None
                
            logger.debug(f"Empresa {company_name} encontrada com ID {row[0]}")
            return row[0]
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresa {company_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
        finally:
            if 'cursor' in locals():
                cursor.close()
                
    def get_company_by_id(self, company_id: int) -> Optional[dict]:
        """
        Retorna os dados de uma empresa específica pelo ID.
        
        Args:
            company_id: ID da empresa (ID do usuário cliente)
            
        Returns:
            Optional[dict]: Dados da empresa ou None se não encontrada
        """
        if not company_id:
            logger.warning("ID da empresa não fornecido")
            return None
            
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Buscando empresa com ID {company_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, empresa, email 
                FROM usuarios 
                WHERE id = ? AND tipo_acesso = 'cliente'
            """, (company_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhuma empresa encontrada com ID {company_id}")
                return None
                
            # Criar dicionário com os dados da empresa
            company = {
                'id': row[0],
                'nome': row[2] if row[2] else row[1],  # Prefere o campo 'empresa' se existir
                'email': row[3]
            }
            
            logger.debug(f"Empresa ID {company_id} encontrada: {company['nome']}")
            return company
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresa ID {company_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
        finally:
            if 'cursor' in locals():
                cursor.close() 