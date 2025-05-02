from database.models import DatabaseModels
import logging
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EquipmentController:
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
            
        hoje = datetime.now().date()
        proxima_manutencao = data_ultima_manutencao + timedelta(days=frequencia_dias)
        return (proxima_manutencao - hoje).days 