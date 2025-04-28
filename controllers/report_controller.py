from database.models import DatabaseModels
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportController:
    def __init__(self):
        self.db_models = DatabaseModels()
        
    def criar_relatorio(self, inspecao_id: int, data: datetime, 
                       arquivo: str, observacoes: str) -> tuple[bool, str]:
        """Cria um novo relatório no sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO relatorios (inspecao_id, data, arquivo, observacoes)
                VALUES (?, ?, ?, ?)
            """, (inspecao_id, data, arquivo, observacoes))
            
            conn.commit()
            return True, "Relatório criado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar relatório: {str(e)}")
            return False, f"Erro ao criar relatório: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_reports(self) -> list[dict]:
        """Retorna todos os relatórios do sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, i.id as inspecao_id, r.data, r.arquivo, r.observacoes
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                ORDER BY r.data DESC
            """)
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'data': row[2],
                    'arquivo': row[3],
                    'observacoes': row[4]
                })
                
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_reports_by_engineer(self, engineer_id: int) -> list[dict]:
        """Retorna os relatórios das inspeções de um engenheiro"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, i.id as inspecao_id, r.data, r.arquivo
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                WHERE i.engenheiro_id = ?
                ORDER BY r.data DESC
            """, (engineer_id,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'data': row[2],
                    'arquivo': row[3]
                })
                
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios do engenheiro {engineer_id}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_reports_by_company(self, company: str) -> list[dict]:
        """Retorna os relatórios das inspeções de uma empresa"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, i.id as inspecao_id, r.data, r.arquivo
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                JOIN equipamentos e ON i.equipamento_id = e.id
                WHERE e.empresa = ?
                ORDER BY r.data DESC
            """, (company,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'data': row[2],
                    'arquivo': row[3]
                })
                
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios da empresa {company}: {str(e)}")
            return []
            
        finally:
            cursor.close()
            
    def get_report_by_id(self, report_id: int) -> dict:
        """Retorna um relatório específico pelo ID"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, i.id as inspecao_id, r.data, r.arquivo, r.observacoes
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                WHERE r.id = ?
            """, (report_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'inspecao_id': row[1],
                    'data': row[2],
                    'arquivo': row[3],
                    'observacoes': row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatório {report_id}: {str(e)}")
            return None
            
        finally:
            cursor.close()
            
    def update_report(self, report_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de um relatório"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                    
            if not update_fields:
                return False, "Nenhum campo para atualizar"
                
            values.append(report_id)
            
            cursor.execute(f"""
                UPDATE relatorios
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            return True, "Relatório atualizado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar relatório: {str(e)}")
            return False, f"Erro ao atualizar relatório: {str(e)}"
            
        finally:
            cursor.close()
            
    def delete_report(self, report_id: int) -> tuple[bool, str]:
        """Remove um relatório do sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM relatorios
                WHERE id = ?
            """, (report_id,))
            
            conn.commit()
            return True, "Relatório removido com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao remover relatório: {str(e)}")
            return False, f"Erro ao remover relatório: {str(e)}"
            
        finally:
            cursor.close() 