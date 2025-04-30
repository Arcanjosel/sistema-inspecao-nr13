import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class InspecaoModel:
    def __init__(self, db_models):
        self.db_models = db_models
        self.table = 'inspecoes'
        logger.debug("InspecaoModel inicializado")

    def create(self, equipamento_id, engenheiro_id, data_inspecao, tipo_inspecao, 
              resultado, recomendacoes=""):
        """Cria uma nova inspeção no banco de dados"""
        try:
            logger.debug(f"Criando nova inspeção para equipamento {equipamento_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO inspecoes (
                    equipamento_id, 
                    engenheiro_id, 
                    data_inspecao, 
                    tipo_inspecao, 
                    resultado, 
                    recomendacoes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                equipamento_id, 
                engenheiro_id, 
                data_inspecao, 
                tipo_inspecao, 
                resultado, 
                recomendacoes
            ))
            
            conn.commit()
            logger.info(f"Inspeção criada com sucesso, ID: {cursor.lastrowid}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            
    def update(self, id, equipamento_id, engenheiro_id, data_inspecao, 
              tipo_inspecao, resultado, recomendacoes=""):
        """Atualiza uma inspeção existente"""
        try:
            logger.debug(f"Atualizando inspeção {id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inspecoes 
                SET 
                    equipamento_id = ?, 
                    engenheiro_id = ?, 
                    data_inspecao = ?, 
                    tipo_inspecao = ?, 
                    resultado = ?, 
                    recomendacoes = ?
                WHERE id = ?
            """, (
                equipamento_id, 
                engenheiro_id, 
                data_inspecao, 
                tipo_inspecao, 
                resultado, 
                recomendacoes,
                id
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Inspeção {id} atualizada com sucesso")
                return True
            else:
                logger.warning(f"Nenhuma inspeção encontrada com ID {id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            
    def delete(self, id):
        """Exclui uma inspeção pelo ID"""
        try:
            logger.debug(f"Excluindo inspeção {id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM inspecoes WHERE id = ?", (id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Inspeção {id} excluída com sucesso")
                return True
            else:
                logger.warning(f"Nenhuma inspeção encontrada com ID {id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao excluir inspeção: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            
    def get_all(self):
        """Retorna todas as inspeções com informações relacionadas"""
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
            
    def get_by_id(self, id):
        """Retorna uma inspeção específica pelo ID"""
        try:
            logger.debug(f"Buscando inspeção com ID {id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.id = ?
            """, (id,))
            
            row = cursor.fetchone()
            if row:
                inspection = {
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
                }
                logger.debug(f"Inspeção {id} encontrada")
                return inspection
            else:
                logger.warning(f"Nenhuma inspeção encontrada com ID {id}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar inspeção {id}: {str(e)}")
            return None
            
        finally:
            cursor.close()
            
    def get_by_equipment(self, equipment_id):
        """Retorna todas as inspeções de um equipamento específico"""
        try:
            logger.debug(f"Buscando inspeções do equipamento {equipment_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.equipamento_id = ?
                ORDER BY i.data_inspecao DESC
            """, (equipment_id,))
            
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
                
            logger.debug(f"Encontradas {len(inspections)} inspeções para o equipamento {equipment_id}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções do equipamento {equipment_id}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_by_engineer(self, engineer_id):
        """Retorna todas as inspeções realizadas por um engenheiro específico"""
        try:
            logger.debug(f"Buscando inspeções do engenheiro {engineer_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.engenheiro_id = ?
                ORDER BY i.data_inspecao DESC
            """, (engineer_id,))
            
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
                
            logger.debug(f"Encontradas {len(inspections)} inspeções para o engenheiro {engineer_id}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções do engenheiro {engineer_id}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_by_date_range(self, start_date, end_date):
        """Retorna todas as inspeções dentro de um intervalo de datas"""
        try:
            logger.debug(f"Buscando inspeções entre {start_date} e {end_date}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.data_inspecao BETWEEN ? AND ?
                ORDER BY i.data_inspecao DESC
            """, (start_date, end_date))
            
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
                
            logger.debug(f"Encontradas {len(inspections)} inspeções no intervalo de datas")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções no intervalo de datas: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_by_type(self, inspection_type):
        """Retorna todas as inspeções de um tipo específico"""
        try:
            logger.debug(f"Buscando inspeções do tipo {inspection_type}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.tipo_inspecao = ?
                ORDER BY i.data_inspecao DESC
            """, (inspection_type,))
            
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
                
            logger.debug(f"Encontradas {len(inspections)} inspeções do tipo {inspection_type}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções do tipo {inspection_type}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_by_result(self, result):
        """Retorna todas as inspeções com um resultado específico"""
        try:
            logger.debug(f"Buscando inspeções com resultado {result}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
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
                WHERE i.resultado = ?
                ORDER BY i.data_inspecao DESC
            """, (result,))
            
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
                
            logger.debug(f"Encontradas {len(inspections)} inspeções com resultado {result}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções com resultado {result}: {str(e)}")
            return []
            
        finally:
            cursor.close() 