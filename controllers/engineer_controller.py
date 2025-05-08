#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador para gerenciamento de engenheiros
"""

import logging
import traceback
from database.models import DatabaseModels

logger = logging.getLogger(__name__)

class EngineerController:
    """Controlador para operações relacionadas aos engenheiros"""
    
    def __init__(self, db_models=None):
        """Inicializa o controlador"""
        self.db_models = db_models or DatabaseModels()
        
    def get_all_engineers(self):
        """Retorna todos os engenheiros cadastrados"""
        try:
            logger.debug("Buscando todos os engenheiros")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Busca apenas usuários com tipo_acesso = 'engenheiro'
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, empresa, ativo, crea
                FROM usuarios
                WHERE tipo_acesso = 'engenheiro' OR tipo_acesso = 'admin'
                ORDER BY nome
            """)
            
            columns = [column[0] for column in cursor.description]
            engineers = []
            
            for row in cursor.fetchall():
                engineers.append(dict(zip(columns, row)))
                
            logger.debug(f"Encontrados {len(engineers)} engenheiros")
            return engineers
            
        except Exception as e:
            logger.error(f"Erro ao buscar engenheiros: {str(e)}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_engineer_by_id(self, engineer_id):
        """Retorna um engenheiro pelo seu ID"""
        try:
            logger.debug(f"Buscando engenheiro com ID: {engineer_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, tipo_acesso, empresa, ativo, crea
                FROM usuarios
                WHERE id = ?
            """, (engineer_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Engenheiro com ID {engineer_id} não encontrado")
                return None
                
            columns = [column[0] for column in cursor.description]
            engineer = dict(zip(columns, row))
            
            logger.debug(f"Engenheiro encontrado: {engineer['nome']}")
            return engineer
            
        except Exception as e:
            logger.error(f"Erro ao buscar engenheiro por ID: {str(e)}")
            logger.error(traceback.format_exc())
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def create_engineer(self, engineer_data):
        """Cria um novo engenheiro no sistema"""
        try:
            logger.debug(f"Criando novo engenheiro: {engineer_data.get('nome')}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Verifica se o email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (engineer_data.get('email'),))
            if cursor.fetchone():
                logger.warning(f"Email já cadastrado: {engineer_data.get('email')}")
                return False, "Email já cadastrado no sistema."
            
            # Insere o novo engenheiro
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, tipo_acesso, empresa, crea, ativo)
                VALUES (?, ?, ?, 'engenheiro', ?, ?, 1)
            """, (
                engineer_data.get('nome'),
                engineer_data.get('email'),
                engineer_data.get('senha_hash'),
                engineer_data.get('empresa'),
                engineer_data.get('crea')
            ))
            
            conn.commit()
            logger.info(f"Engenheiro criado com sucesso: {engineer_data.get('nome')}")
            return True, "Engenheiro cadastrado com sucesso!"
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao criar engenheiro: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def update_engineer(self, engineer_id, engineer_data):
        """Atualiza os dados de um engenheiro existente"""
        try:
            logger.debug(f"Atualizando engenheiro ID {engineer_id}: {engineer_data.get('nome')}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Verifica se o engenheiro existe
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (engineer_id,))
            if not cursor.fetchone():
                logger.warning(f"Engenheiro não encontrado: {engineer_id}")
                return False, "Engenheiro não encontrado."
            
            # Verifica se o email está disponível (se foi alterado)
            if 'email' in engineer_data:
                cursor.execute("""
                    SELECT id FROM usuarios 
                    WHERE email = ? AND id != ?
                """, (engineer_data.get('email'), engineer_id))
                
                if cursor.fetchone():
                    logger.warning(f"Email já em uso: {engineer_data.get('email')}")
                    return False, "Este email já está em uso por outro usuário."
            
            # Monta a query de atualização
            update_fields = []
            params = []
            
            if 'nome' in engineer_data:
                update_fields.append("nome = ?")
                params.append(engineer_data['nome'])
                
            if 'email' in engineer_data:
                update_fields.append("email = ?")
                params.append(engineer_data['email'])
                
            if 'empresa' in engineer_data:
                update_fields.append("empresa = ?")
                params.append(engineer_data['empresa'])
                
            if 'crea' in engineer_data:
                update_fields.append("crea = ?")
                params.append(engineer_data['crea'])
                
            if 'ativo' in engineer_data:
                update_fields.append("ativo = ?")
                params.append(1 if engineer_data['ativo'] else 0)
                
            if 'senha_hash' in engineer_data:
                update_fields.append("senha_hash = ?")
                params.append(engineer_data['senha_hash'])
            
            if not update_fields:
                logger.warning("Nenhum campo para atualizar")
                return False, "Nenhum campo para atualizar."
            
            # Adiciona o ID ao final dos parâmetros
            params.append(engineer_id)
            
            # Executa a atualização
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            logger.info(f"Engenheiro atualizado com sucesso: ID {engineer_id}")
            return True, "Engenheiro atualizado com sucesso!"
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao atualizar engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao atualizar engenheiro: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def delete_engineer(self, engineer_id):
        """Remove um engenheiro do sistema"""
        try:
            logger.debug(f"Removendo engenheiro ID: {engineer_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Verifica se o engenheiro existe
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (engineer_id,))
            if not cursor.fetchone():
                logger.warning(f"Engenheiro não encontrado: {engineer_id}")
                return False, "Engenheiro não encontrado."
            
            # Verifica se há inspeções associadas a este engenheiro
            cursor.execute("SELECT COUNT(*) FROM inspecoes WHERE engenheiro_id = ?", (engineer_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.warning(f"Não é possível excluir engenheiro com inspeções: {engineer_id}")
                return False, f"Não é possível excluir este engenheiro pois ele está associado a {count} inspeções."
            
            # Executa a exclusão
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (engineer_id,))
            
            conn.commit()
            logger.info(f"Engenheiro removido com sucesso: ID {engineer_id}")
            return True, "Engenheiro removido com sucesso!"
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao remover engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao remover engenheiro: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close() 