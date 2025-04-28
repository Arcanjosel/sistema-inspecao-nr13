from database.models import DatabaseModels
import logging

logger = logging.getLogger(__name__)

class EquipmentController:
    def __init__(self):
        self.db_models = DatabaseModels()
        
    def criar_equipamento(self, tipo: str, empresa: str, localizacao: str, 
                         codigo: str, pressao: str, temperatura: str) -> tuple[bool, str]:
        """Cria um novo equipamento no sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO equipamentos (tipo, empresa, localizacao, codigo_projeto, 
                                        pressao_maxima, temperatura_maxima, status)
                VALUES (?, ?, ?, ?, ?, ?, 'ativo')
            """, (tipo, empresa, localizacao, codigo, pressao, temperatura))
            
            conn.commit()
            return True, "Equipamento criado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao criar equipamento: {str(e)}")
            return False, f"Erro ao criar equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def get_all_equipment(self) -> list[dict]:
        """Retorna todos os equipamentos do sistema"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tipo, empresa, localizacao, codigo_projeto, 
                       pressao_maxima, temperatura_maxima, status
                FROM equipamentos
                WHERE status = 'ativo'
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
            logger.error(f"Erro ao buscar equipamentos: {str(e)}")
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
            
    def update_equipment(self, equipment_id: int, **kwargs) -> tuple[bool, str]:
        """Atualiza os dados de um equipamento"""
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
                
            values.append(equipment_id)
            
            cursor.execute(f"""
                UPDATE equipamentos
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            return True, "Equipamento atualizado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao atualizar equipamento: {str(e)}")
            return False, f"Erro ao atualizar equipamento: {str(e)}"
            
        finally:
            cursor.close()
            
    def delete_equipment(self, equipment_id: int) -> tuple[bool, str]:
        """Marca um equipamento como inativo"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE equipamentos
                SET status = 'inativo'
                WHERE id = ?
            """, (equipment_id,))
            
            conn.commit()
            return True, "Equipamento removido com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao remover equipamento: {str(e)}")
            return False, f"Erro ao remover equipamento: {str(e)}"
            
        finally:
            cursor.close() 