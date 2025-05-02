from database.models import DatabaseModels
import logging
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

class ReportController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando ReportController")
        self.db_models = db_models
        self.connection = None
        self._ensure_connection()
        
    def _ensure_connection(self):
        """Garante que a conexão com o banco de dados está ativa"""
        try:
            if self.connection is None or self.connection.closed:
                self.connection = self.db_models.db.get_connection()
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
                self.connection = self.db_models.db.get_connection()
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
            
    def criar_relatorio(self, inspecao_id: int, data_emissao: str, 
                      link_arquivo: str, observacoes: str = None) -> tuple[bool, str]:
        """Cria um novo relatório no sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Criando relatório para inspeção {inspecao_id}")
            logger.debug(f"Parâmetros - data: {data_emissao}, arquivo: {link_arquivo}, obs: {observacoes}")
            
            conn = self.connection
            cursor = conn.cursor()
            
            # Verifica se a inspeção existe
            cursor.execute("SELECT id FROM inspecoes WHERE id = ?", (inspecao_id,))
            if not cursor.fetchone():
                logger.warning(f"Inspeção {inspecao_id} não encontrada")
                return False, "Inspeção não encontrada"
                
            # Converte a data para datetime se for string
            if isinstance(data_emissao, str):
                try:
                    # Se a data contém horas, minutos e segundos
                    if len(data_emissao) > 10:
                        try:
                            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            data_obj = datetime.strptime(data_emissao[:10], "%Y-%m-%d")
                    else:
                        data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
                except ValueError as e:
                    logger.error(f"Formato de data inválido: {data_emissao}")
                    logger.error(str(e))
                    return False, "Formato de data inválido. Use YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD"
            else:
                data_obj = data_emissao
                
            # Formata a data como string simples YYYY-MM-DD
            data_formatada = data_obj.strftime('%Y-%m-%d')
            logger.debug(f"Data formatada: {data_formatada}")
            
            # Verifica se já existe um relatório para esta inspeção
            cursor.execute("SELECT id FROM relatorios WHERE inspecao_id = ?", (inspecao_id,))
            existing_report = cursor.fetchone()
            
            if existing_report:
                logger.warning(f"Já existe um relatório para a inspeção {inspecao_id}")
                return False, f"Já existe um relatório para a inspeção {inspecao_id}"
            
            # Insere o relatório sem usar CONVERT no SQL
            insert_query = """
                INSERT INTO relatorios (inspecao_id, data_emissao, link_arquivo, observacoes)
                VALUES (?, ?, ?, ?)
            """
            
            values = (inspecao_id, data_formatada, link_arquivo, observacoes)
            logger.debug(f"Query: {insert_query}")
            logger.debug(f"Valores: {values}")
            
            cursor.execute(insert_query, values)
            
            # Verificar se a inserção foi bem-sucedida
            rows_affected = cursor.rowcount
            logger.debug(f"Linhas afetadas: {rows_affected}")
            
            if rows_affected == 0:
                logger.warning("Nenhuma linha inserida")
                conn.rollback()
                return False, "Falha ao inserir o relatório"
            
            # Obter o ID do relatório inserido
            cursor.execute("SELECT @@IDENTITY")
            report_id = cursor.fetchone()[0]
            logger.debug(f"ID do relatório inserido: {report_id}")
            
            # Forçar sincronização após a operação
            self.force_sync()
            
            return True, f"Relatório #{report_id} criado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao criar relatório: {str(e)}"
            
        finally:
            if 'cursor' in locals():
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
            
    def get_reports_by_company(self, company_id: int) -> list[dict]:
        """Retorna os relatórios de uma empresa específica"""
        try:
            logger.debug(f"Buscando relatórios da empresa ID: {company_id}")
            self._ensure_connection()
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, r.inspecao_id, 
                       r.data_emissao, r.link_arquivo, r.observacoes,
                       i.equipamento_id, i.tipo_inspecao, i.engenheiro_id,
                       e.tag as equipamento_tag, e.categoria as equipamento_categoria,
                       u.nome as engenheiro_nome
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                WHERE e.empresa_id = ?
            """, (company_id,))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'inspecao_id': row[1],
                    'data_emissao': row[2],
                    'link_arquivo': row[3],
                    'observacoes': row[4],
                    'equipamento_id': row[5],
                    'tipo_inspecao': row[6],
                    'engenheiro_id': row[7],
                    'equipamento_tag': row[8],
                    'equipamento_categoria': row[9],
                    'engenheiro_nome': row[10]
                })
                
            logger.debug(f"Encontrados {len(reports)} relatórios para a empresa ID: {company_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Erro ao buscar relatórios da empresa {company_id}: {str(e)}")
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
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Atualizando relatório {report_id} com parâmetros: {kwargs}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verifica se o relatório existe
            cursor.execute("SELECT id FROM relatorios WHERE id = ?", (report_id,))
            if not cursor.fetchone():
                logger.warning(f"Relatório {report_id} não encontrado")
                return False, f"Relatório {report_id} não encontrado"
            
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                    logger.debug(f"Campo a atualizar: {field} = {value}")
                    
            if not update_fields:
                logger.warning("Nenhum campo para atualizar")
                return False, "Nenhum campo para atualizar"
                
            values.append(report_id)
            
            update_query = f"""
                UPDATE relatorios
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            logger.debug(f"Query de atualização: {update_query}")
            logger.debug(f"Valores: {values}")
            
            cursor.execute(update_query, values)
            
            # Verifica se alguma linha foi afetada
            rows_affected = cursor.rowcount
            logger.debug(f"Linhas afetadas: {rows_affected}")
            
            if rows_affected == 0:
                logger.warning(f"Nenhuma linha afetada na atualização do relatório {report_id}")
                conn.rollback()
                return False, "Nenhuma alteração realizada"
            
            # Forçar sincronização após a operação
            self.force_sync()
            
            return True, "Relatório atualizado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar relatório {report_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar relatório: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def atualizar_relatorio(self, report_id: int, inspecao_id: int, data_emissao: str, 
                           link_arquivo: str, observacoes: str = None) -> bool:
        """
        Atualiza um relatório existente.
        Esta é uma função de compatibilidade que chama update_report com os parâmetros adequados.
        """
        try:
            if not report_id:
                logger.error("ID do relatório não fornecido")
                return False
            
            logger.debug(f"Atualizando relatório {report_id} via atualizar_relatorio")
            logger.debug(f"Parâmetros - inspecao_id: {inspecao_id}, data: {data_emissao}, arquivo: {link_arquivo}")
            
            # Validar a data
            try:
                if isinstance(data_emissao, str):
                    if len(data_emissao) > 10:
                        data_emissao = data_emissao[:10]  # Pega apenas YYYY-MM-DD
                    datetime.strptime(data_emissao, "%Y-%m-%d")  # Valida o formato
            except ValueError as e:
                logger.error(f"Formato de data inválido: {data_emissao}, erro: {str(e)}")
                return False
            
            # Prepara os dados para atualização
            params = {
                'inspecao_id': inspecao_id,
                'data_emissao': data_emissao,
                'link_arquivo': link_arquivo,
                'observacoes': observacoes
            }
            
            # Remove campos None ou vazios
            update_params = {k: v for k, v in params.items() if v is not None and v != ''}
            
            if not update_params:
                logger.warning("Nenhum parâmetro válido para atualização")
                return False
            
            logger.debug(f"Parâmetros de atualização: {update_params}")
            
            # Chama o método update_report
            success, message = self.update_report(report_id, **update_params)
            
            logger.debug(f"Resultado da atualização: {success}, {message}")
            return success
            
        except Exception as e:
            logger.error(f"Erro ao atualizar relatório {report_id} via atualizar_relatorio: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def excluir_relatorio(self, report_id: int) -> bool:
        """
        Exclui um relatório do sistema.
        Esta é uma função de compatibilidade que chama delete_report.
        """
        try:
            logger.debug(f"Excluindo relatório {report_id} via excluir_relatorio")
            success, message = self.delete_report(report_id)
            logger.debug(f"Resultado da exclusão: {success}, {message}")
            return success
        except Exception as e:
            logger.error(f"Erro ao excluir relatório {report_id} via excluir_relatorio: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def delete_report(self, report_id: int) -> tuple[bool, str]:
        """Deleta um relatório"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Deletando relatório {report_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM relatorios
                WHERE id = ?
            """, (report_id,))
            
            # Forçar sincronização após a operação
            self.force_sync()
            
            return True, "Relatório deletado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao deletar relatório {report_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao deletar relatório: {str(e)}"
            
        finally:
            cursor.close() 