"""
Interface gráfica do administrador do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels

logger = logging.getLogger(__name__)

class AdminWindow(QMainWindow):
    """
    Janela principal do administrador.
    """
    
    def __init__(self, auth_controller: AuthController):
        super().__init__()
        self.auth_controller = auth_controller
        self.db_models = DatabaseModels()
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle('Sistema de Inspeções NR-13 - Administrador')
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Abas
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Aba de Usuários
        users_tab = QWidget()
        tabs.addTab(users_tab, "Usuários")
        self._setup_users_tab(users_tab)
        
        # Aba de Equipamentos
        equipment_tab = QWidget()
        tabs.addTab(equipment_tab, "Equipamentos")
        self._setup_equipment_tab(equipment_tab)
        
        # Aba de Inspeções
        inspection_tab = QWidget()
        tabs.addTab(inspection_tab, "Inspeções")
        self._setup_inspection_tab(inspection_tab)
        
        # Aba de Relatórios
        reports_tab = QWidget()
        tabs.addTab(reports_tab, "Relatórios")
        self._setup_reports_tab(reports_tab)
        
    def _setup_users_tab(self, tab):
        """Configura a aba de usuários."""
        layout = QVBoxLayout(tab)
        
        # Formulário de cadastro
        form_layout = QHBoxLayout()
        
        # Campos do formulário
        self.user_name = QLineEdit()
        self.user_name.setPlaceholderText("Nome")
        form_layout.addWidget(self.user_name)
        
        self.user_email = QLineEdit()
        self.user_email.setPlaceholderText("Email")
        form_layout.addWidget(self.user_email)
        
        self.user_password = QLineEdit()
        self.user_password.setPlaceholderText("Senha")
        self.user_password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.user_password)
        
        self.user_type = QComboBox()
        self.user_type.addItems(["admin", "cliente"])
        form_layout.addWidget(self.user_type)
        
        self.user_company = QLineEdit()
        self.user_company.setPlaceholderText("Empresa")
        form_layout.addWidget(self.user_company)
        
        add_button = QPushButton("Adicionar Usuário")
        add_button.clicked.connect(self._add_user)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Tabela de usuários
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Tipo", "Empresa", "Status"
        ])
        layout.addWidget(self.users_table)
        
        self._load_users()
        
    def _setup_equipment_tab(self, tab):
        """Configura a aba de equipamentos."""
        layout = QVBoxLayout(tab)
        
        # Formulário de cadastro
        form_layout = QHBoxLayout()
        
        # Campos do formulário
        self.equipment_type = QComboBox()
        self.equipment_type.addItems(["caldeira", "vaso_pressao", "tubulacao"])
        form_layout.addWidget(self.equipment_type)
        
        self.equipment_company = QLineEdit()
        self.equipment_company.setPlaceholderText("Empresa")
        form_layout.addWidget(self.equipment_company)
        
        self.equipment_location = QLineEdit()
        self.equipment_location.setPlaceholderText("Localização")
        form_layout.addWidget(self.equipment_location)
        
        self.equipment_code = QLineEdit()
        self.equipment_code.setPlaceholderText("Código do Projeto")
        form_layout.addWidget(self.equipment_code)
        
        self.equipment_pressure = QLineEdit()
        self.equipment_pressure.setPlaceholderText("Pressão Máxima")
        form_layout.addWidget(self.equipment_pressure)
        
        self.equipment_temperature = QLineEdit()
        self.equipment_temperature.setPlaceholderText("Temperatura Máxima")
        form_layout.addWidget(self.equipment_temperature)
        
        add_button = QPushButton("Adicionar Equipamento")
        add_button.clicked.connect(self._add_equipment)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Tabela de equipamentos
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(8)
        self.equipment_table.setHorizontalHeaderLabels([
            "ID", "Tipo", "Empresa", "Localização", "Código",
            "Pressão", "Temperatura", "Status"
        ])
        layout.addWidget(self.equipment_table)
        
        self._load_equipment()
        
    def _setup_inspection_tab(self, tab):
        """Configura a aba de inspeções."""
        layout = QVBoxLayout(tab)
        
        # Formulário de cadastro
        form_layout = QHBoxLayout()
        
        # Campos do formulário
        self.inspection_equipment = QComboBox()
        form_layout.addWidget(self.inspection_equipment)
        
        self.inspection_date = QDateEdit()
        self.inspection_date.setDate(QDate.currentDate())
        form_layout.addWidget(self.inspection_date)
        
        self.inspection_type = QComboBox()
        self.inspection_type.addItems(["periodica", "extraordinaria"])
        form_layout.addWidget(self.inspection_type)
        
        self.inspection_engineer = QLineEdit()
        self.inspection_engineer.setPlaceholderText("Engenheiro Responsável")
        form_layout.addWidget(self.inspection_engineer)
        
        self.inspection_result = QComboBox()
        self.inspection_result.addItems(["aprovado", "reprovado", "condicional"])
        form_layout.addWidget(self.inspection_result)
        
        self.inspection_recommendations = QTextEdit()
        self.inspection_recommendations.setPlaceholderText("Recomendações")
        form_layout.addWidget(self.inspection_recommendations)
        
        add_button = QPushButton("Adicionar Inspeção")
        add_button.clicked.connect(self._add_inspection)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Tabela de inspeções
        self.inspection_table = QTableWidget()
        self.inspection_table.setColumnCount(7)
        self.inspection_table.setHorizontalHeaderLabels([
            "ID", "Equipamento", "Data", "Tipo", "Engenheiro",
            "Resultado", "Próxima Inspeção"
        ])
        layout.addWidget(self.inspection_table)
        
        self._load_inspections()
        
    def _setup_reports_tab(self, tab):
        """Configura a aba de relatórios."""
        layout = QVBoxLayout(tab)
        
        # Formulário de cadastro
        form_layout = QHBoxLayout()
        
        # Campos do formulário
        self.report_inspection = QComboBox()
        form_layout.addWidget(self.report_inspection)
        
        self.report_date = QDateEdit()
        self.report_date.setDate(QDate.currentDate())
        form_layout.addWidget(self.report_date)
        
        self.report_file = QLineEdit()
        self.report_file.setPlaceholderText("Link do Arquivo")
        form_layout.addWidget(self.report_file)
        
        self.report_observations = QTextEdit()
        self.report_observations.setPlaceholderText("Observações")
        form_layout.addWidget(self.report_observations)
        
        add_button = QPushButton("Adicionar Relatório")
        add_button.clicked.connect(self._add_report)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Tabela de relatórios
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "ID", "Inspeção", "Data", "Arquivo"
        ])
        layout.addWidget(self.report_table)
        
        self._load_reports()
        
    def _add_user(self):
        """Adiciona um novo usuário."""
        try:
            nome = self.user_name.text()
            email = self.user_email.text()
            senha = self.user_password.text()
            tipo = self.user_type.currentText()
            empresa = self.user_company.text()
            
            if not all([nome, email, senha]):
                QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios")
                return
                
            if self.auth_controller.criar_usuario(nome, email, senha, tipo, empresa):
                QMessageBox.information(self, "Sucesso", "Usuário criado com sucesso")
                self._load_users()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao criar usuário")
                
        except Exception as e:
            logger.error(f"Erro ao adicionar usuário: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar usuário: {str(e)}")
            
    def _load_users(self):
        """Carrega os usuários na tabela."""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM usuarios")
            users = cursor.fetchall()
            
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
                self.users_table.setItem(i, 1, QTableWidgetItem(user.nome))
                self.users_table.setItem(i, 2, QTableWidgetItem(user.email))
                self.users_table.setItem(i, 3, QTableWidgetItem(user.tipo))
                self.users_table.setItem(i, 4, QTableWidgetItem(user.empresa or ""))
                self.users_table.setItem(i, 5, QTableWidgetItem("Ativo" if user.ativo else "Inativo"))
                
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")
            
        finally:
            cursor.close()
            
    def _add_equipment(self):
        """Adiciona um novo equipamento."""
        try:
            tipo = self.equipment_type.currentText()
            empresa = self.equipment_company.text()
            localizacao = self.equipment_location.text()
            codigo = self.equipment_code.text()
            pressao = float(self.equipment_pressure.text())
            temperatura = float(self.equipment_temperature.text())
            
            if not all([tipo, empresa, localizacao, codigo]):
                QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios")
                return
                
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO equipamentos (tipo, empresa, localizacao, codigo_projeto,
                                        pressao_maxima, temperatura_maxima)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tipo, empresa, localizacao, codigo, pressao, temperatura)
            )
            
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Equipamento adicionado com sucesso")
            self._load_equipment()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar equipamento: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar equipamento: {str(e)}")
            
        finally:
            cursor.close()
            
    def _load_equipment(self):
        """Carrega os equipamentos na tabela."""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM equipamentos")
            equipment = cursor.fetchall()
            
            self.equipment_table.setRowCount(len(equipment))
            for i, item in enumerate(equipment):
                self.equipment_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
                self.equipment_table.setItem(i, 1, QTableWidgetItem(item.tipo))
                self.equipment_table.setItem(i, 2, QTableWidgetItem(item.empresa))
                self.equipment_table.setItem(i, 3, QTableWidgetItem(item.localizacao))
                self.equipment_table.setItem(i, 4, QTableWidgetItem(item.codigo_projeto))
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(item.pressao_maxima)))
                self.equipment_table.setItem(i, 6, QTableWidgetItem(str(item.temperatura_maxima)))
                self.equipment_table.setItem(i, 7, QTableWidgetItem(item.status))
                
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
            
        finally:
            cursor.close()
            
    def _add_inspection(self):
        """Adiciona uma nova inspeção."""
        try:
            equipamento_id = int(self.inspection_equipment.currentText().split(" - ")[0])
            data = self.inspection_date.date().toPyDate()
            tipo = self.inspection_type.currentText()
            engenheiro = self.inspection_engineer.text()
            resultado = self.inspection_result.currentText()
            recomendacoes = self.inspection_recommendations.toPlainText()
            
            if not all([equipamento_id, data, tipo, engenheiro, resultado]):
                QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios")
                return
                
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO inspecoes (equipamento_id, data_inspecao, tipo_inspecao,
                                     engenheiro_responsavel, resultado, recomendacoes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (equipamento_id, data, tipo, engenheiro, resultado, recomendacoes)
            )
            
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Inspeção adicionada com sucesso")
            self._load_inspections()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar inspeção: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar inspeção: {str(e)}")
            
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
            """)
            inspections = cursor.fetchall()
            
            self.inspection_table.setRowCount(len(inspections))
            for i, insp in enumerate(inspections):
                self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp.id)))
                self.inspection_table.setItem(i, 1, QTableWidgetItem(insp.codigo_projeto))
                self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp.data_inspecao)))
                self.inspection_table.setItem(i, 3, QTableWidgetItem(insp.tipo_inspecao))
                self.inspection_table.setItem(i, 4, QTableWidgetItem(insp.engenheiro_responsavel))
                self.inspection_table.setItem(i, 5, QTableWidgetItem(insp.resultado))
                self.inspection_table.setItem(i, 6, QTableWidgetItem(str(insp.proxima_inspecao or "")))
                
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
            
        finally:
            cursor.close()
            
    def _add_report(self):
        """Adiciona um novo relatório."""
        try:
            inspecao_id = int(self.report_inspection.currentText().split(" - ")[0])
            data = self.report_date.date().toPyDate()
            arquivo = self.report_file.text()
            observacoes = self.report_observations.toPlainText()
            
            if not all([inspecao_id, data, arquivo]):
                QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios")
                return
                
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO relatorios (inspecao_id, data_emissao, link_arquivo, observacoes)
                VALUES (?, ?, ?, ?)
                """,
                (inspecao_id, data, arquivo, observacoes)
            )
            
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Relatório adicionado com sucesso")
            self._load_reports()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar relatório: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar relatório: {str(e)}")
            
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
            """)
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