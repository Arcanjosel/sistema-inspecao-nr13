from database.models import DatabaseModels
import logging
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

class ReportController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando ReportController")
        self.db_models = db_models
        
    def criar_relatorio(self, inspecao_id: int, data_emissao: str, 
                      link_arquivo: str, observacoes: str = None) -> tuple[bool, str]:
        """Cria um novo relatório no sistema"""
        try:
            logger.debug(f"Criando relatório para inspeção {inspecao_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Verifica se a inspeção existe
            cursor.execute("SELECT id FROM inspecoes WHERE id = ?", (inspecao_id,))
            if not cursor.fetchone():
                return False, "Inspeção não encontrada"
                
            # Converte a data para datetime se for string
            if isinstance(data_emissao, str):
                try:
                    data_obj = datetime.strptime(data_emissao, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
                    except ValueError:
                        return False, "Formato de data inválido. Use YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD"
            else:
                data_obj = data_emissao
                
            # Formata a data como string simples YYYY-MM-DD
            data_formatada = data_obj.strftime('%Y-%m-%d')
            
            # Insere o relatório sem usar CONVERT no SQL
            cursor.execute("""
                INSERT INTO relatorios (inspecao_id, data_emissao, link_arquivo, observacoes)
                VALUES (?, ?, ?, ?)
            """, (inspecao_id, data_formatada, link_arquivo, observacoes))
            
            conn.commit()
            logger.info(f"Relatório criado com sucesso para inspeção {inspecao_id}")
            return True, "Relatório criado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao criar relatório: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_reports(self) -> list[dict]:
        """Retorna todos os relatórios do sistema"""
        try:
            logger.debug("Buscando todos os relatórios")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    r.id,
                    r.inspecao_id,
                    r.data_emissao,
                    r.link_arquivo,
                    r.observacoes,
                    i.tipo_inspecao,
                    i.resultado as inspecao_resultado,
                    e.tag as equipamento_tag,
                    e.categoria as equipamento_categoria,
                    u.nome as engenheiro_nome
                FROM dbo.relatorios r
                JOIN dbo.inspecoes i ON r.inspecao_id = i.id
                JOIN dbo.equipamentos e ON i.equipamento_id = e.id
                JOIN dbo.usuarios u ON i.engenheiro_id = u.id
                ORDER BY r.data_emissao DESC
            """
            
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
                logger.debug(f"Relatório {row[0]}: {dict(zip(columns, row))}")
            
            logger.debug(f"Encontrados {len(result)} relatórios")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_reports_by_engineer(self, engineer_id: int) -> list[dict]:
        """Retorna os relatórios de um engenheiro específico"""
        try:
            logger.debug(f"Buscando relatórios do engenheiro {engineer_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, r.inspecao_id, r.engenheiro_responsavel, 
                       r.data_emissao, r.link_arquivo,
                       i.equipamento_id, i.tipo_inspecao,
                       e.tipo as equipamento_tipo, e.empresa as equipamento_empresa,
                       u.nome as engenheiro_nome
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON r.engenheiro_responsavel = u.id
                WHERE r.engenheiro_responsavel = ?
            """, (engineer_id,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'arquivo': row[4],
                    'equipamento_id': row[5],
                    'tipo_inspecao': row[6],
                    'equipamento_tipo': row[7],
                    'equipamento_empresa': row[8],
                    'engenheiro_nome': row[9]
                })
                
            logger.debug(f"Encontrados {len(reports)} relatórios para o engenheiro {engineer_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios do engenheiro {engineer_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_reports_by_company(self, company: str) -> list[dict]:
        """Retorna os relatórios de uma empresa específica"""
        try:
            logger.debug(f"Buscando relatórios da empresa {company}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, r.inspecao_id, r.engenheiro_responsavel, 
                       r.data_emissao, r.link_arquivo,
                       i.equipamento_id, i.tipo_inspecao,
                       e.tipo as equipamento_tipo, e.empresa as equipamento_empresa,
                       u.nome as engenheiro_nome
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON r.engenheiro_responsavel = u.id
                WHERE e.empresa = ?
            """, (company,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'arquivo': row[4],
                    'equipamento_id': row[5],
                    'tipo_inspecao': row[6],
                    'equipamento_tipo': row[7],
                    'equipamento_empresa': row[8],
                    'engenheiro_nome': row[9]
                })
                
            logger.debug(f"Encontrados {len(reports)} relatórios para a empresa {company}")
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios da empresa {company}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def get_report_by_id(self, report_id: int) -> dict:
        """Retorna um relatório específico pelo ID"""
        try:
            logger.debug(f"Buscando relatório {report_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    r.id,
                    r.inspecao_id,
                    r.data_emissao,
                    r.link_arquivo,
                    r.observacoes,
                    i.tipo_inspecao,
                    i.resultado as inspecao_resultado,
                    e.tag as equipamento_tag,
                    e.categoria as equipamento_categoria,
                    u.nome as engenheiro_nome
                FROM dbo.relatorios r
                JOIN dbo.inspecoes i ON r.inspecao_id = i.id
                JOIN dbo.equipamentos e ON i.equipamento_id = e.id
                JOIN dbo.usuarios u ON i.engenheiro_id = u.id
                WHERE r.id = ?
            """
            
            cursor.execute(query, (report_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
                logger.debug(f"Relatório {report_id}: {result}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatório {report_id}: {str(e)}")
            return None
            
        finally:
            cursor.close()
            
    def update_report(self, report_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de um relatório"""
        try:
            logger.debug(f"Atualizando relatório {report_id}")
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
                
            values.append(report_id)
            
            cursor.execute(f"""
                UPDATE relatorios
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            logger.info(f"Relatório {report_id} atualizado com sucesso")
            return True, "Relatório atualizado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar relatório {report_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao atualizar relatório: {str(e)}"
            
        finally:
            cursor.close()
            
    def delete_report(self, report_id: int) -> tuple[bool, str]:
        """Deleta um relatório"""
        try:
            logger.debug(f"Deletando relatório {report_id}")
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM relatorios
                WHERE id = ?
            """, (report_id,))
            
            conn.commit()
            logger.info(f"Relatório {report_id} deletado com sucesso")
            return True, "Relatório deletado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao deletar relatório {report_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao deletar relatório: {str(e)}"
            
        finally:
            cursor.close() 