from database.models import DatabaseModels
import logging
from datetime import datetime, timedelta
import traceback
from db.models import InspecaoModel
import sqlite3

logger = logging.getLogger(__name__)

class InspectionController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando InspectionController")
        self.db_models = db_models
        self.model = InspecaoModel(db_models)
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
        
    def criar_inspecao(self, equipamento_id: int, engenheiro_id: int, 
                      data_inspecao: str, tipo_inspecao: str,
                      resultado: str = None, recomendacoes: str = None) -> tuple[bool, str]:
        """Cria uma nova inspeção no sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Criando inspeção para equipamento {equipamento_id}")
            logger.debug(f"Parâmetros - engenheiro: {engenheiro_id}, data: {data_inspecao}, tipo: {tipo_inspecao}")
            
            conn = self.connection
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
            resultado = resultado or "Pendente"
            recomendacoes = recomendacoes or ""
            
            # Calcula a próxima inspeção (6 meses após a data atual)
            proxima_inspecao = data_obj + timedelta(days=180)
            
            insert_query = """
                INSERT INTO dbo.inspecoes (
                    equipamento_id, engenheiro_id, data_inspecao, 
                    tipo_inspecao, resultado, recomendacoes,
                    proxima_inspecao, status, prazo_proxima_inspecao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                equipamento_id, engenheiro_id, data_formatada, 
                tipo_inspecao, resultado, recomendacoes,
                proxima_inspecao.isoformat(timespec='seconds'),
                'Ativo',
                proxima_inspecao.isoformat(timespec='seconds')
            )
            
            logger.debug(f"Query: {insert_query}")
            logger.debug(f"Valores: {values}")
            
            cursor.execute(insert_query, values)
            
            # Verifica se a operação teve sucesso
            rows_affected = cursor.rowcount
            logger.debug(f"Linhas afetadas: {rows_affected}")
            
            if rows_affected == 0:
                logger.warning("Nenhuma linha inserida")
                return False, "Falha ao inserir a inspeção"
                
            # Obtém o ID da inspeção inserida
            cursor.execute("SELECT @@IDENTITY")
            inspection_id = cursor.fetchone()[0]
            logger.debug(f"ID da inspeção inserida: {inspection_id}")
            
            # Força a sincronização
            self.force_sync()
            
            logger.info(f"Inspeção #{inspection_id} criada com sucesso para equipamento {equipamento_id}")
            return True, f"Inspeção #{inspection_id} criada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao criar inspeção: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_all_inspections(self):
        """Retorna todas as inspeções"""
        # Garante que a conexão está ativa
        self._ensure_connection()
        
        query = """
            SELECT 
                i.id,
                i.equipamento_id,
                i.data_inspecao,
                i.tipo_inspecao,
                i.resultado,
                i.recomendacoes,
                i.proxima_inspecao,
                i.engenheiro_id,
                i.status,
                i.prazo_proxima_inspecao,
                e.tag AS equipamento_tag,
                e.categoria AS equipamento_categoria,
                u.nome AS engenheiro_nome
            FROM dbo.inspecoes i
            JOIN dbo.equipamentos e ON i.equipamento_id = e.id
            JOIN dbo.usuarios u ON i.engenheiro_id = u.id
            ORDER BY i.data_inspecao DESC
        """
        conn = self.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções: {str(e)}")
            return []
        finally:
            cursor.close()
        
    def get_filtered_inspections(self, filters):
        """Retorna inspeções com base nos filtros aplicados
        
        Args:
            filters (dict): Dicionário com os filtros a serem aplicados
        
        Returns:
            list: Lista de inspeções que atendem aos filtros
        """
        query_parts = [
            """
            SELECT 
                i.id,
                i.equipamento_id,
                i.data_inspecao,
                i.tipo_inspecao,
                i.resultado,
                i.recomendacoes,
                i.proxima_inspecao,
                i.engenheiro_id,
                i.status,
                i.prazo_proxima_inspecao,
                e.tag AS equipamento_tag,
                e.categoria AS equipamento_categoria,
                u.nome AS engenheiro_nome
            FROM dbo.inspecoes i
            JOIN dbo.equipamentos e ON i.equipamento_id = e.id
            JOIN dbo.usuarios u ON i.engenheiro_id = u.id
            WHERE 1=1
            """
        ]
        params = []
        
        # Filtro por data
        if filters.get('date_from') and filters.get('date_to'):
            query_parts.append("AND i.data_inspecao BETWEEN ? AND ?")
            params.append(filters['date_from'])
            params.append(filters['date_to'])
        
        # Filtro por equipamento
        if filters.get('equipment_id'):
            query_parts.append("AND i.equipamento_id = ?")
            params.append(filters['equipment_id'])
        
        # Filtro por tipo de inspeção
        if filters.get('tipo_inspecao'):
            query_parts.append("AND i.tipo_inspecao = ?")
            params.append(filters['tipo_inspecao'])
        
        # Filtro por resultado
        if filters.get('resultado'):
            query_parts.append("AND i.resultado = ?")
            params.append(filters['resultado'])
        
        # Filtro por status
        if filters.get('status'):
            query_parts.append("AND i.status = ?")
            params.append(filters['status'])
        
        # Ordena por data (mais recente primeiro)
        query_parts.append("ORDER BY i.data_inspecao DESC")
        
        # Monta a query completa
        query = " ".join(query_parts)
        
        # Executa a consulta
        conn = self.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções filtradas: {str(e)}")
            return []
        finally:
            cursor.close()
            
    def get_inspection_by_id(self, inspection_id):
        """Retorna uma inspeção específica pelo ID"""
        if not inspection_id:
            logger.warning("ID da inspeção não fornecido")
            return None
            
        try:
            logger.debug(f"Obtendo inspeção {inspection_id}")
            return self.model.get_by_id(inspection_id)
        except Exception as e:
            logger.error(f"Erro ao obter inspeção {inspection_id}: {str(e)}")
            return None
            
    def get_inspections_by_engineer(self, engineer_id: int) -> list[dict]:
        """Retorna as inspeções de um engenheiro específico"""
        try:
            logger.debug(f"Buscando inspeções do engenheiro {engineer_id}")
            conn = self.connection
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
            
    def get_inspections_by_company(self, company_id: int) -> list[dict]:
        """Retorna as inspeções de uma empresa específica"""
        try:
            logger.debug(f"Buscando inspeções da empresa ID: {company_id}")
            self._ensure_connection()
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, i.equipamento_id, i.engenheiro_id, 
                       i.data_inspecao, i.tipo_inspecao, i.resultado,
                       e.tag as equipamento_tag, e.categoria as equipamento_categoria,
                       u.nome as engenheiro_nome
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
                WHERE e.empresa_id = ?
            """, (company_id,))
            
            inspections = []
            for row in cursor.fetchall():
                inspections.append({
                    'id': row[0],
                    'equipamento_id': row[1],
                    'engenheiro_id': row[2],
                    'data': row[3],
                    'tipo': row[4],
                    'resultado': row[5],
                    'equipamento_tag': row[6],
                    'equipamento_categoria': row[7],
                    'engenheiro_nome': row[8]
                })
                
            logger.debug(f"Encontradas {len(inspections)} inspeções para a empresa ID: {company_id}")
            return inspections
            
        except Exception as e:
            logger.error(f"Erro ao buscar inspeções da empresa {company_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            cursor.close()
            
    def update_inspection(self, inspection_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de uma inspeção"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Atualizando inspeção {inspection_id} com parâmetros: {kwargs}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verifica se a inspeção existe
            cursor.execute("SELECT id FROM inspecoes WHERE id = ?", (inspection_id,))
            if not cursor.fetchone():
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                return False, f"Inspeção {inspection_id} não encontrada"
            
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
                
            values.append(inspection_id)
            
            update_query = f"""
                UPDATE inspecoes
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
                logger.warning(f"Nenhuma linha afetada na atualização da inspeção {inspection_id}")
                return False, "Nenhuma alteração realizada"
            
            # Força a sincronização
            self.force_sync()
            
            logger.info(f"Inspeção {inspection_id} atualizada com sucesso. Linhas afetadas: {rows_affected}")
            return True, "Inspeção atualizada com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar inspeção {inspection_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar inspeção: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def cancel_inspection(self, inspection_id: int) -> tuple[bool, str]:
        """Cancela uma inspeção"""
        try:
            logger.debug(f"Cancelando inspeção {inspection_id}")
            conn = self.connection
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
            conn = self.connection
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
            conn = self.connection
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
            
    def create_inspection(self, inspection_data):
        """Cria uma nova inspeção"""
        try:
            # Verificar campos obrigatórios
            required_fields = ['equipamento_id', 'engenheiro_id', 'data_inspecao', 
                              'tipo_inspecao', 'resultado']
            for field in required_fields:
                if field not in inspection_data or not inspection_data[field]:
                    logger.warning(f"Campo obrigatório ausente: {field}")
                    return False, f"Campo obrigatório ausente: {field}"
                    
            # Valores padrão
            recomendacoes = inspection_data.get('recomendacoes', '')
            
            logger.debug(f"Criando inspeção para equipamento {inspection_data['equipamento_id']}")
            success = self.model.create(
                equipamento_id=inspection_data['equipamento_id'],
                engenheiro_id=inspection_data['engenheiro_id'],
                data_inspecao=inspection_data['data_inspecao'],
                tipo_inspecao=inspection_data['tipo_inspecao'],
                resultado=inspection_data['resultado'],
                recomendacoes=recomendacoes
            )
            
            if success:
                return True, "Inspeção criada com sucesso"
            else:
                return False, "Erro ao criar inspeção"
                
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            return False, f"Erro ao criar inspeção: {str(e)}"
            
    def delete_inspection(self, inspection_id):
        """Exclui uma inspeção e seus relatórios associados"""
        if not inspection_id:
            logger.warning("ID da inspeção não fornecido")
            return False, "ID da inspeção não fornecido"
            
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Excluindo inspeção {inspection_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verificar se a inspeção existe
            existing_inspection = self.model.get_by_id(inspection_id)
            if not existing_inspection:
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                return False, f"Inspeção {inspection_id} não encontrada"
            
            # Iniciar uma transação para garantir atomicidade
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # 1. Primeiro, excluir os relatórios associados à inspeção
                logger.debug(f"Excluindo relatórios associados à inspeção {inspection_id}")
                cursor.execute("DELETE FROM relatorios WHERE inspecao_id = ?", (inspection_id,))
                deleted_reports_count = cursor.rowcount
                logger.debug(f"Excluídos {deleted_reports_count} relatórios associados à inspeção {inspection_id}")
                
                # 2. Agora, excluir a inspeção
                logger.debug(f"Excluindo inspeção {inspection_id}")
                success = self.model.delete(inspection_id)
                
                if success:
                    # Confirmar a transação
                    conn.commit()
                    
                    # Força a sincronização
                    self.force_sync()
                    
                    return True, f"Inspeção {inspection_id} e {deleted_reports_count} relatórios associados excluídos com sucesso"
                else:
                    # Reverter alterações em caso de falha
                    conn.rollback()
                    return False, f"Erro ao excluir inspeção {inspection_id}"
                    
            except Exception as e:
                # Reverter alterações em caso de exceção
                conn.rollback()
                raise e
                
        except Exception as e:
            logger.error(f"Erro ao excluir inspeção {inspection_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, f"Erro ao excluir inspeção: {str(e)}"
            
    def get_inspections_by_equipment(self, equipment_id):
        """Retorna todas as inspeções de um equipamento específico"""
        if not equipment_id:
            logger.warning("ID do equipamento não fornecido")
            return []
            
        try:
            logger.debug(f"Obtendo inspeções do equipamento {equipment_id}")
            return self.model.get_by_equipment(equipment_id)
        except Exception as e:
            logger.error(f"Erro ao obter inspeções do equipamento {equipment_id}: {str(e)}")
            return []
            
    def get_inspections_by_date_range(self, start_date, end_date):
        """Retorna todas as inspeções dentro de um intervalo de datas"""
        if not start_date or not end_date:
            logger.warning("Intervalo de datas incompleto")
            return []
            
        try:
            logger.debug(f"Obtendo inspeções entre {start_date} e {end_date}")
            return self.model.get_by_date_range(start_date, end_date)
        except Exception as e:
            logger.error(f"Erro ao obter inspeções por intervalo de datas: {str(e)}")
            return []
            
    def get_inspections_by_type(self, inspection_type):
        """Retorna todas as inspeções de um tipo específico"""
        if not inspection_type:
            logger.warning("Tipo de inspeção não fornecido")
            return []
            
        try:
            logger.debug(f"Obtendo inspeções do tipo {inspection_type}")
            return self.model.get_by_type(inspection_type)
        except Exception as e:
            logger.error(f"Erro ao obter inspeções do tipo {inspection_type}: {str(e)}")
            return []
            
    def get_inspections_by_result(self, result):
        """Retorna todas as inspeções com um resultado específico"""
        if result is None:
            logger.warning("Resultado não fornecido")
            return []
            
        try:
            logger.debug(f"Obtendo inspeções com resultado {result}")
            return self.model.get_by_result(result)
        except Exception as e:
            logger.error(f"Erro ao obter inspeções com resultado {result}: {str(e)}")
            return []
            
    def add_inspection(self, equipamento_id, engenheiro_id, data, tipo, resultado, recomendacoes):
        """
        Adiciona uma nova inspeção ao banco de dados.
        
        Args:
            equipamento_id (int): ID do equipamento inspecionado
            engenheiro_id (int): ID do engenheiro responsável
            data (str): Data da inspeção no formato ISO (YYYY-MM-DD)
            tipo (str): Tipo de inspeção
            resultado (str): Resultado da inspeção
            recomendacoes (str): Recomendações da inspeção
            
        Returns:
            bool: True se a inspeção foi adicionada com sucesso, False caso contrário
        """
        try:
            # Valida os parâmetros
            if not equipamento_id or not engenheiro_id:
                logging.error("IDs de equipamento ou engenheiro inválidos")
                return False
                
            # Converte os IDs para inteiros se necessário
            try:
                equipamento_id = int(equipamento_id)
                engenheiro_id = int(engenheiro_id)
            except (ValueError, TypeError):
                logging.error(f"Erro ao converter IDs: equipamento_id={equipamento_id}, engenheiro_id={engenheiro_id}")
                return False
                
            # Verifica se a data está no formato correto
            if not data:
                data = datetime.datetime.now().strftime("%Y-%m-%d")
                
            # Comando SQL para inserção
            sql = """
                INSERT INTO inspecoes (equipamento_id, engenheiro_id, data, tipo, resultado, recomendacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Executa o comando
            self.cursor.execute(sql, (
                equipamento_id,
                engenheiro_id,
                data,
                tipo,
                resultado,
                recomendacoes
            ))
            
            # Confirma a transação
            self.conn.commit()
            
            logging.info(f"Inspeção adicionada com sucesso: equipamento_id={equipamento_id}, engenheiro_id={engenheiro_id}")
            return True
            
        except sqlite3.Error as e:
            # Reverte a transação em caso de erro
            self.conn.rollback()
            logging.error(f"Erro ao adicionar inspeção: {str(e)}")
            return False
        except Exception as e:
            # Reverte a transação em caso de erro
            self.conn.rollback()
            logging.error(f"Erro inesperado ao adicionar inspeção: {str(e)}")
            return False

    def atualizar_inspecao(self, inspection_id, inspection_data):
        """
        Atualiza uma inspeção existente com os dados fornecidos.
        
        Args:
            inspection_id (int): ID da inspeção a ser atualizada
            inspection_data (dict): Dicionário com os dados da inspeção
            
        Returns:
            tuple: (bool, str) - Sucesso e mensagem
        """
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Atualizando inspeção {inspection_id} com dados: {inspection_data}")
            
            # Verificar se a inspeção existe
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM dbo.inspecoes WHERE id = ?", (inspection_id,))
            if not cursor.fetchone():
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                return False, f"Inspeção {inspection_id} não encontrada"
            
            # Verificar campos obrigatórios
            required_fields = ['equipamento_id', 'engenheiro_id', 'data_inspecao', 
                              'tipo_inspecao', 'resultado']
            for field in required_fields:
                if field not in inspection_data or not inspection_data[field]:
                    logger.warning(f"Campo obrigatório ausente: {field}")
                    return False, f"Campo obrigatório ausente: {field}"
            
            # Construir a query de atualização
            update_fields = []
            update_values = []
            
            for field, value in inspection_data.items():
                if field != 'id':  # Não atualiza o ID
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
                    logger.debug(f"Campo a atualizar: {field} = {value}")
            
            if not update_fields:
                logger.warning("Nenhum campo para atualizar")
                return False, "Nenhum campo para atualizar"
            
            # Adiciona o ID para a cláusula WHERE
            update_values.append(inspection_id)
            
            # Executa a atualização
            update_query = f"UPDATE dbo.inspecoes SET {', '.join(update_fields)} WHERE id = ?"
            logger.debug(f"Query de atualização: {update_query}")
            logger.debug(f"Valores: {update_values}")
            
            cursor.execute(update_query, update_values)
            
            # Verifica se alguma linha foi afetada
            rows_affected = cursor.rowcount
            logger.debug(f"Linhas afetadas: {rows_affected}")
            
            if rows_affected == 0:
                logger.warning(f"Nenhuma linha afetada na atualização da inspeção {inspection_id}")
                return False, "Nenhuma alteração realizada"
            
            # Força a sincronização
            self.force_sync()
            
            logger.info(f"Inspeção {inspection_id} atualizada com sucesso. Campos: {', '.join(update_fields)}")
            return True, f"Inspeção {inspection_id} atualizada com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar inspeção {inspection_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'cursor' in locals():
                cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.rollback()
            return False, f"Erro ao atualizar inspeção: {str(e)}"
        
        finally:
            if 'cursor' in locals():
                cursor.close() 