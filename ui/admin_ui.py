"""
Interface gráfica do administrador do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QFileDialog, QToolButton, QMenu,
    QHeaderView, QDialog
)
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import datetime
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.styles import Styles
from PyQt5.QtGui import QIcon, QPixmap
from ui.modals import UserModal, EquipmentModal, InspectionModal, ReportModal
from controllers.equipment_controller import EquipmentController
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController

logger = logging.getLogger(__name__)

class AdminWindow(QMainWindow):
    """
    Janela principal do administrador.
    """
    
    def __init__(self, auth_controller: AuthController):
        super().__init__()
        self.auth_controller = auth_controller
        self.db_models = DatabaseModels()
        self.equipment_controller = EquipmentController()
        self.inspection_controller = InspectionController()
        self.report_controller = ReportController()
        self.is_dark = True
        self.initUI()
        self.apply_theme()
        
    def get_tab_icon(self, filename):
        pixmap = QPixmap(f"ui/{filename}")
        if self.is_dark:
            # Inverte as cores do ícone para o modo escuro
            img = pixmap.toImage()
            img.invertPixels()
            pixmap = QPixmap.fromImage(img)
        return QIcon(pixmap)

    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle('Sistema de Inspeções NR-13 - Administrador')
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Título
        title = QLabel("Painel do Administrador")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Abas
        self.tabs = QTabWidget()
        
        # Aba de Usuários
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        
        # Botões de ação para usuários
        user_buttons = QHBoxLayout()
        self.add_user_button = QPushButton("Adicionar Usuário")
        self.add_user_button.setMinimumHeight(36)
        self.add_user_button.clicked.connect(self.add_user)
        user_buttons.addWidget(self.add_user_button)
        user_layout.addLayout(user_buttons)
        
        # Tabela de usuários
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Tipo", "Empresa"
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_users()
        user_layout.addWidget(self.user_table)
        
        # Aba de Equipamentos
        equipment_tab = QWidget()
        equipment_layout = QVBoxLayout(equipment_tab)
        
        # Botões de ação para equipamentos
        equipment_buttons = QHBoxLayout()
        self.add_equipment_button = QPushButton("Adicionar Equipamento")
        self.add_equipment_button.setMinimumHeight(36)
        self.add_equipment_button.clicked.connect(self.add_equipment)
        equipment_buttons.addWidget(self.add_equipment_button)
        equipment_layout.addLayout(equipment_buttons)
        
        # Tabela de equipamentos
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(5)
        self.equipment_table.setHorizontalHeaderLabels([
            "ID", "Tipo", "Empresa", "Última Inspeção", "Status"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_equipment()
        equipment_layout.addWidget(self.equipment_table)
        
        # Aba de Inspeções
        inspection_tab = QWidget()
        inspection_layout = QVBoxLayout(inspection_tab)
        
        # Botões de ação para inspeções
        inspection_buttons = QHBoxLayout()
        self.add_inspection_button = QPushButton("Adicionar Inspeção")
        self.add_inspection_button.setMinimumHeight(36)
        self.add_inspection_button.clicked.connect(self.add_inspection)
        inspection_buttons.addWidget(self.add_inspection_button)
        inspection_layout.addLayout(inspection_buttons)
        
        # Tabela de inspeções
        self.inspection_table = QTableWidget()
        self.inspection_table.setColumnCount(6)
        self.inspection_table.setHorizontalHeaderLabels([
            "ID", "Equipamento", "Data", "Tipo", "Engenheiro", "Resultado"
        ])
        self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_inspections()
        inspection_layout.addWidget(self.inspection_table)
        
        # Aba de Relatórios
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)
        
        # Botões de ação para relatórios
        report_buttons = QHBoxLayout()
        self.add_report_button = QPushButton("Adicionar Relatório")
        self.add_report_button.setMinimumHeight(36)
        self.add_report_button.clicked.connect(self.add_report)
        report_buttons.addWidget(self.add_report_button)
        report_layout.addLayout(report_buttons)
        
        # Tabela de relatórios
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "ID", "Inspeção", "Data", "Arquivo"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_reports()
        report_layout.addWidget(self.report_table)
        
        # Adiciona as abas com ícones
        self.tabs.addTab(user_tab, self.get_tab_icon("user.png"), "")
        self.tabs.addTab(equipment_tab, self.get_tab_icon("equipamentos.png"), "")
        self.tabs.addTab(inspection_tab, self.get_tab_icon("inspecoes.png"), "")
        self.tabs.addTab(report_tab, self.get_tab_icon("relatorios.png"), "")
        self.tabs.setIconSize(QSize(35, 35))
        layout.addWidget(self.tabs)
        
        # Barra inferior com botão de configurações
        bottom_bar = QHBoxLayout()
        bottom_bar.setAlignment(Qt.AlignRight)
        
        # Botão de configurações
        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon("icons/settings.png"))
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setToolTip("Configurações")
        self.settings_button.setPopupMode(QToolButton.InstantPopup)
        
        # Menu de configurações
        settings_menu = QMenu()
        self.theme_action = settings_menu.addAction("Tema Claro")
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(self.is_dark)
        self.theme_action.triggered.connect(self.toggle_theme)
        
        self.settings_button.setMenu(settings_menu)
        bottom_bar.addWidget(self.settings_button)
        
        layout.addLayout(bottom_bar)
        
    def apply_theme(self):
        """Aplica o tema atual"""
        if self.is_dark:
            self.setStyleSheet(Styles.get_dark_theme())
            self.theme_action.setText("Tema Claro")
        else:
            self.setStyleSheet(Styles.get_light_theme())
            self.theme_action.setText("Tema Escuro")
        # Atualiza os ícones das abas ao trocar o tema
        self.tabs.setTabIcon(0, self.get_tab_icon("user.png"))
        self.tabs.setTabIcon(1, self.get_tab_icon("equipamentos.png"))
        self.tabs.setTabIcon(2, self.get_tab_icon("inspecoes.png"))
        self.tabs.setTabIcon(3, self.get_tab_icon("relatorios.png"))
            
    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.theme_action.setChecked(self.is_dark)
        self.apply_theme()
        
    def load_users(self):
        """Carrega os usuários na tabela"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM usuarios")
            users = cursor.fetchall()
            
            self.user_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
                self.user_table.setItem(i, 1, QTableWidgetItem(user.nome))
                self.user_table.setItem(i, 2, QTableWidgetItem(user.email))
                self.user_table.setItem(i, 3, QTableWidgetItem(user.tipo_acesso))
                self.user_table.setItem(i, 4, QTableWidgetItem(user.empresa or ""))
                
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")
            
        finally:
            cursor.close()
            
    def load_equipment(self):
        """Carrega os equipamentos na tabela"""
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
                self.equipment_table.setItem(i, 5, QTableWidgetItem(item.status))
                
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
            
        finally:
            cursor.close()
            
    def add_user(self):
        """Abre a janela modal para adicionar usuário"""
        modal = UserModal(self, self.is_dark)
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.auth_controller.criar_usuario(
                nome=data['nome'],
                email=data['email'],
                senha=data['senha'],
                tipo_acesso=data['tipo'],
                empresa=data['empresa']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_users()
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def add_equipment(self):
        """Abre a janela modal para adicionar equipamento"""
        modal = EquipmentModal(self, self.is_dark)
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.equipment_controller.criar_equipamento(
                tipo=data['tipo'],
                empresa=data['empresa'],
                localizacao=data['localizacao'],
                codigo=data['codigo'],
                pressao=data['pressao'],
                temperatura=data['temperatura']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_equipment()
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def add_inspection(self):
        """Abre a janela modal para adicionar inspeção"""
        modal = InspectionModal(self, self.is_dark)
        
        # Carrega os equipamentos no combobox
        equipment = self.equipment_controller.get_all_equipment()
        for equip in equipment:
            modal.equipamento_input.addItem(f"{equip['id']} - {equip['tipo']} ({equip['empresa']})")
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.inspection_controller.criar_inspecao(
                equipamento_id=data['equipamento_id'],
                data_inspecao=data['data'],
                tipo_inspecao=data['tipo'],
                engenheiro=data['engenheiro'],
                resultado=data['resultado'],
                recomendacoes=data['recomendacoes']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def add_report(self):
        """Abre a janela modal para adicionar relatório"""
        modal = ReportModal(self, self.is_dark)
        
        # Carrega as inspeções no combobox
        inspections = self.inspection_controller.get_all_inspections()
        for insp in inspections:
            modal.inspecao_input.addItem(f"{insp['id']} - {insp['tipo_inspecao']} ({insp['data_inspecao']})")
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.report_controller.criar_relatorio(
                inspecao_id=data['inspecao_id'],
                data_emissao=data['data'],
                link_arquivo=data['link_arquivo'],
                observacoes=data['observacoes']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def load_inspections(self):
        """Carrega as inspeções na tabela"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.id, e.tipo, i.data_inspecao, i.tipo_inspecao, u.nome, i.resultado
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON i.engenheiro_id = u.id
            """)
            inspections = cursor.fetchall()
            
            self.inspection_table.setRowCount(len(inspections))
            for i, insp in enumerate(inspections):
                self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp[0])))
                self.inspection_table.setItem(i, 1, QTableWidgetItem(insp[1]))
                self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp[2])))
                self.inspection_table.setItem(i, 3, QTableWidgetItem(insp[3]))
                self.inspection_table.setItem(i, 4, QTableWidgetItem(insp[4]))
                self.inspection_table.setItem(i, 5, QTableWidgetItem(insp[5]))
                
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
            
        finally:
            cursor.close()
            
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, i.id, r.data_emissao, r.link_arquivo
                FROM relatorios r
                JOIN inspecoes i ON r.inspecao_id = i.id
            """)
            reports = cursor.fetchall()
            
            self.report_table.setRowCount(len(reports))
            for i, rep in enumerate(reports):
                self.report_table.setItem(i, 0, QTableWidgetItem(str(rep[0])))
                self.report_table.setItem(i, 1, QTableWidgetItem(str(rep[1])))
                self.report_table.setItem(i, 2, QTableWidgetItem(str(rep[2])))
                self.report_table.setItem(i, 3, QTableWidgetItem(rep[3]))
                
        except Exception as e:
            logger.error(f"Erro ao carregar relatórios: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar relatórios: {str(e)}")
            
        finally:
            cursor.close() 