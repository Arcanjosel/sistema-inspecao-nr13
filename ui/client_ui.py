"""
Interface gráfica do cliente do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels

logger = logging.getLogger(__name__)

class ClientWindow(QMainWindow):
    """
    Janela principal do cliente.
    """
    
    def __init__(self, auth_controller: AuthController, user_email: str):
        super().__init__()
        self.auth_controller = auth_controller
        self.db_models = DatabaseModels()
        self.user_email = user_email
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle('Sistema de Inspeções NR-13 - Cliente')
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Abas
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Aba de Equipamentos
        equipment_tab = QWidget()
        tabs.addTab(equipment_tab, "Meus Equipamentos")
        self._setup_equipment_tab(equipment_tab)
        
        # Aba de Inspeções
        inspection_tab = QWidget()
        tabs.addTab(inspection_tab, "Minhas Inspeções")
        self._setup_inspection_tab(inspection_tab)
        
        # Aba de Relatórios
        reports_tab = QWidget()
        tabs.addTab(reports_tab, "Meus Relatórios")
        self._setup_reports_tab(reports_tab)
        
    def _setup_equipment_tab(self, tab):
        """Configura a aba de equipamentos."""
        layout = QVBoxLayout(tab)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.equipment_filter = QComboBox()
        self.equipment_filter.addItems(["Todos", "Caldeiras", "Vasos de Pressão", "Tubulações"])
        filter_layout.addWidget(self.equipment_filter)
        
        self.equipment_status = QComboBox()
        self.equipment_status.addItems(["Todos", "Ativos", "Inativos", "Em Manutenção"])
        filter_layout.addWidget(self.equipment_status)
        
        filter_button = QPushButton("Filtrar")
        filter_button.clicked.connect(self._filter_equipment)
        filter_layout.addWidget(filter_button)
        
        layout.addLayout(filter_layout)
        
        # Tabela de equipamentos
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(8)
        self.equipment_table.setHorizontalHeaderLabels([
            "ID", "Tipo", "Localização", "Código", "Pressão",
            "Temperatura", "Última Inspeção", "Próxima Inspeção"
        ])
        layout.addWidget(self.equipment_table)
        
        self._load_equipment()
        
    def _setup_inspection_tab(self, tab):
        """Configura a aba de inspeções."""
        layout = QVBoxLayout(tab)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.inspection_filter = QComboBox()
        self.inspection_filter.addItems([
            "Todas", "Próximas 30 dias", "Vencidas",
            "Periódicas", "Extraordinárias"
        ])
        filter_layout.addWidget(self.inspection_filter)
        
        filter_button = QPushButton("Filtrar")
        filter_button.clicked.connect(self._filter_inspections)
        filter_layout.addWidget(filter_button)
        
        layout.addLayout(filter_layout)
        
        # Tabela de inspeções
        self.inspection_table = QTableWidget()
        self.inspection_table.setColumnCount(7)
        self.inspection_table.setHorizontalHeaderLabels([
            "ID", "Equipamento", "Data", "Tipo", "Engenheiro",
            "Resultado", "Status"
        ])
        layout.addWidget(self.inspection_table)
        
        self._load_inspections()
        
    def _setup_reports_tab(self, tab):
        """Configura a aba de relatórios."""
        layout = QVBoxLayout(tab)
        
        # Tabela de relatórios
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "ID", "Inspeção", "Data", "Arquivo"
        ])
        layout.addWidget(self.report_table)
        
        self._load_reports()
        
    def _load_equipment(self):
        """Carrega os equipamentos na tabela."""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.*, i.data_inspecao, i.proxima_inspecao
                FROM equipamentos e
                LEFT JOIN inspecoes i ON e.id = i.equipamento_id
                WHERE e.empresa = (
                    SELECT empresa FROM usuarios WHERE email = ?
                )
                ORDER BY i.proxima_inspecao ASC
            """, (self.user_email,))
            
            equipment = cursor.fetchall()
            
            self.equipment_table.setRowCount(len(equipment))
            for i, item in enumerate(equipment):
                self.equipment_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
                self.equipment_table.setItem(i, 1, QTableWidgetItem(item.tipo))
                self.equipment_table.setItem(i, 2, QTableWidgetItem(item.localizacao))
                self.equipment_table.setItem(i, 3, QTableWidgetItem(item.codigo_projeto))
                self.equipment_table.setItem(i, 4, QTableWidgetItem(str(item.pressao_maxima)))
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(item.temperatura_maxima)))
                self.equipment_table.setItem(i, 6, QTableWidgetItem(str(item.data_inspecao or "")))
                self.equipment_table.setItem(i, 7, QTableWidgetItem(str(item.proxima_inspecao or "")))
                
                # Destaca equipamentos com inspeção próxima ou vencida
                if item.proxima_inspecao:
                    if item.proxima_inspecao < datetime.now():
                        for j in range(8):
                            self.equipment_table.item(i, j).setBackground(Qt.red)
                    elif (item.proxima_inspecao - datetime.now()).days <= 30:
                        for j in range(8):
                            self.equipment_table.item(i, j).setBackground(Qt.yellow)
                            
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
            
        finally:
            cursor.close()
            
    def _filter_equipment(self):
        """Filtra os equipamentos na tabela."""
        try:
            tipo = self.equipment_filter.currentText()
            status = self.equipment_status.currentText()
            
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT e.*, i.data_inspecao, i.proxima_inspecao
                FROM equipamentos e
                LEFT JOIN inspecoes i ON e.id = i.equipamento_id
                WHERE e.empresa = (
                    SELECT empresa FROM usuarios WHERE email = ?
                )
            """
            params = [self.user_email]
            
            if tipo != "Todos":
                query += " AND e.tipo = ?"
                params.append(tipo.lower().replace(" ", "_"))
                
            if status != "Todos":
                query += " AND e.status = ?"
                params.append(status.lower().replace(" ", "_"))
                
            query += " ORDER BY i.proxima_inspecao ASC"
            
            cursor.execute(query, params)
            equipment = cursor.fetchall()
            
            self.equipment_table.setRowCount(len(equipment))
            for i, item in enumerate(equipment):
                self.equipment_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
                self.equipment_table.setItem(i, 1, QTableWidgetItem(item.tipo))
                self.equipment_table.setItem(i, 2, QTableWidgetItem(item.localizacao))
                self.equipment_table.setItem(i, 3, QTableWidgetItem(item.codigo_projeto))
                self.equipment_table.setItem(i, 4, QTableWidgetItem(str(item.pressao_maxima)))
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(item.temperatura_maxima)))
                self.equipment_table.setItem(i, 6, QTableWidgetItem(str(item.data_inspecao or "")))
                self.equipment_table.setItem(i, 7, QTableWidgetItem(str(item.proxima_inspecao or "")))
                
                # Destaca equipamentos com inspeção próxima ou vencida
                if item.proxima_inspecao:
                    if item.proxima_inspecao < datetime.now():
                        for j in range(8):
                            self.equipment_table.item(i, j).setBackground(Qt.red)
                    elif (item.proxima_inspecao - datetime.now()).days <= 30:
                        for j in range(8):
                            self.equipment_table.item(i, j).setBackground(Qt.yellow)
                            
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar equipamentos: {str(e)}")
            
        finally:
            cursor.close()
            
    def _load_inspections(self):
        """Carrega as inspeções na tabela."""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.*, e.codigo_projeto
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                WHERE e.empresa = (
                    SELECT empresa FROM usuarios WHERE email = ?
                )
                ORDER BY i.data_inspecao DESC
            """, (self.user_email,))
            
            inspections = cursor.fetchall()
            
            self.inspection_table.setRowCount(len(inspections))
            for i, insp in enumerate(inspections):
                self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp.id)))
                self.inspection_table.setItem(i, 1, QTableWidgetItem(insp.codigo_projeto))
                self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp.data_inspecao)))
                self.inspection_table.setItem(i, 3, QTableWidgetItem(insp.tipo_inspecao))
                self.inspection_table.setItem(i, 4, QTableWidgetItem(insp.engenheiro_responsavel))
                self.inspection_table.setItem(i, 5, QTableWidgetItem(insp.resultado))
                
                # Define o status da inspeção
                if insp.proxima_inspecao:
                    if insp.proxima_inspecao < datetime.now():
                        status = "Vencida"
                        for j in range(7):
                            self.inspection_table.item(i, j).setBackground(Qt.red)
                    elif (insp.proxima_inspecao - datetime.now()).days <= 30:
                        status = "Próxima"
                        for j in range(7):
                            self.inspection_table.item(i, j).setBackground(Qt.yellow)
                    else:
                        status = "Em dia"
                else:
                    status = "Sem data definida"
                    
                self.inspection_table.setItem(i, 6, QTableWidgetItem(status))
                
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
            
        finally:
            cursor.close()
            
    def _filter_inspections(self):
        """Filtra as inspeções na tabela."""
        try:
            filtro = self.inspection_filter.currentText()
            
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT i.*, e.codigo_projeto
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                WHERE e.empresa = (
                    SELECT empresa FROM usuarios WHERE email = ?
                )
            """
            params = [self.user_email]
            
            if filtro == "Próximas 30 dias":
                query += " AND i.proxima_inspecao BETWEEN ? AND ?"
                params.extend([datetime.now(), datetime.now() + timedelta(days=30)])
            elif filtro == "Vencidas":
                query += " AND i.proxima_inspecao < ?"
                params.append(datetime.now())
            elif filtro == "Periódicas":
                query += " AND i.tipo_inspecao = 'periodica'"
            elif filtro == "Extraordinárias":
                query += " AND i.tipo_inspecao = 'extraordinaria'"
                
            query += " ORDER BY i.data_inspecao DESC"
            
            cursor.execute(query, params)
            inspections = cursor.fetchall()
            
            self.inspection_table.setRowCount(len(inspections))
            for i, insp in enumerate(inspections):
                self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp.id)))
                self.inspection_table.setItem(i, 1, QTableWidgetItem(insp.codigo_projeto))
                self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp.data_inspecao)))
                self.inspection_table.setItem(i, 3, QTableWidgetItem(insp.tipo_inspecao))
                self.inspection_table.setItem(i, 4, QTableWidgetItem(insp.engenheiro_responsavel))
                self.inspection_table.setItem(i, 5, QTableWidgetItem(insp.resultado))
                
                # Define o status da inspeção
                if insp.proxima_inspecao:
                    if insp.proxima_inspecao < datetime.now():
                        status = "Vencida"
                        for j in range(7):
                            self.inspection_table.item(i, j).setBackground(Qt.red)
                    elif (insp.proxima_inspecao - datetime.now()).days <= 30:
                        status = "Próxima"
                        for j in range(7):
                            self.inspection_table.item(i, j).setBackground(Qt.yellow)
                    else:
                        status = "Em dia"
                else:
                    status = "Sem data definida"
                    
                self.inspection_table.setItem(i, 6, QTableWidgetItem(status))
                
        except Exception as e:
            logger.error(f"Erro ao filtrar inspeções: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar inspeções: {str(e)}")
            
        finally:
            cursor.close()
            
    def _load_reports(self):
        """Carrega os relatórios na tabela."""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.*, i.data_inspecao
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
                JOIN equipamentos e ON i.equipamento_id = e.id
                WHERE e.empresa = (
                    SELECT empresa FROM usuarios WHERE email = ?
                )
                ORDER BY r.data_emissao DESC
            """, (self.user_email,))
            
            reports = cursor.fetchall()
            
            self.report_table.setRowCount(len(reports))
            for i, rep in enumerate(reports):
                self.report_table.setItem(i, 0, QTableWidgetItem(str(rep.id)))
                self.report_table.setItem(i, 1, QTableWidgetItem(str(rep.inspecao_id)))
                self.report_table.setItem(i, 2, QTableWidgetItem(str(rep.data_emissao)))
                self.report_table.setItem(i, 3, QTableWidgetItem(rep.link_arquivo))
                
        except Exception as e:
            logger.error(f"Erro ao carregar relatórios: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar relatórios: {str(e)}")
            
        finally:
            cursor.close() 