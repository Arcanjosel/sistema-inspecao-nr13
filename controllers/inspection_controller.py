from database.models import DatabaseModels
import logging
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

class InspectionController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando InspectionController")
        self.db_models = db_models
        
    def criar_inspecao(self, equipamento_id: int, engenheiro_id: int, 
                      data_inspecao: str, tipo_inspecao: str,
                      resultado: str = None, recomendacoes: str = None) -> tuple[bool, str]:
        """Cria uma nova inspeção no sistema"""
        try:
            logger.debug(f"Criando inspeção para equipamento {equipamento_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Converte a data para o formato correto do SQL Server
            if isinstance(data_inspecao, str):
                try:
                    data_obj = datetime.strptime(data_inspecao, "%Y-%m-%d")
                except ValueError:
                    try:
                        data_obj = datetime.strptime(data_inspecao, "%d/%m/%Y")
                    except ValueError:
                        return False, "Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY"
            else:
                # Se já é um objeto date, converte para datetime
                data_obj = datetime.combine(data_inspecao, datetime.min.time())
            
            # Formata a data no estilo ISO que o SQL Server aceita
            data_formatada = data_obj.isoformat(timespec='seconds')
            
            # Define valores padrão para campos obrigatórios se não fornecidos
            resultado = resultado or "pendente"
            recomendacoes = recomendacoes or ""
            
            cursor.execute("""
                INSERT INTO inspecoes (equipamento_id, engenheiro_id, 
                                     data_inspecao, tipo_inspecao,
                                     resultado, recomendacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (equipamento_id, engenheiro_id, data_formatada, 
                 tipo_inspecao, resultado, recomendacoes))
            
            conn.commit()
            logger.info(f"Inspeção criada com sucesso para equipamento {equipamento_id}")
            return True, "Inspeção criada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao criar inspeção: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_inspections(self) -> list[dict]:
        """Retorna todas as inspeções do sistema"""
        try:
            logger.debug("Buscando todas as inspeções")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Query com INNER JOIN para pegar informações relacionadas
            cursor.execute("""
                SELECT 
                    i.id,
                    i.equipamento_id,
                    i.engenheiro_id,
                    i.data_inspecao,
                    i.tipo_inspecao,
                    i.resultado,
                    i.recomendacoes,
                    e.tag as equipamento_tag,
                    e.categoria as equipamento_categoria,
                    u.nome as engenheiro_nome
                FROM inspecoes i
                LEFT JOIN equipamentos e ON i.equipamento_id = e.id
                LEFT JOIN usuarios u ON i.engenheiro_id = u.id
                ORDER BY i.data_inspecao DESC
            """)
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'tipo': row[4],
                    'resultado': row[5],
                    'recomendacoes': row[6],
                    'equipamento_tag': row[7],
                    'equipamento_categoria': row[8],
                    'engenheiro_nome': row[9]
                })
                
            logger.debug(f"Encontradas {len(inspections)} inspeções")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_inspections_by_engineer(self, engineer_id: int) -> list[dict]:
        """Retorna as inspeções de um engenheiro específico"""
        try:
            logger.debug(f"Buscando inspeções do engenheiro {engineer_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, i.equipamento_id, i.engenheiro_id, 
                       i.data_inspecao, i.tipo_inspecao,
                       e.tag as equipamento_tag, e.categoria as equipamento_categoria,
                       u.nome as engenheiro_nome
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                WHERE i.engenheiro_id = ?
            """, (engineer_id,))
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'tipo': row[4],
                    'equipamento_tag': row[5],
                    'equipamento_categoria': row[6],
                    'engenheiro_nome': row[7]
                })
                
            logger.debug(f"Encontradas {len(inspections)} inspeções para o engenheiro {engineer_id}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções do engenheiro {engineer_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_inspections_by_company(self, company: str) -> list[dict]:
        """Retorna as inspeções de uma empresa específica"""
        try:
            logger.debug(f"Buscando inspeções da empresa {company}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, i.equipamento_id, i.engenheiro_id, 
                       i.data_inspecao, i.tipo_inspecao,
                       e.tag as equipamento_tag, e.categoria as equipamento_categoria,
                       u.nome as engenheiro_nome
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                WHERE e.empresa_id = ?
            """, (company,))
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'tipo': row[4],
                    'equipamento_tag': row[5],
                    'equipamento_categoria': row[6],
                    'engenheiro_nome': row[7]
                })
                
            logger.debug(f"Encontradas {len(inspections)} inspeções para a empresa {company}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções da empresa {company}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def update_inspection(self, inspection_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de uma inspeção"""
        try:
            logger.debug(f"Atualizando inspeção {inspection_id}")
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
                
            values.append(inspection_id)
            
            cursor.execute(f"""
                UPDATE inspecoes
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            logger.info(f"Inspeção {inspection_id} atualizada com sucesso")
            return True, "Inspeção atualizada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar inspeção {inspection_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao atualizar inspeção: {str(e)}"
            
        finally:
            cursor.close()
            
    def cancel_inspection(self, inspection_id: int) -> tuple[bool, str]:
        """Cancela uma inspeção"""
        try:
            logger.debug(f"Cancelando inspeção {inspection_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inspecoes
                SET status = 'cancelada'
                WHERE id = ?
            """, (inspection_id,))
            
            conn.commit()
            logger.info(f"Inspeção {inspection_id} cancelada com sucesso")
            return True, "Inspeção cancelada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao cancelar inspeção {inspection_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao cancelar inspeção: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_available_equipment(self) -> list[dict]:
        """Retorna os equipamentos disponíveis para inspeção"""
        try:
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
                
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos disponíveis: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_equipment_by_company(self, company: str) -> list[dict]:
        """Retorna os equipamentos de uma empresa específica"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tipo, empresa, localizacao, codigo_projeto, 
                       pressao_maxima, temperatura_maxima, status
                FROM equipamentos
                WHERE empresa = ? AND status = 'ativo'
            """, (company,))
            
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
                
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos da empresa {company}: {str(e)}")
            return []
            
        finally:
            cursor.close() 