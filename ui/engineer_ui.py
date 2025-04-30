from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QToolButton, QMenu
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from ui.styles import Styles
from ui.modals import InspectionModal, ReportModal
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController
from controllers.equipment_controller import EquipmentController
from controllers.database_models import DatabaseModels
from controllers.auth_controller import AuthController

class EngineerWindow(QMainWindow):
    def __init__(self, auth_controller, usuario_id):
        super().__init__()
        self.auth_controller = auth_controller
        self.usuario_id = usuario_id
        self.usuario = auth_controller.get_usuario_atual()
        
        # Configurar os controllers
        self.db_models = DatabaseModels()
        self.equipment_controller = EquipmentController(self.db_models)
        self.inspection_controller = InspectionController(self.db_models)
        self.report_controller = ReportController(self.db_models)
        
        self.is_dark = True
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Sistema de Inspeções NR-13 - Engenheiro")
        self.setMinimumSize(800, 600)
        
        # Definir ícone da janela com o logo da empresa
        self.setWindowIcon(QIcon("ui/CTREINA_LOGO.png"))
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Barra superior
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignRight)
        
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
        top_bar.addWidget(self.settings_button)
        
        layout.addLayout(top_bar)
        
        # Título
        title = QLabel("Painel do Engenheiro")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.add_inspection_button = QPushButton("Adicionar Inspeção")
        self.add_inspection_button.setMinimumHeight(36)
        self.add_inspection_button.clicked.connect(self.add_inspection)
        buttons_layout.addWidget(self.add_inspection_button)
        
        self.add_report_button = QPushButton("Adicionar Relatório")
        self.add_report_button.setMinimumHeight(36)
        self.add_report_button.clicked.connect(self.add_report)
        buttons_layout.addWidget(self.add_report_button)
        
        layout.addLayout(buttons_layout)
        
        # Tabelas
        tables_layout = QHBoxLayout()
        
        # Tabela de inspeções
        self.inspection_table = QTableWidget()
        self.inspection_table.setColumnCount(6)
        self.inspection_table.setHorizontalHeaderLabels([
            "ID", "Equipamento", "Data", "Tipo", "Cliente", "Resultado"
        ])
        self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_inspections()
        tables_layout.addWidget(self.inspection_table)
        
        # Tabela de relatórios
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "ID", "Inspeção", "Data", "Arquivo"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_reports()
        tables_layout.addWidget(self.report_table)
        
        layout.addLayout(tables_layout)
        
        # Aplicar tema
        self.apply_theme()
        
    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.theme_action.setChecked(self.is_dark)
        self.apply_theme()
        
    def apply_theme(self):
        """Aplica o tema atual"""
        if self.is_dark:
            self.setStyleSheet(Styles.get_dark_theme())
            self.theme_action.setText("Tema Claro")
        else:
            self.setStyleSheet(Styles.get_light_theme())
            self.theme_action.setText("Tema Escuro")
            
    def load_inspections(self):
        """Carrega as inspeções na tabela"""
        inspections = self.inspection_controller.get_inspections_by_engineer(self.usuario_id)
        self.inspection_table.setRowCount(len(inspections))
        
        for i, insp in enumerate(inspections):
            self.inspection_table.setItem(i, 0, QTableWidgetItem(str(insp['id'])))
            self.inspection_table.setItem(i, 1, QTableWidgetItem(insp['equipamento']))
            self.inspection_table.setItem(i, 2, QTableWidgetItem(str(insp['data'])))
            self.inspection_table.setItem(i, 3, QTableWidgetItem(insp['tipo']))
            self.inspection_table.setItem(i, 4, QTableWidgetItem(insp['cliente']))
            self.inspection_table.setItem(i, 5, QTableWidgetItem(insp['resultado']))
            
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        reports = self.report_controller.get_reports_by_engineer(self.usuario_id)
        self.report_table.setRowCount(len(reports))
        
        for i, rep in enumerate(reports):
            self.report_table.setItem(i, 0, QTableWidgetItem(str(rep['id'])))
            self.report_table.setItem(i, 1, QTableWidgetItem(str(rep['inspecao_id'])))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(rep['data'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(rep['arquivo']))
            
    def add_inspection(self):
        """Abre a janela modal para adicionar inspeção"""
        modal = InspectionModal(self, self.is_dark)
        
        # Carrega os equipamentos disponíveis no combobox
        equipment = self.inspection_controller.get_available_equipment()
        for equip in equipment:
            modal.equipamento_input.addItem(f"{equip['id']} - {equip['tipo']} ({equip['cliente']})")
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.inspection_controller.criar_inspecao(
                equipamento_id=data['equipamento_id'],
                data=data['data'],
                tipo=data['tipo'],
                engenheiro=self.usuario_id,
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
        
        # Carrega as inspeções do engenheiro no combobox
        inspections = self.inspection_controller.get_inspections_by_engineer(self.usuario_id)
        for insp in inspections:
            modal.inspecao_input.addItem(f"{insp['id']} - {insp['tipo']} ({insp['data']})")
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.report_controller.criar_relatorio(
                inspecao_id=data['inspecao_id'],
                data=data['data'],
                arquivo=data['arquivo'],
                observacoes=data['observacoes']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_reports()
            else:
                QMessageBox.warning(self, "Erro", message) 