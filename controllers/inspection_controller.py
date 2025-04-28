from database.models import DatabaseModels
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InspectionController:
    def __init__(self):
        self.db_models = DatabaseModels()
        
    def criar_inspecao(self, equipamento_id: int, data: datetime, tipo: str,
                      engenheiro: int, resultado: str, recomendacoes: str) -> tuple[bool, str]:
        """Cria uma nova inspeção no sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO inspecoes (equipamento_id, data, tipo, engenheiro_id,
                                     resultado, recomendacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (equipamento_id, data, tipo, engenheiro, resultado, recomendacoes))
            
            conn.commit()
            return True, "Inspeção criada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            return False, f"Erro ao criar inspeção: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_inspections(self) -> list[dict]:
        """Retorna todas as inspeções do sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, e.tipo as equipamento, i.data, i.tipo, 
                       u.nome as engenheiro, i.resultado, i.recomendacoes
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                ORDER BY i.data DESC
            """)
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento': row[1],
                    'data': row[2],
                    'tipo': row[3],
                    'engenheiro': row[4],
                    'resultado': row[5],
                    'recomendacoes': row[6]
                })
                
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_inspections_by_engineer(self, engineer_id: int) -> list[dict]:
        """Retorna as inspeções realizadas por um engenheiro"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, e.tipo as equipamento, i.data, i.tipo, 
                       e.empresa as cliente, i.resultado
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                WHERE i.engenheiro_id = ?
                ORDER BY i.data DESC
            """, (engineer_id,))
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento': row[1],
                    'data': row[2],
                    'tipo': row[3],
                    'cliente': row[4],
                    'resultado': row[5]
                })
                
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções do engenheiro {engineer_id}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_inspections_by_company(self, company: str) -> list[dict]:
        """Retorna as inspeções dos equipamentos de uma empresa"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, e.tipo as equipamento, i.data, i.tipo, 
                       u.nome as engenheiro, i.resultado
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                WHERE e.empresa = ?
                ORDER BY i.data DESC
            """, (company,))
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento': row[1],
                    'data': row[2],
                    'tipo': row[3],
                    'engenheiro': row[4],
                    'resultado': row[5]
                })
                
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções da empresa {company}: {str(e)}")
            return []
            
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