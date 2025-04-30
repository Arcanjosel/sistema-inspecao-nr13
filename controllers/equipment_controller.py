from database.models import DatabaseModels
import logging
import traceback

logger = logging.getLogger(__name__)

class EquipmentController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando EquipmentController")
        self.db_models = db_models
        
    def criar_equipamento(self, tag: str, categoria: str, empresa_id: int,
                         fabricante: str, ano_fabricacao: int,
                         pressao_projeto: float, pressao_trabalho: float,
                         volume: float, fluido: str) -> tuple[bool, str]:
        """Cria um novo equipamento no sistema"""
        try:
            logger.debug(f"Criando equipamento com tag {tag}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO equipamentos (tag, categoria, empresa_id,
                                        fabricante, ano_fabricacao,
                                        pressao_projeto, pressao_trabalho,
                                        volume, fluido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tag, categoria, empresa_id, fabricante, ano_fabricacao,
                  pressao_projeto, pressao_trabalho, volume, fluido))
            
            conn.commit()
            logger.info(f"Equipamento {tag} criado com sucesso")
            return True, "Equipamento criado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar equipamento {tag}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao criar equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_equipment(self) -> list[dict]:
        """Retorna todos os equipamentos do sistema"""
        try:
            logger.debug("Buscando todos os equipamentos")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.id, e.tag, e.categoria, e.empresa_id,
                       e.fabricante, e.ano_fabricacao, e.pressao_projeto,
                       e.pressao_trabalho, e.volume, e.fluido, e.ativo,
                       u.nome as empresa_nome
                FROM equipamentos e
                LEFT JOIN usuarios u ON e.empresa_id = u.id
                ORDER BY e.tag
            """)
            
            equipment = []
            for row in cursor.fetchall():
                equipment.append({
                    'id': row[0],
                    'tag': row[1],
                    'categoria': row[2],
                    'empresa_id': row[3],
                    'fabricante': row[4],
                    'ano_fabricacao': row[5],
                    'pressao_projeto': row[6],
                    'pressao_trabalho': row[7],
                    'volume': row[8],
                    'fluido': row[9],
                    'ativo': bool(row[10]),
                    'empresa_nome': row[11] if row[11] else ''
                })
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_equipment_by_company(self, company_id: int) -> list[dict]:
        """Retorna os equipamentos de uma empresa específica"""
        try:
            logger.debug(f"Buscando equipamentos da empresa {company_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.id, e.tag, e.categoria, e.empresa_id,
                       e.fabricante, e.ano_fabricacao, e.pressao_projeto,
                       e.pressao_trabalho, e.volume, e.fluido,
                       u.nome as empresa_nome
                FROM equipamentos e
                JOIN usuarios u ON e.empresa_id = u.id
                WHERE e.empresa_id = ? AND e.ativo = 1
            """, (company_id,))
            
            equipment = []
            for row in cursor.fetchall():
                equipment.append({
                    'id': row[0],
                    'tag': row[1],
                    'categoria': row[2],
                    'empresa_id': row[3],
                    'fabricante': row[4],
                    'ano_fabricacao': row[5],
                    'pressao_projeto': row[6],
                    'pressao_trabalho': row[7],
                    'volume': row[8],
                    'fluido': row[9],
                    'empresa_nome': row[10]
                })
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos para a empresa {company_id}")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos da empresa {company_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_available_equipment(self) -> list[dict]:
        """Retorna os equipamentos disponíveis para inspeção"""
        try:
            logger.debug("Buscando equipamentos disponíveis para inspeção")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.id, e.tipo, e.empresa, e.localizacao, e.codigo_projeto,
                       e.pressao_maxima, e.temperatura_maxima, e.status
                FROM equipamentos e
                LEFT JOIN inspecoes i ON e.id = i.equipamento_id
                WHERE e.status = 'ativo'
                AND (i.id IS NULL OR i.data < DATEADD(month, -6, GETDATE()))
            """)
            
            equipment = []
            for row in cursor.fetchall():
                equipment.append({
                    'id': row[0],
                    'tipo': row[1],
                    'empresa': row[2],
                    'localizacao': row[3],
                    'codigo': row[4],
                    'pressao': row[5],
                    'temperatura': row[6],
                    'status': row[7]
                })
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos disponíveis")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos disponíveis: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def update_equipment(self, equipment_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de um equipamento"""
        try:
            logger.debug(f"Atualizando equipamento {equipment_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                    
            if not update_fields:
                logger.warning("Nenhum campo para atualizar")
                return False, "Nenhum campo para atualizar"
                
            values.append(equipment_id)
            
            cursor.execute(f"""
                UPDATE equipamentos
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            logger.info(f"Equipamento {equipment_id} atualizado com sucesso")
            return True, "Equipamento atualizado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao atualizar equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def delete_equipment(self, equipment_id: int) -> tuple[bool, str]:
        """Deleta um equipamento (soft delete)"""
        try:
            logger.debug(f"Deletando equipamento {equipment_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE equipamentos
                SET ativo = 0
                WHERE id = ?
            """, (equipment_id,))
            
            conn.commit()
            logger.info(f"Equipamento {equipment_id} deletado com sucesso")
            return True, "Equipamento deletado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao deletar equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao deletar equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_equipment_by_id(self, equipment_id):
        """Retorna os dados de um equipamento específico pelo ID"""
        if not equipment_id:
            logger.warning("ID do equipamento não fornecido")
            return None
            
        try:
            logger.debug(f"Buscando equipamento com ID {equipment_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tag, categoria, empresa_id, fabricante, ano_fabricacao,
                       pressao_projeto, pressao_trabalho, volume, fluido, ativo
                FROM equipamentos
                WHERE id = ?
            """, (equipment_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhum equipamento encontrado com ID {equipment_id}")
                return None
                
            # Criar dicionário com os dados do equipamento
            equipment = {
                'id': row[0],
                'tag': row[1],
                'categoria': row[2],
                'empresa_id': row[3],
                'fabricante': row[4],
                'ano_fabricacao': row[5],
                'pressao_projeto': row[6],
                'pressao_trabalho': row[7],
                'volume': row[8],
                'fluido': row[9],
                'ativo': row[10]
            }
            
            logger.debug(f"Equipamento {equipment_id} encontrado: {equipment['tag']}")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
        finally:
            cursor.close()
            
    def toggle_equipment_status(self, equipment_id, new_status) -> tuple[bool, str]:
        """
        Ativa ou desativa um equipamento
        
        Args:
            equipment_id: ID do equipamento a ser alterado
            new_status: Novo status (1 para ativo, 0 para inativo)
            
        Returns:
            tuple[bool, str]: Sucesso e mensagem
        """
        try:
            logger.debug(f"Alterando status do equipamento {equipment_id} para {new_status}")
            # Verifica se o equipamento existe
            equipment = self.get_equipment_by_id(equipment_id)
            if not equipment:
                logger.warning(f"Equipamento {equipment_id} não encontrado")
                return False, "Equipamento não encontrado."
            
            # Atualiza o status na tabela
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE equipamentos SET ativo = ? WHERE id = ?",
                (new_status, equipment_id)
            )
            
            conn.commit()
            
            status_text = "ativado" if new_status == 1 else "desativado"
            logger.info(f"Equipamento {equipment_id} {status_text} com sucesso")
            return True, f"Equipamento {status_text} com sucesso."
            
        except Exception as e:
            logger.error(f"Erro ao alterar status do equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao alterar status do equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_equipment_by_tag(self, tag):
        """
        Retorna os dados de um equipamento específico pelo tag
        
        Args:
            tag: Tag do equipamento
            
        Returns:
            dict or None: Dados do equipamento ou None se não encontrado
        """
        if not tag:
            logger.warning("Tag do equipamento não fornecido")
            return None
            
        try:
            logger.debug(f"Buscando equipamento com tag '{tag}'")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tag, categoria, empresa_id, fabricante, ano_fabricacao,
                       pressao_projeto, pressao_trabalho, volume, fluido, ativo
                FROM equipamentos
                WHERE tag = ?
            """, (tag,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhum equipamento encontrado com tag '{tag}'")
                return None
                
            # Criar dicionário com os dados do equipamento
            equipment = {
                'id': row[0],
                'tag': row[1],
                'categoria': row[2],
                'empresa_id': row[3],
                'fabricante': row[4],
                'ano_fabricacao': row[5],
                'pressao_projeto': row[6],
                'pressao_trabalho': row[7],
                'volume': row[8],
                'fluido': row[9],
                'ativo': row[10]
            }
            
            logger.debug(f"Equipamento com tag '{tag}' encontrado: ID={equipment['id']}")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamento com tag '{tag}': {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
        finally:
            cursor.close() 