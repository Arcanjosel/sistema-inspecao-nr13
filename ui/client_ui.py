"""
Interface gráfica do cliente do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QToolButton, QMenu, QHeaderView,
    QDialog
)
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import datetime, timedelta
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.styles import Styles
from PyQt5.QtGui import QIcon
from ui.modals import InspectionModal, ReportModal
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController

logger = logging.getLogger(__name__)

class ClientWindow(QMainWindow):
    """
    Janela principal do cliente.
    """
    
    def __init__(self, auth_controller: AuthController, user_id: int, company: str):
        super().__init__()
        self.auth_controller = auth_controller
        self.db_models = DatabaseModels()
        self.user_id = user_id
        self.company = company
        self.inspection_controller = InspectionController()
        self.report_controller = ReportController()
        self.is_dark = True
        self.initUI()
        self.apply_theme()
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle('Sistema de Inspeções NR-13 - Cliente')
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Título
        title = QLabel(f"Painel do Cliente - {self.company}")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Abas
        self.tabs = QTabWidget()
        
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
        
        # Adiciona as abas
        self.tabs.addTab(inspection_tab, "Inspeções")
        self.tabs.addTab(report_tab, "Relatórios")
        
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
            
    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.theme_action.setChecked(self.is_dark)
        self.apply_theme()
        
    def load_inspections(self):
        """Carrega as inspeções na tabela"""
        inspections = self.inspection_controller.get_inspections_by_company(self.company)
        self.inspection_table.setRowCount(len(inspections))
        
        for i, insp in enumerate(inspections):
            self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp['id'])))
            self.inspection_table.setItem(i, 1, QTableWidgetItem(insp['equipamento']))
            self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp['data'])))
            self.inspection_table.setItem(i, 3, QTableWidgetItem(insp['tipo']))
            self.inspection_table.setItem(i, 4, QTableWidgetItem(insp['engenheiro']))
            self.inspection_table.setItem(i, 5, QTableWidgetItem(insp['resultado']))
            
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        reports = self.report_controller.get_reports_by_company(self.company)
        self.report_table.setRowCount(len(reports))
        
        for i, rep in enumerate(reports):
            self.report_table.setItem(i, 0, QTableWidgetItem(str(rep['id'])))
            self.report_table.setItem(i, 1, QTableWidgetItem(str(rep['inspecao_id'])))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(rep['data_emissao'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(rep['link_arquivo']))
            
    def add_inspection(self):
        """Abre a janela modal para adicionar inspeção"""
        modal = InspectionModal(self, self.is_dark)
        
        # Carrega os equipamentos da empresa no combobox
        equipment = self.inspection_controller.get_equipment_by_company(self.company)
        for equip in equipment:
            modal.equipamento_input.addItem(f"{equip['id']} - {equip['tipo']}")
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.inspection_controller.criar_inspecao(
                equipamento_id=data['equipamento_id'],
                data=data['data'],
                tipo=data['tipo'],
                engenheiro=data['engenheiro'],
                resultado=data['resultado'],
                recomendacoes=data['recomendacoes']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_inspections()
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def add_report(self):
        """Abre a janela modal para adicionar relatório"""
        modal = ReportModal(self, self.is_dark)
        
        # Carrega as inspeções da empresa no combobox
        inspections = self.inspection_controller.get_inspections_by_company(self.company)
        for insp in inspections:
            modal.inspecao_input.addItem(f"{insp['id']} - {insp['tipo']} ({insp['data']})")
            
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
                self.load_reports()
            else:
                QMessageBox.warning(self, "Erro", message) 