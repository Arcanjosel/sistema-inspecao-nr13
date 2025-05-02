from database.models import DatabaseModels
import logging
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EquipmentController:
    def __init__(self, db_models: DatabaseModels):
        logger.debug("Iniciando EquipmentController")
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
        
    def criar_equipamento(self, tag: str, categoria: str, empresa_id: int,
                         fabricante: str, ano_fabricacao: int,
                         pressao_projeto: float, pressao_trabalho: float,
                         volume: float, fluido: str,
                         categoria_nr13: str = None, pmta: str = None,
                         placa_identificacao: str = None, numero_registro: str = None) -> tuple[bool, str]:
        """Cria um novo equipamento no sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            logger.debug(f"Criando equipamento com tag {tag}")
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO equipamentos (tag, categoria, empresa_id,
                                        fabricante, ano_fabricacao,
                                        pressao_projeto, pressao_trabalho,
                                        volume, fluido,
                                        categoria_nr13, pmta, placa_identificacao, numero_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tag, categoria, empresa_id, fabricante, ano_fabricacao,
                  pressao_projeto, pressao_trabalho, volume, fluido,
                  categoria_nr13, pmta, placa_identificacao, numero_registro))
            # Força a sincronização
            self.force_sync()
            logger.info(f"Equipamento {tag} criado com sucesso")
            return True, "Equipamento criado com sucesso!"
        except Exception as e:
            logger.error(f"Erro ao criar equipamento {tag}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao criar equipamento: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_all_equipment(self) -> list[dict]:
        """Retorna todos os equipamentos do sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            logger.debug("Buscando todos os equipamentos")
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.id, e.tag, e.categoria, e.empresa_id,
                       e.fabricante, e.ano_fabricacao, e.pressao_projeto,
                       e.pressao_trabalho, e.volume, e.fluido, 
                       e.frequencia_manutencao, e.data_ultima_manutencao,
                       e.categoria_nr13, e.pmta, e.placa_identificacao, e.numero_registro,
                       CASE 
                           WHEN e.ativo IS NOT NULL THEN e.ativo 
                           WHEN e.status = 'ativo' THEN 1
                           ELSE 0
                       END AS ativo_calculado,
                       u.nome as empresa_nome
                FROM equipamentos e
                LEFT JOIN usuarios u ON e.empresa_id = u.id
                ORDER BY e.tag
            """)
            equipment = []
            for row in cursor.fetchall():
                equipment_item = {
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
                    'frequencia_manutencao': row[10],
                    'data_ultima_manutencao': row[11],
                    'categoria_nr13': row[12],
                    'pmta': row[13],
                    'placa_identificacao': row[14],
                    'numero_registro': row[15],
                    'ativo': bool(row[16]),
                    'empresa_nome': row[17] if row[17] else ''
                }
                
                # Calcular dias até próxima manutenção se houver data de última manutenção
                if equipment_item['data_ultima_manutencao'] and equipment_item['frequencia_manutencao']:
                    dias_ate_manutencao = self.calcular_dias_ate_proxima_manutencao(
                        equipment_item['data_ultima_manutencao'], 
                        equipment_item['frequencia_manutencao']
                    )
                    equipment_item['dias_ate_manutencao'] = dias_ate_manutencao
                else:
                    equipment_item['dias_ate_manutencao'] = None
                    
                equipment.append(equipment_item)
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos")
            return equipment
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_equipment_by_company(self, company_id: int) -> list[dict]:
        """
        Busca todos os equipamentos de uma empresa
        """
        try:
            logger.debug(f"Buscando equipamentos da empresa ID: {company_id}")
            self._ensure_connection()
            conn = self.connection
            cursor = conn.cursor()
            
            logger.debug(f"Executando consulta para buscar equipamentos da empresa ID: {company_id}")
            
            # Query atualizada para incluir campos de manutenção
            cursor.execute("""
                SELECT 
                    id, tag, categoria, empresa_id, fabricante, 
                    ano_fabricacao, pressao_projeto, pressao_trabalho, 
                    volume, fluido, frequencia_manutencao, data_ultima_manutencao,
                    CASE 
                        WHEN ativo IS NOT NULL THEN ativo 
                        WHEN status = 'ativo' THEN 1
                        ELSE 0
                    END AS ativo
                FROM equipamentos 
                WHERE empresa_id = ?
            """, (company_id,))
            
            results = cursor.fetchall()
            equipment_list = []
            
            logger.debug(f"Foram encontrados {len(results)} equipamentos para a empresa ID: {company_id}")
            
            for row in results:
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
                    'frequencia_manutencao': row[10],
                    'data_ultima_manutencao': row[11],
                    'ativo': row[12]
                }
                
                # Calcular dias até próxima manutenção se houver data de última manutenção
                if equipment['data_ultima_manutencao'] and equipment['frequencia_manutencao']:
                    dias_ate_manutencao = self.calcular_dias_ate_proxima_manutencao(
                        equipment['data_ultima_manutencao'], 
                        equipment['frequencia_manutencao']
                    )
                    equipment['dias_ate_manutencao'] = dias_ate_manutencao
                else:
                    equipment['dias_ate_manutencao'] = None
                
                equipment_list.append(equipment)
                logger.debug(f"Adicionado equipamento ID={equipment['id']}, Tag={equipment['tag']}")
                
            logger.debug(f"Processados {len(equipment_list)} equipamentos para a empresa ID: {company_id}")
            return equipment_list
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos da empresa {company_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_available_equipment(self) -> list[dict]:
        """Retorna os equipamentos disponíveis para inspeção"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug("Buscando equipamentos disponíveis para inspeção")
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
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos disponíveis")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamentos disponíveis: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def update_equipment(self, equipment_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de um equipamento"""
        try:
            self._ensure_connection()
            logger.debug(f"Atualizando equipamento {equipment_id}")
            conn = self.connection
            cursor = conn.cursor()
            update_fields = []
            values = []
            # Permitir atualização dos campos NR-13
            for field, value in kwargs.items():
                if value is not None and field in [
                    'tag', 'categoria', 'empresa_id', 'fabricante', 'ano_fabricacao',
                    'pressao_projeto', 'pressao_trabalho', 'volume', 'fluido',
                    'categoria_nr13', 'pmta', 'placa_identificacao', 'numero_registro']:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                    logger.debug(f"Campo a atualizar: {field} = {value}")
            if not update_fields:
                logger.warning("Nenhum campo para atualizar")
                return False, "Nenhum campo para atualizar"
            values.append(equipment_id)
            update_query = f"""
                UPDATE equipamentos
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            logger.debug(f"Query de atualização: {update_query}")
            logger.debug(f"Valores: {values}")
            cursor.execute(update_query, values)
            rows_affected = cursor.rowcount
            logger.debug(f"Linhas afetadas: {rows_affected}")
            if rows_affected == 0:
                logger.warning(f"Nenhuma linha afetada na atualização do equipamento {equipment_id}")
                return False, "Nenhuma alteração realizada"
            self.force_sync()
            logger.info(f"Equipamento {equipment_id} atualizado com sucesso. Linhas afetadas: {rows_affected}")
            return True, "Equipamento atualizado com sucesso!"
        except Exception as e:
            logger.error(f"Erro ao atualizar equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar equipamento: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def delete_equipment(self, equipment_id: int) -> tuple[bool, str]:
        """Exclui um equipamento do sistema"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Excluindo equipamento {equipment_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verificar se o equipamento existe
            cursor.execute("SELECT id FROM equipamentos WHERE id = ?", (equipment_id,))
            if not cursor.fetchone():
                logger.warning(f"Equipamento {equipment_id} não encontrado")
                return False, f"Equipamento {equipment_id} não encontrado"
                
            # Verificar se há inspeções associadas
            cursor.execute("SELECT COUNT(*) FROM inspecoes WHERE equipamento_id = ?", (equipment_id,))
            inspection_count = cursor.fetchone()[0]
            
            if inspection_count > 0:
                logger.warning(f"Equipamento {equipment_id} possui {inspection_count} inspeções associadas. Não pode ser excluído.")
                return False, f"Equipamento possui {inspection_count} inspeções associadas. Não pode ser excluído."
                
            # Excluir equipamento
            cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equipment_id,))
            
            # Força a sincronização
            self.force_sync()
            
            logger.info(f"Equipamento {equipment_id} excluído com sucesso")
            return True, "Equipamento excluído com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao excluir equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao excluir equipamento: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_equipment_by_id(self, equipment_id):
        """Retorna um equipamento específico pelo ID"""
        if not equipment_id:
            logger.warning("ID do equipamento não fornecido")
            return None
        try:
            self._ensure_connection()
            logger.debug(f"Obtendo equipamento {equipment_id}")
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.id, e.tag, e.categoria, e.empresa_id,
                       e.fabricante, e.ano_fabricacao, e.pressao_projeto,
                       e.pressao_trabalho, e.volume, e.fluido, e.ativo,
                       e.categoria_nr13, e.pmta, e.placa_identificacao, e.numero_registro,
                       u.nome as empresa_nome
                FROM equipamentos e
                LEFT JOIN usuarios u ON e.empresa_id = u.id
                WHERE e.id = ?
            """, (equipment_id,))
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Nenhum equipamento encontrado com ID {equipment_id}")
                return None
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
                'ativo': bool(row[10]),
                'categoria_nr13': row[11],
                'pmta': row[12],
                'placa_identificacao': row[13],
                'numero_registro': row[14],
                'empresa_nome': row[15] if row[15] else ''
            }
            logger.debug(f"Equipamento {equipment_id} encontrado: {equipment['tag']}")
            return equipment
        except Exception as e:
            logger.error(f"Erro ao buscar equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def toggle_equipment_status(self, equipment_id, new_status) -> tuple[bool, str]:
        """Altera o status de um equipamento (ativo/inativo)"""
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Alterando status do equipamento {equipment_id} para {new_status}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verificar se o equipamento existe
            cursor.execute("SELECT id, tag FROM equipamentos WHERE id = ?", (equipment_id,))
            equipment = cursor.fetchone()
            
            if not equipment:
                logger.warning(f"Equipamento {equipment_id} não encontrado")
                return False, f"Equipamento {equipment_id} não encontrado"
                
            # Atualizar status
            cursor.execute(
                "UPDATE equipamentos SET ativo = ? WHERE id = ?",
                (1 if new_status else 0, equipment_id)
            )
            
            # Força a sincronização
            self.force_sync()
            
            status_text = "ativado" if new_status else "desativado"
            logger.info(f"Equipamento {equipment[1]} (ID: {equipment_id}) {status_text} com sucesso")
            return True, f"Equipamento {equipment[1]} {status_text} com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao alterar status do equipamento {equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao alterar status do equipamento: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def get_equipment_by_tag(self, tag):
        """Busca um equipamento pela tag"""
        if not tag:
            logger.warning("Tag do equipamento não fornecida")
            return None
            
        try:
            # Garante que a conexão está ativa
            self._ensure_connection()
            
            logger.debug(f"Buscando equipamento com tag {tag}")
            conn = self.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.id, e.tag, e.categoria, e.empresa_id,
                       e.fabricante, e.ano_fabricacao, e.pressao_projeto,
                       e.pressao_trabalho, e.volume, e.fluido, e.ativo,
                       u.nome as empresa_nome
                FROM equipamentos e
                LEFT JOIN usuarios u ON e.empresa_id = u.id
                WHERE e.tag LIKE ?
            """, (f"%{tag}%",))
            
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
                
            logger.debug(f"Encontrados {len(equipment)} equipamentos com tag similar a {tag}")
            return equipment
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamento com tag {tag}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            
    def activate_equipment(self, equipment_id):
        """Ativa um equipamento"""
        return self.toggle_equipment_status(equipment_id, True)
        
    def deactivate_equipment(self, equipment_id):
        """Desativa um equipamento"""
        return self.toggle_equipment_status(equipment_id, False)

    def atualizar_manutencao_equipamento(self, equipment_id: int, data_ultima_manutencao, frequencia_manutencao=None) -> tuple[bool, str]:
        """Atualiza a data da última manutenção e opcionalmente a frequência de manutenção de um equipamento"""
        try:
            self._ensure_connection()
            logger.debug(f"Atualizando manutenção do equipamento ID={equipment_id}")
            conn = self.connection
            cursor = conn.cursor()
            
            # Converter a data para string se for um objeto datetime
            if isinstance(data_ultima_manutencao, datetime):
                data_ultima_manutencao_str = data_ultima_manutencao.strftime('%Y-%m-%d')
            else:
                data_ultima_manutencao_str = data_ultima_manutencao
            
            logger.debug(f"Data formatada: {data_ultima_manutencao_str}")
            
            # Usar SQL direto sem placeholders para evitar problemas com o driver
            if frequencia_manutencao:
                sql = f"UPDATE equipamentos SET data_ultima_manutencao = '{data_ultima_manutencao_str}', frequencia_manutencao = {frequencia_manutencao} WHERE id = {equipment_id}"
            else:
                sql = f"UPDATE equipamentos SET data_ultima_manutencao = '{data_ultima_manutencao_str}' WHERE id = {equipment_id}"
            
            logger.debug(f"SQL: {sql}")
            cursor.execute(sql)
            
            # Forçar commit das alterações
            conn.commit()
            logger.info(f"Manutenção do equipamento ID={equipment_id} atualizada com sucesso")
            return True, "Manutenção atualizada com sucesso"
        except Exception as e:
            logger.error(f"Erro ao atualizar manutenção do equipamento ID={equipment_id}: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar manutenção: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()

    def atualizar_tabela_equipamentos(self):
        """Atualiza a estrutura da tabela equipamentos para adicionar novos campos"""
        try:
            self._ensure_connection()
            logger.debug("Atualizando estrutura da tabela equipamentos")
            conn = self.connection
            cursor = conn.cursor()
            
            # Verificar se a coluna frequencia_manutencao já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'frequencia_manutencao'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna frequencia_manutencao
                cursor.execute("""
                    ALTER TABLE equipamentos
                    ADD frequencia_manutencao INT DEFAULT 180
                """)
                logger.info("Coluna frequencia_manutencao adicionada à tabela equipamentos")
            
            # Verificar se a coluna data_ultima_manutencao já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'equipamentos' AND COLUMN_NAME = 'data_ultima_manutencao'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna data_ultima_manutencao
                cursor.execute("""
                    ALTER TABLE equipamentos
                    ADD data_ultima_manutencao DATE
                """)
                logger.info("Coluna data_ultima_manutencao adicionada à tabela equipamentos")
            
            # Forçar commit das alterações
            conn.commit()
            return True, "Tabela equipamentos atualizada com sucesso"
        except Exception as e:
            logger.error(f"Erro ao atualizar tabela equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            if 'conn' in locals():
                conn.rollback()
            return False, f"Erro ao atualizar tabela equipamentos: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()

    def calcular_dias_ate_proxima_manutencao(self, data_ultima_manutencao, frequencia_dias):
        """Calcula quantos dias faltam para a próxima manutenção"""
        if not data_ultima_manutencao or not frequencia_dias:
            return None
            
        try:
            # Converter data_ultima_manutencao para datetime se for string
            if isinstance(data_ultima_manutencao, str):
                try:
                    # Tentar converter para datetime
                    if len(data_ultima_manutencao) >= 10:
                        data_ultima_manutencao = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d')
                    else:
                        logger.warning(f"Formato de data inválido: {data_ultima_manutencao}")
                        return None
                except Exception as e:
                    logger.error(f"Erro ao converter data: {str(e)}")
                    return None
                
            hoje = datetime.now().date()
            proxima_manutencao = data_ultima_manutencao + timedelta(days=frequencia_dias)
            
            # Se data_ultima_manutencao é datetime mas não date, converter
            if isinstance(proxima_manutencao, datetime):
                proxima_manutencao = proxima_manutencao.date()
                
            return (proxima_manutencao - hoje).days
        except Exception as e:
            logger.error(f"Erro ao calcular dias até próxima manutenção: {str(e)}")
            logger.error(traceback.format_exc())
            return None