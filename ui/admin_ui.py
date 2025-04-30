"""
Interface gráfica do administrador do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QFileDialog, QToolButton, QMenu,
    QHeaderView, QDialog, QGridLayout, QFormLayout
)
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import datetime
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.styles import Styles
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from ui.modals import UserModal, EquipmentModal, InspectionModal, ReportModal
from controllers.equipment_controller import EquipmentController
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController
import traceback
import os

logger = logging.getLogger(__name__)

class AdminWindow(QMainWindow):
    """
    Janela principal do administrador.
    """
    
    def __init__(self, auth_controller: AuthController):
        try:
            logger.debug("Iniciando construtor do AdminWindow")
            super().__init__()
            self.auth_controller = auth_controller
            logger.debug("Criando instância do DatabaseModels")
            self.db_models = DatabaseModels()
            logger.debug("Criando instância do EquipmentController")
            self.equipment_controller = EquipmentController(self.db_models)
            logger.debug("Criando instância do InspectionController")
            self.inspection_controller = InspectionController(self.db_models)
            logger.debug("Criando instância do ReportController")
            self.report_controller = ReportController(self.db_models)
            self.is_dark = True
            
            # Definir ícones SVG
            self.icons = {
                'add': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>''',
                'edit': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>''',
                'disable': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                </svg>''',
                'enable': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="16"></line>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                </svg>''',
                'delete': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>''',
                'browse': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="16"></line>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                </svg>''',
                'user': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>''',
                'equipment': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="7"></circle>
                    <circle cx="12" cy="12" r="3"></circle>
                    <line x1="12" y1="5" x2="12" y2="1"></line>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="5" y1="12" x2="1" y2="12"></line>
                    <line x1="19" y1="12" x2="23" y2="12"></line>
                </svg>''',
                'inspection': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9 12l2 2 4-4"></path>
                </svg>''',
                'report': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>'''
            }
            
            logger.debug("Iniciando setup da UI")
            self.initUI()
            logger.debug("Aplicando tema")
            self.apply_theme()
            logger.info("AdminWindow inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar AdminWindow: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar janela: {str(e)}")
            raise

    def create_icon_from_svg(self, svg_str):
        """Cria um QIcon a partir de uma string SVG"""
        # Substituir currentColor pela cor baseada no tema
        if self.is_dark:
            svg_str = svg_str.replace("currentColor", "white")
        else:
            svg_str = svg_str.replace("currentColor", "#333333")
            
        svg_bytes = svg_str.encode('utf-8')
        pixmap = QPixmap()
        pixmap.loadFromData(svg_bytes)
        return QIcon(pixmap)

    def get_tab_icon(self, icon_name):
        """Retorna o ícone apropriado para a aba usando o dicionário de SVGs"""
        try:
            logger.debug(f"Obtendo ícone: {icon_name}")
            
            # Mapear nome do ícone para chave no dicionário de ícones
            icon_key = None
            if icon_name == "user.png":
                icon_key = 'user'
            elif icon_name == "equipamentos.png":
                icon_key = 'equipment'
            elif icon_name == "inspecoes.png":
                icon_key = 'inspection'
            elif icon_name == "relatorios.png":
                icon_key = 'report'
            
            # Se temos um ícone SVG, usar ele
            if icon_key and icon_key in self.icons:
                return self.create_icon_from_svg(self.icons[icon_key])
                
            # Caso contrário, tentar carregar do arquivo
            pixmap = QPixmap(f"ui/{icon_name}")
            if not pixmap.isNull():
                if self.is_dark:
                    # Inverte as cores do ícone para o modo escuro
                    img = pixmap.toImage()
                    img.invertPixels()
                    pixmap = QPixmap.fromImage(img)
                return QIcon(pixmap)
        except Exception as e:
            logger.warning(f"Erro ao carregar ícone {icon_name}: {str(e)}")
            
        # Se não conseguir carregar o ícone, usa um ícone padrão do Qt
        if icon_name == "user.png":
            return QIcon.fromTheme("user", QIcon(":/icons/user.png"))
        elif icon_name == "equipamentos.png":
            return QIcon.fromTheme("settings", QIcon(":/icons/settings.png"))
        elif icon_name == "inspecoes.png":
            return QIcon.fromTheme("document", QIcon(":/icons/document.png"))
        elif icon_name == "relatorios.png":
            return QIcon.fromTheme("document-save", QIcon(":/icons/document-save.png"))
        else:
            return QIcon()
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        try:
            logger.debug("Iniciando setup da interface")
            self.setWindowTitle("Administração do Sistema")
            self.resize(1024, 768)
            
            # Definir ícone da janela com o logo da empresa
            self.setWindowIcon(QIcon("ui/CTREINA_LOGO.png"))
            
            # Widget central
            logger.debug("Criando widget central")
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout principal
            layout = QVBoxLayout(central_widget)
            layout.setSpacing(16)
            layout.setContentsMargins(24, 24, 24, 24)
            
            # Container do título com logo
            title_container = QHBoxLayout()
            
            # Logo
            logo_label = QLabel()
            logo_pixmap = QPixmap("ui/CTREINA_LOGO.png")
            logo_label.setPixmap(logo_pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            title_container.addWidget(logo_label)
            
            # Título
            title = QLabel("Painel do Administrador")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            title_container.addWidget(title)
            title_container.addStretch()
            
            layout.addLayout(title_container)
            
            # Abas
            logger.debug("Criando abas")
            self.tabs = QTabWidget()
            
            # Aba de Usuários
            logger.debug("Configurando aba de usuários")
            users_tab = QWidget()
            user_layout = QVBoxLayout(users_tab)
            
            # Container para botões e barra de pesquisa
            top_container = QHBoxLayout()
            
            # Container para botões (lado esquerdo)
            buttons_container = QHBoxLayout()
            
            # Botão Adicionar
            self.add_user_button = QPushButton("Adicionar Usuário")
            self.add_user_button.setIcon(self.create_icon_from_svg(self.icons['add']))
            self.add_user_button.setIconSize(QSize(24, 24))
            self.add_user_button.setMinimumHeight(32)
            self.add_user_button.setFixedWidth(160)
            self.add_user_button.clicked.connect(self.add_user)
            self.add_user_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            buttons_container.addWidget(self.add_user_button)
            
            # Botão Editar
            self.edit_user_button = QPushButton("Editar Usuário")
            self.edit_user_button.setIcon(self.create_icon_from_svg(self.icons['edit']))
            self.edit_user_button.setIconSize(QSize(24, 24))
            self.edit_user_button.setMinimumHeight(32)
            self.edit_user_button.setFixedWidth(160)
            self.edit_user_button.clicked.connect(self.edit_selected_user)
            self.edit_user_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            buttons_container.addWidget(self.edit_user_button)
            
            # Botão Ativar/Desativar
            self.toggle_user_button = QPushButton("Selecione um usuário")
            self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['disable']))
            self.toggle_user_button.setIconSize(QSize(24, 24))
            self.toggle_user_button.setMinimumHeight(32)
            self.toggle_user_button.setFixedWidth(160)
            self.toggle_user_button.clicked.connect(self.toggle_selected_user)
            self.toggle_user_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            buttons_container.addWidget(self.toggle_user_button)
            
            # Botão Excluir Permanentemente
            self.remove_user_button = QPushButton("Excluir Permanentemente")
            self.remove_user_button.setIcon(self.create_icon_from_svg(self.icons['delete']))
            self.remove_user_button.setIconSize(QSize(24, 24))
            self.remove_user_button.setMinimumHeight(32)
            self.remove_user_button.setFixedWidth(180)
            self.remove_user_button.clicked.connect(self.remove_selected_user)
            self.remove_user_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            buttons_container.addWidget(self.remove_user_button)
            
            # Adiciona o container de botões ao container principal
            top_container.addLayout(buttons_container)
            
            # Adiciona um espaçador expansível
            top_container.addStretch()
            
            # Container para barra de pesquisa (lado direito)
            search_container = QHBoxLayout()
            
            # Barra de pesquisa com autocompletar
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Pesquisar usuários...")
            self.search_input.setMinimumWidth(200)
            self.search_input.setMaximumWidth(300)
            self.search_input.setMinimumHeight(32)
            self.search_input.textChanged.connect(self.filter_users)
            
            # Estilo da barra de pesquisa
            self.search_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 5px 10px;
                    background: #333;
                    color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
            """)
            
            search_container.addWidget(self.search_input)
            top_container.addLayout(search_container)
            
            # Adiciona o container principal ao layout da aba
            user_layout.addLayout(top_container)
            
            # Tabela de usuários
            self.user_table = QTableWidget()
            self.user_table.setColumnCount(5)  # Reduzido para 5 colunas
            self.user_table.setHorizontalHeaderLabels([
                "ID", "Nome", "Email", "Tipo Acesso", "Status"
            ])
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.user_table.setSelectionMode(QTableWidget.SingleSelection)
            self.user_table.setAlternatingRowColors(True)
            self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Desabilita edição direta
            self.user_table.verticalHeader().setVisible(False)  # Oculta o cabeçalho vertical
            # Conecta o evento de seleção da tabela
            self.user_table.itemSelectionChanged.connect(self.update_toggle_button)
            logger.debug("Carregando usuários")
            self.load_users()
            user_layout.addWidget(self.user_table)
            
            # Aba de Equipamentos
            logger.debug("Configurando aba de equipamentos")
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
            self.equipment_table.setColumnCount(11)
            self.equipment_table.setHorizontalHeaderLabels([
                "ID", "Tag", "Categoria", "Empresa ID", "Fabricante", "Ano Fabricação", "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido", "Status"
            ])
            self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            logger.debug("Carregando equipamentos")
            self.load_equipment()
            equipment_layout.addWidget(self.equipment_table)
            
            # Aba de Inspeções
            logger.debug("Configurando aba de inspeções")
            inspection_tab = QWidget()
            inspection_layout = QVBoxLayout(inspection_tab)
            
            # Título da aba
            inspection_title = QLabel("Gestão de Inspeções")
            inspection_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
            inspection_layout.addWidget(inspection_title)
            
            # Container para busca e botões
            top_container = QHBoxLayout()
            
            # Botões de ação
            buttons_container = QHBoxLayout()
            buttons_container.setSpacing(10)
            
            # Botão Adicionar Inspeção
            self.add_inspection_btn = QPushButton("Adicionar Inspeção")
            self.add_inspection_btn.setIcon(self.create_icon_from_svg(self.icons['add']))
            self.add_inspection_btn.setIconSize(QSize(24, 24))
            self.add_inspection_btn.setMinimumHeight(36)
            self.add_inspection_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.add_inspection_btn.clicked.connect(self.add_inspection)
            buttons_container.addWidget(self.add_inspection_btn)
            
            # Adiciona os botões ao container principal
            top_container.addLayout(buttons_container)
            
            # Adiciona um espaçador expansível
            top_container.addStretch()
            
            # Barra de pesquisa para inspeções
            search_container = QHBoxLayout()
            self.insp_search_input = QLineEdit()
            self.insp_search_input.setPlaceholderText("Pesquisar inspeções...")
            self.insp_search_input.setMinimumWidth(200)
            self.insp_search_input.setMaximumWidth(300)
            self.insp_search_input.setMinimumHeight(32)
            self.insp_search_input.textChanged.connect(self.filter_inspections)
            
            # Estilo da barra de pesquisa
            self.insp_search_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 5px 10px;
                    background: #333;
                    color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
            """)
            
            search_container.addWidget(self.insp_search_input)
            top_container.addLayout(search_container)
            
            # Adiciona o container principal ao layout da aba
            inspection_layout.addLayout(top_container)
            
            # Lista de inspeções
            self.inspection_table = QTableWidget()
            self.inspection_table.setColumnCount(6)
            self.inspection_table.setHorizontalHeaderLabels([
                "ID", "Equipamento", "Data", "Tipo", "Engenheiro", "Resultado"
            ])
            self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.inspection_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.inspection_table.setSelectionMode(QTableWidget.SingleSelection)
            self.inspection_table.setAlternatingRowColors(True)
            self.inspection_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.inspection_table.verticalHeader().setVisible(False)
            
            # Carrega as inspeções
            self.load_inspections()
            inspection_layout.addWidget(self.inspection_table)
            
            # Botões de ação para inspeções
            bottom_buttons = QHBoxLayout()
            
            # Botão Editar
            self.edit_inspection_btn = QPushButton("Editar")
            self.edit_inspection_btn.setIcon(self.create_icon_from_svg(self.icons['edit']))
            self.edit_inspection_btn.setIconSize(QSize(24, 24))
            self.edit_inspection_btn.setMinimumHeight(36)
            self.edit_inspection_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0069d9;
                }
            """)
            self.edit_inspection_btn.clicked.connect(self.edit_selected_inspection)
            bottom_buttons.addWidget(self.edit_inspection_btn)
            
            # Botão Excluir
            self.delete_inspection_btn = QPushButton("Excluir")
            self.delete_inspection_btn.setIcon(self.create_icon_from_svg(self.icons['delete']))
            self.delete_inspection_btn.setIconSize(QSize(24, 24))
            self.delete_inspection_btn.setMinimumHeight(36)
            self.delete_inspection_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.delete_inspection_btn.clicked.connect(self.delete_selected_inspection)
            bottom_buttons.addWidget(self.delete_inspection_btn)
            
            # Botão Gerar Relatório
            self.generate_report_btn = QPushButton("Gerar Relatório")
            self.generate_report_btn.setIcon(self.create_icon_from_svg(self.icons['report']))
            self.generate_report_btn.setIconSize(QSize(24, 24))
            self.generate_report_btn.setMinimumHeight(36)
            self.generate_report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            self.generate_report_btn.clicked.connect(self.generate_report_from_inspection)
            bottom_buttons.addWidget(self.generate_report_btn)
            
            inspection_layout.addLayout(bottom_buttons)
            
            # Aba de Relatórios
            logger.debug("Configurando aba de relatórios")
            report_tab = QWidget()
            report_layout = QVBoxLayout(report_tab)
            
            # Container para busca e filtros
            search_container = QHBoxLayout()
            search_container.setContentsMargins(0, 0, 0, 0)
            
            # Container para botão (lado esquerdo)
            button_container = QHBoxLayout()
            
            # Botão Adicionar Relatório
            self.add_report_btn = QPushButton("Adicionar Relatório")
            self.add_report_btn.setIcon(self.create_icon_from_svg(self.icons['add']))
            self.add_report_btn.setIconSize(QSize(24, 24))
            self.add_report_btn.setMinimumHeight(36)
            self.add_report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.add_report_btn.clicked.connect(self.show_add_report_modal)
            button_container.addWidget(self.add_report_btn)
            button_container.addStretch()
            
            search_container.addLayout(button_container, stretch=1)
            
            # Container para barra de pesquisa (lado direito)
            search_box = QHBoxLayout()
            search_box.setContentsMargins(0, 0, 0, 0)
            
            # Barra de pesquisa
            self.report_search_input = QLineEdit()
            self.report_search_input.setPlaceholderText("Pesquisar relatórios...")
            self.report_search_input.setFixedWidth(250)
            self.report_search_input.setMinimumHeight(36)
            self.report_search_input.textChanged.connect(self.filter_reports)
            self.report_search_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 5px 10px;
                    background: #333;
                    color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
            """)
            search_box.addWidget(self.report_search_input)
            
            search_container.addLayout(search_box)
            
            report_layout.addLayout(search_container)
            
            # Tabela de relatórios
            self.report_table = QTableWidget()
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels([
                "ID", "Inspeção", "Data", "Arquivo", "Observações", "Status"
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.report_table.setSelectionMode(QTableWidget.SingleSelection)
            self.report_table.setAlternatingRowColors(True)
            self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            logger.debug("Carregando relatórios do banco de dados")
            self.load_reports()
            report_layout.addWidget(self.report_table)
            
            # Container para botões de ação
            action_buttons = QHBoxLayout()
            action_buttons.setSpacing(10)
            
            # Botão Editar
            self.edit_report_btn = QPushButton("Editar")
            self.edit_report_btn.setIcon(self.create_icon_from_svg(self.icons['edit']))
            self.edit_report_btn.setIconSize(QSize(24, 24))
            self.edit_report_btn.setMinimumHeight(36)
            self.edit_report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            self.edit_report_btn.clicked.connect(self.edit_selected_report)
            action_buttons.addWidget(self.edit_report_btn)
            
            # Botão Excluir
            self.delete_report_btn = QPushButton("Excluir")
            self.delete_report_btn.setIcon(self.create_icon_from_svg(self.icons['delete']))
            self.delete_report_btn.setIconSize(QSize(24, 24))
            self.delete_report_btn.setMinimumHeight(36)
            self.delete_report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            self.delete_report_btn.clicked.connect(self.delete_selected_report)
            action_buttons.addWidget(self.delete_report_btn)
            
            # Botão Visualizar
            self.view_report_btn = QPushButton("Visualizar")
            self.view_report_btn.setIcon(self.create_icon_from_svg(self.icons['browse']))
            self.view_report_btn.setIconSize(QSize(24, 24))
            self.view_report_btn.setMinimumHeight(36)
            self.view_report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:pressed {
                    background-color: #0f6674;
                }
            """)
            self.view_report_btn.clicked.connect(self.view_selected_report)
            action_buttons.addWidget(self.view_report_btn)
            
            # Adiciona um espaçador expansível
            action_buttons.addStretch()
            
            # Adiciona os botões ao layout
            report_layout.addLayout(action_buttons)
            
            # Adiciona as abas com ícones
            logger.debug("Adicionando abas ao TabWidget")
            self.tabs.addTab(users_tab, self.get_tab_icon("user.png"), "Usuários")
            self.tabs.addTab(equipment_tab, self.get_tab_icon("equipamentos.png"), "Equipamentos")
            self.tabs.addTab(inspection_tab, self.get_tab_icon("inspecoes.png"), "Inspeções")
            self.tabs.addTab(report_tab, self.get_tab_icon("relatorios.png"), "Relatórios")
            self.tabs.setIconSize(QSize(35, 35))
            layout.addWidget(self.tabs)
            
            # Barra inferior com botão de configurações
            logger.debug("Configurando barra inferior")
            bottom_bar = QHBoxLayout()
            bottom_bar.setAlignment(Qt.AlignRight)
            
            # Botão de tema
            self.theme_button = QPushButton()
            self.theme_button.setIcon(QIcon(os.path.join("assets", "icons", "theme.png")))
            self.theme_button.setIconSize(QSize(24, 24))
            self.theme_button.setFixedSize(36, 36)
            self.theme_button.clicked.connect(self.toggle_theme)
            bottom_bar.addWidget(self.theme_button)
            
            layout.addLayout(bottom_bar)
            
            logger.debug("Interface inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar UI: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar interface: {str(e)}")
            raise

    def apply_theme(self):
        """Aplica o tema atual"""
        try:
            if self.is_dark:
                self.setStyleSheet(Styles.get_dark_theme())
                
                # Estilos específicos para tabelas no modo escuro
                table_style = """
                    QTableWidget {
                        background-color: #232629;
                        color: #ffffff;
                        gridline-color: #3a3d40;
                        alternate-background-color: #2a2d30;
                    }
                    QHeaderView::section {
                        background-color: #2a2d30;
                        color: #ffffff;
                        padding: 8px;
                        border: 1px solid #3a3d40;
                    }
                    QTableWidget::item:selected {
                        background-color: #3a3d40;
                        color: #ffffff;
                    }
                """
                
                # Aplica estilos às tabelas
                self.user_table.setStyleSheet(table_style)
                self.equipment_table.setStyleSheet(table_style)
                self.inspection_table.setStyleSheet(table_style)
                self.report_table.setStyleSheet(table_style)
                
                # Ativa cores alternadas
                self.user_table.setAlternatingRowColors(True)
                self.equipment_table.setAlternatingRowColors(True)
                self.inspection_table.setAlternatingRowColors(True)
                self.report_table.setAlternatingRowColors(True)
            else:
                self.setStyleSheet(Styles.get_light_theme())
                
                # Estilos específicos para tabelas no modo claro
                table_style = """
                    QTableWidget {
                        background-color: #ffffff;
                        color: #000000;
                        gridline-color: #d0d0d0;
                        alternate-background-color: #f8f8f8;
                    }
                    QHeaderView::section {
                        background-color: #f0f0f0;
                        color: #000000;
                        padding: 8px;
                        border: 1px solid #d0d0d0;
                    }
                    QTableWidget::item:selected {
                        background-color: #e0e0e0;
                        color: #000000;
                    }
                """
                
                # Aplica estilos às tabelas
                self.user_table.setStyleSheet(table_style)
                self.equipment_table.setStyleSheet(table_style)
                self.inspection_table.setStyleSheet(table_style)
                self.report_table.setStyleSheet(table_style)
                
                # Ativa cores alternadas
                self.user_table.setAlternatingRowColors(True)
                self.equipment_table.setAlternatingRowColors(True)
                self.inspection_table.setAlternatingRowColors(True)
                self.report_table.setAlternatingRowColors(True)
                
            # Atualiza os ícones das abas ao trocar o tema
            self.tabs.setTabIcon(0, self.get_tab_icon("user.png"))
            self.tabs.setTabIcon(1, self.get_tab_icon("equipamentos.png"))
            self.tabs.setTabIcon(2, self.get_tab_icon("inspecoes.png"))
            self.tabs.setTabIcon(3, self.get_tab_icon("relatorios.png"))
            
            # Atualiza o botão de ativar/desativar
            self.update_toggle_button()
            
        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar tema: {str(e)}")

    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.apply_theme()
        
    def load_users(self):
        """Carrega os usuários na tabela"""
        try:
            logger.debug("Carregando usuários")
            users = self.auth_controller.get_all_users()
            self.user_table.setRowCount(len(users))
            
            for i, user in enumerate(users):
                # ID
                id_item = QTableWidgetItem(str(user['id']))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Torna não editável
                self.user_table.setItem(i, 0, id_item)
                
                # Nome
                nome_item = QTableWidgetItem(user['nome'])
                nome_item.setFlags(nome_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 1, nome_item)
                
                # Email
                email_item = QTableWidgetItem(user['email'])
                email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 2, email_item)
                
                # Tipo Acesso
                tipo_item = QTableWidgetItem(user['tipo_acesso'])
                tipo_item.setFlags(tipo_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 3, tipo_item)
                
                # Status
                status_item = QTableWidgetItem("Ativo" if user.get('ativo', 1) else "Inativo")
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 4, status_item)
                
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")
            
    def load_equipment(self):
        """Carrega os equipamentos na tabela"""
        try:
            logger.debug("Carregando equipamentos")
            equipment = self.equipment_controller.get_all_equipment()
            self.equipment_table.setRowCount(len(equipment))
            for i, item in enumerate(equipment):
                self.equipment_table.setItem(i, 0, QTableWidgetItem(str(item.get('id', ''))))
                self.equipment_table.setItem(i, 1, QTableWidgetItem(item.get('tag', '')))
                self.equipment_table.setItem(i, 2, QTableWidgetItem(item.get('categoria', '')))
                self.equipment_table.setItem(i, 3, QTableWidgetItem(str(item.get('empresa_id', ''))))
                self.equipment_table.setItem(i, 4, QTableWidgetItem(item.get('fabricante', '')))
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(item.get('ano_fabricacao', ''))))
                self.equipment_table.setItem(i, 6, QTableWidgetItem(str(item.get('pressao_projeto', ''))))
                self.equipment_table.setItem(i, 7, QTableWidgetItem(str(item.get('pressao_trabalho', ''))))
                self.equipment_table.setItem(i, 8, QTableWidgetItem(str(item.get('volume', ''))))
                self.equipment_table.setItem(i, 9, QTableWidgetItem(item.get('fluido', '')))
                status = "Ativo" if item.get('ativo', 1) else "Inativo"
                self.equipment_table.setItem(i, 10, QTableWidgetItem(status))
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
            
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
        """Abre o modal para adicionar um equipamento"""
        try:
            logger.debug("Abrindo modal para adicionar equipamento")
            modal = EquipmentModal(self, is_dark=self.is_dark)
            
            if modal.exec_():
                data = modal.get_data()
                logger.debug(f"Dados do equipamento: {data}")
                
                # Obter o ID da empresa pelo nome
                empresa_id = self.get_empresa_id_by_name(data['empresa'])
                
                # Validar e converter campos numéricos
                try:
                    ano_fabricacao = int(data['ano_fabricacao']) if data['ano_fabricacao'] else 0
                    pressao_projeto = float(data['pressao_projeto'].replace(',', '.')) if data['pressao_projeto'] else 0.0
                    pressao_trabalho = float(data['pressao_trabalho'].replace(',', '.')) if data['pressao_trabalho'] else 0.0
                    volume = float(data['volume'].replace(',', '.')) if data['volume'] else 0.0
                except ValueError as e:
                    QMessageBox.warning(self, "Dados Inválidos", 
                                        f"Valor numérico inválido: {str(e)}\n\nVerifique se os campos de pressão, volume e ano contêm apenas números.")
                    return
                
                # Criar o equipamento
                success, message = self.equipment_controller.criar_equipamento(
                    tag=data['tag'],
                    categoria=data['categoria'],
                    empresa_id=empresa_id,
                    fabricante=data['fabricante'],
                    ano_fabricacao=ano_fabricacao,
                    pressao_projeto=pressao_projeto,
                    pressao_trabalho=pressao_trabalho,
                    volume=volume,
                    fluido=data['fluido']
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_equipment()
                else:
                    QMessageBox.critical(self, "Erro", message)
        except Exception as e:
            logger.error(f"Erro ao adicionar equipamento: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar equipamento: {str(e)}")
                
    def get_empresa_id_by_name(self, empresa_nome: str) -> int:
        """Obtém o ID de uma empresa pelo nome"""
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE nome = ? AND tipo_acesso = 'cliente'", (empresa_nome,))
            row = cursor.fetchone()
            if row:
                return row[0]
            # Se não encontrar, retorna o ID do primeiro usuário (geralmente admin)
            return 1
        except Exception as e:
            logger.error(f"Erro ao buscar ID da empresa: {str(e)}")
            return 1  # Retorna ID 1 como fallback
        finally:
            cursor.close()
            
    def add_inspection(self):
        """Abre o modal para adicionar nova inspeção"""
        try:
            logging.info("Abrindo modal para adicionar nova inspeção")
            
            # Cria o modal de inspeção
            modal = InspectionModal(self, self.is_dark_mode)
            
            # Carrega equipamentos no combobox
            equipments = self.admin_controller.get_equipments()
            modal.equipamento_input.clear()
            
            for equip in equipments:
                equip_id = equip.get('id', 0)
                tag = equip.get('tag', 'Desconhecido')
                descricao = equip.get('descricao', '')
                display_text = f"{tag} - {descricao} (ID: {equip_id})"
                modal.equipamento_input.addItem(display_text, equip_id)
            
            # Carrega engenheiros no combobox do modal
            self.load_engineers_to_combo(modal.engenheiro_input)
            
            # Executa o modal
            if modal.exec_() == QDialog.Accepted:
                # Obtém os dados do formulário
                data = modal.get_data()
                logging.info(f"Dados do formulário: {data}")
                
                # Adiciona a inspeção
                result = self.inspection_controller.add_inspection(
                    equipamento_id=data['equipamento_id'],
                    data=data['data'],
                    tipo=data['tipo'],
                    engenheiro_id=data['engenheiro_id'],
                    resultado=data['resultado'],
                    recomendacoes=data['recomendacoes']
                )
                
                if result:
                    # Atualiza a tabela
                    self.load_inspections()
                    QMessageBox.information(self, "Sucesso", "Inspeção adicionada com sucesso.")
                    logging.info("Inspeção adicionada com sucesso")
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível adicionar a inspeção.")
                    logging.error("Falha ao adicionar inspeção")
        except Exception as e:
            self.show_error(f"Erro ao adicionar inspeção: {str(e)}")
            logging.error(f"Erro ao adicionar inspeção: {str(e)}")
    
    def add_report(self):
        """Abre a janela modal para adicionar relatório"""
        modal = ReportModal(self, self.is_dark)
        
        # Carrega as inspeções no combobox
        inspections = self.inspection_controller.get_all_inspections()
        for insp in inspections:
            data_str = insp['data'].strftime('%d/%m/%Y') if insp.get('data') else 'Data não definida'
            modal.inspecao_input.addItem(
                f"{insp['id']} - {insp.get('equipamento_tag', 'N/A')} ({data_str})",
                insp['id']
            )
            
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.report_controller.criar_relatorio(
                inspecao_id=data['inspecao_id'],
                data_emissao=data['data'],  # A data já vem formatada corretamente
                link_arquivo=data['arquivo'],
                observacoes=data['observacoes']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_reports()
            else:
                QMessageBox.warning(self, "Erro", message)
                
    def load_inspections(self):
        """Carrega as inspeções do banco de dados"""
        try:
            logger.debug("Carregando inspeções do banco de dados")
            
            # Limpa a tabela
            self.inspection_table.setRowCount(0)
            
            # Carrega os equipamentos para ter o mapeamento de IDs para nomes
            equipamentos = self.equipment_controller.get_all_equipment()
            equipamentos_map = {equip['id']: equip['tag'] for equip in equipamentos}
            logger.debug(f"Carregados {len(equipamentos)} equipamentos")
            
            # Busca todas as inspeções
            inspecoes = self.inspection_controller.get_all_inspections()
            
            # Preenche a tabela
            for i, inspecao in enumerate(inspecoes):
                # Adiciona uma nova linha
                self.inspection_table.insertRow(i)
                
                # ID
                id_item = QTableWidgetItem(str(inspecao.get('id', '')))
                self.inspection_table.setItem(i, 0, id_item)
                
                # Equipamento (tag)
                equip_id = inspecao.get('equipamento_id', 0)
                equip_tag = equipamentos_map.get(equip_id, f"ID: {equip_id}")
                equip_item = QTableWidgetItem(equip_tag)
                self.inspection_table.setItem(i, 1, equip_item)
                
                # Data
                data_str = inspecao.get('data_inspecao', '')
                if data_str:
                    if isinstance(data_str, datetime):
                        data_str = data_str.strftime('%d/%m/%Y')
                    elif isinstance(data_str, str) and len(data_str) > 10:
                        # Assume formato ISO
                        try:
                            data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                            data_str = data_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            pass
                data_item = QTableWidgetItem(data_str)
                self.inspection_table.setItem(i, 2, data_item)
                
                # Tipo
                tipo_item = QTableWidgetItem(inspecao.get('tipo_inspecao', ''))
                self.inspection_table.setItem(i, 3, tipo_item)
                
                # Engenheiro (nome)
                eng_nome = inspecao.get('engenheiro_nome', f"ID: {inspecao.get('engenheiro_id', 0)}")
                eng_item = QTableWidgetItem(eng_nome)
                self.inspection_table.setItem(i, 4, eng_item)
                
                # Resultado
                resultado_item = QTableWidgetItem(inspecao.get('resultado', ''))
                self.inspection_table.setItem(i, 5, resultado_item)
            
            logger.debug(f"Carregadas {len(inspecoes)} inspeções")
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
    
    def load_engineers_to_combo(self, combo=None):
        """Carrega os engenheiros no combobox"""
        if combo is None:
            combo = self.engineer_combo
            
        try:
            combo.clear()
            
            # Carrega os engenheiros
            engineers = self.admin_controller.get_engineers()
            
            # Adiciona os engenheiros ao combobox
            for engineer in engineers:
                engineer_id = engineer.get('id', 0)
                name = engineer.get('nome', 'Desconhecido')
                registration = engineer.get('registro', 'N/A')
                display_text = f"{name} (Registro: {registration})"
                combo.addItem(display_text, engineer_id)
                
            # Verifica se há engineers e seleciona o primeiro
            if combo.count() > 0:
                combo.setCurrentIndex(0)
            else:
                # Adiciona um item padrão se não houver engenheiros
                combo.addItem("Nenhum engenheiro disponível", 0)
                
            return True
        except Exception as e:
            self.show_error(f"Erro ao carregar engenheiros: {str(e)}")
            logging.error(f"Erro ao carregar engenheiros: {str(e)}")
            return False
    
    def load_equipment_to_combo(self, combo_box):
        """Carrega equipamentos para o combo box especificado"""
        try:
            combo_box.clear()
            equipamentos = self.equipment_controller.get_all_equipment()
            
            for equip in equipamentos:
                # Adiciona a tag e armazena o ID como dados do item
                combo_box.addItem(equip['tag'], equip['id'])
                
            logger.debug(f"Carregados {len(equipamentos)} equipamentos")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
    
    def filter_inspections(self):
        """Filtra a lista de inspeções com base no texto de pesquisa"""
        search_text = self.insp_search_input.text().lower()
        
        # Mostra todas as linhas se o texto estiver vazio
        if not search_text:
            for row in range(self.inspection_table.rowCount()):
                self.inspection_table.setRowHidden(row, False)
            return
        
        # Procura em cada linha
        for row in range(self.inspection_table.rowCount()):
            match_found = False
            
            # Procura em cada coluna da linha
            for col in range(self.inspection_table.columnCount()):
                item = self.inspection_table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            
            # Mostra ou esconde a linha com base no resultado da pesquisa
            self.inspection_table.setRowHidden(row, not match_found)
    
    def save_inspection(self):
        """Salva a inspeção atual"""
        try:
            # Obter os dados do formulário
            inspection_data = self.get_inspection_form_data()
            
            if inspection_data is None:
                return
                
            # Verificar se é uma edição ou criação
            if self.current_inspection_id:
                # Atualizar inspeção existente
                logger.debug(f"Atualizando inspeção {self.current_inspection_id}")
                success = self.inspection_controller.update_inspection(
                    self.current_inspection_id,
                    inspection_data
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Inspeção atualizada com sucesso!")
                    self.clear_inspection_form()
                    self.load_inspections()
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao atualizar inspeção.")
            else:
                # Cria uma nova inspeção
                logger.debug("Criando nova inspeção")
                success, message = self.inspection_controller.criar_inspecao(
                    equipamento_id=inspection_data['equipamento_id'],
                    engenheiro_id=inspection_data['engenheiro_id'],
                    data_inspecao=inspection_data['data_inspecao'],
                    tipo_inspecao=inspection_data['tipo_inspecao'],
                    resultado=inspection_data.get('resultado', 'pendente'),
                    recomendacoes=inspection_data.get('recomendacoes', '')
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.clear_inspection_form()
                    self.load_inspections()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao salvar inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao salvar inspeção: {str(e)}")
    
    def clear_inspection_form(self):
        """Limpa o formulário de inspeção"""
        self.insp_equipamento_combo.setCurrentIndex(0)
        self.insp_engenheiro_combo.setCurrentIndex(0)
        self.insp_data_input.setDate(QDate.currentDate())
        self.insp_tipo_combo.setCurrentIndex(0)
        self.insp_resultado_combo.setCurrentIndex(0)
        self.insp_recomendacoes_input.clear()
        
        # Remove o ID da inspeção atual
        if hasattr(self, "current_inspection_id"):
            delattr(self, "current_inspection_id")
        
        # Atualiza o título do formulário
        self.insp_form_title.setText("Nova Inspeção")
        
        # Atualiza o texto do botão
        self.insp_save_btn.setText("Salvar")
    
    def load_inspection_details(self):
        """Carrega os detalhes da inspeção selecionada no formulário"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            return
        
        # Obtém a linha selecionada
        row = selected_rows[0].row()
        
        # Obtém o ID da inspeção
        inspection_id = int(self.inspection_table.item(row, 0).text())
        
        try:
            # Busca os detalhes completos da inspeção
            inspection = self.inspection_controller.get_inspection_by_id(inspection_id)
            
            if not inspection:
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                return
            
            # Armazena o ID da inspeção atual
            self.current_inspection_id = inspection_id
            
            # Atualiza o título do formulário
            self.insp_form_title.setText(f"Editar Inspeção #{inspection_id}")
            
            # Atualiza o texto do botão
            self.insp_save_btn.setText("Atualizar")
            
            # Preenche o formulário com os dados
            
            # Seleciona o equipamento correto
            index = self.insp_equipamento_combo.findData(inspection['id_equipamento'])
            if index >= 0:
                self.insp_equipamento_combo.setCurrentIndex(index)
            
            # Seleciona o engenheiro correto
            index = self.insp_engenheiro_combo.findData(inspection['id_engenheiro'])
            if index >= 0:
                self.insp_engenheiro_combo.setCurrentIndex(index)
            
            # Define a data
            date_obj = QDate.fromString(inspection['data_inspecao'], "yyyy-MM-dd")
            self.insp_data_input.setDate(date_obj)
            
            # Seleciona o tipo
            index = self.insp_tipo_combo.findText(inspection['tipo_inspecao'])
            if index >= 0:
                self.insp_tipo_combo.setCurrentIndex(index)
            
            # Seleciona o resultado
            index = self.insp_resultado_combo.findText(inspection['resultado'])
            if index >= 0:
                self.insp_resultado_combo.setCurrentIndex(index)
            
            # Define as recomendações
            self.insp_recomendacoes_input.setPlainText(inspection['recomendacoes'])
            
        except Exception as e:
            logger.error(f"Erro ao carregar detalhes da inspeção: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Falha ao carregar detalhes da inspeção: {str(e)}")
    
    def edit_selected_inspection(self):
        """Carrega os detalhes da inspeção selecionada para edição"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para editar.")
            return
        
        # A função load_inspection_details já deve ter sido chamada pelo sinal itemSelectionChanged
        # Apenas verifica se temos um ID de inspeção definido
        if not hasattr(self, "current_inspection_id"):
            QMessageBox.warning(self, "Atenção", "Erro ao carregar inspeção para edição.")
            return
    
    def delete_selected_inspection(self):
        """Exclui a inspeção selecionada"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para excluir.")
            return
        
        # Obtém a linha selecionada
        row = selected_rows[0].row()
        
        # Obtém o ID da inspeção
        inspection_id = int(self.inspection_table.item(row, 0).text())
        
        # Confirmação
        reply = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir permanentemente esta inspeção?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.inspection_controller.delete_inspection(inspection_id)
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Inspeção excluída com sucesso!")
                    self.load_inspections()
                    self.clear_inspection_form()
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao excluir inspeção.")
            except Exception as e:
                logger.error(f"Erro ao excluir inspeção: {str(e)}")
                QMessageBox.critical(self, "Erro", f"Falha ao excluir inspeção: {str(e)}")
    
    def generate_report_from_inspection(self):
        """Gera um relatório a partir da inspeção selecionada"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para gerar o relatório.")
            return
        
        # Obtém a linha selecionada
        row = selected_rows[0].row()
        
        # Obtém o ID da inspeção
        inspection_id = int(self.inspection_table.item(row, 0).text())
        
        try:
            # Busca os detalhes da inspeção
            inspection = self.inspection_controller.get_inspection_by_id(inspection_id)
            
            if not inspection:
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                return
            
            # Muda para a aba de relatórios
            self.tabs.setCurrentIndex(3)  # Ajuste o índice conforme necessário
            
            # Preenche o formulário de relatório com dados da inspeção
            
            # Seleciona a inspeção no combo
            index = self.report_inspecao_combo.findData(inspection_id)
            if index >= 0:
                self.report_inspecao_combo.setCurrentIndex(index)
            
            # Define o título automático
            equip_name = inspection.get('equipment_tag', 'Equipamento')
            data = QDate.fromString(inspection['data_inspecao'], "yyyy-MM-dd").toString("dd/MM/yyyy")
            self.report_titulo_input.setText(f"Relatório de Inspeção - {equip_name} - {data}")
            
            # Define o tipo com base na inspeção
            index = self.report_tipo_combo.findText(inspection['tipo_inspecao'])
            if index >= 0:
                self.report_tipo_combo.setCurrentIndex(index)
            
            # Define a data do relatório como hoje
            self.report_data_input.setDate(QDate.currentDate())
            
            # Define o status como "Pendente" por padrão
            self.report_status_combo.setCurrentIndex(0)
            
            # Define as recomendações com base na inspeção
            self.report_recomendacoes_input.setPlainText(inspection['recomendacoes'])
            
            # Feedback para o usuário
            QMessageBox.information(
                self, 
                "Relatório Iniciado", 
                "Um novo relatório foi iniciado com base na inspeção selecionada.\n"
                "Complete as informações restantes e clique em Salvar."
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório a partir da inspeção: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Falha ao gerar relatório: {str(e)}")

    def edit_selected_user(self, user_id=None, force_type=None):
        """Abre o modal para editar um usuário selecionado"""
        try:
            if user_id is None:
                selected_rows = self.users_table.selectionModel().selectedRows()
                if not selected_rows:
                    QMessageBox.warning(self, "Atenção", "Selecione um usuário para editar.")
                    return
                    
                row = selected_rows[0].row()
                user_id = int(self.users_table.item(row, 0).text())
            
            # Obter dados do usuário
            users = self.auth_controller.get_all_users()
            user = next((u for u in users if u.get('id') == user_id), None)
            
            if not user:
                QMessageBox.warning(self, "Erro", f"Usuário ID {user_id} não encontrado.")
                return
                
            modal = UserModal(self, self.is_dark)
            modal.setWindowTitle("Editar Usuário")
            
            # Preencher o formulário com os dados do usuário
            modal.nome_input.setText(user.get('nome', ''))
            modal.email_input.setText(user.get('email', ''))
            
            # Adicionar "eng" ao combobox de tipo se não existir
            if force_type == "eng" and modal.tipo_input.findText("eng") < 0:
                modal.tipo_input.addItem("eng")
            
            # Selecionar o tipo correto
            tipo = force_type or user.get('tipo_acesso', '')
            tipo_idx = modal.tipo_input.findText(tipo)
            if tipo_idx >= 0:
                modal.tipo_input.setCurrentIndex(tipo_idx)
                
            modal.empresa_input.setText(user.get('empresa', ''))
            
            if modal.exec_():
                data = modal.get_data()
                
                # Se force_type está definido, garantir que o tipo seja respeitado
                if force_type:
                    tipo_acesso = force_type
                else:
                    tipo_acesso = data['tipo']
                    
                # Atualizar apenas o que foi alterado
                if data['nome'] != user.get('nome', '') or data['email'] != user.get('email', '') or \
                tipo_acesso != user.get('tipo_acesso', '') or data['empresa'] != user.get('empresa', ''):
                    # Implementar a atualização do usuário
                    QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
                    self.load_users()
                    
                    # Se estamos editando um engenheiro, atualizar a lista de engenheiros também
                    if tipo_acesso == "eng" or user.get('tipo_acesso') == "eng":
                        self.load_engineers()
                        
                else:
                    QMessageBox.information(self, "Informação", "Nenhuma alteração foi feita.")
        except Exception as e:
            logger.error(f"Erro ao editar usuário: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao editar usuário: {str(e)}")

    def toggle_selected_user(self):
        """Ativa/desativa o usuário selecionado na tabela"""
        try:
            selected_rows = self.user_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um usuário na tabela.")
                return
                
            row = selected_rows[0].row()
            user_id = int(self.user_table.item(row, 0).text())
            user_name = self.user_table.item(row, 1).text()
            is_active = self.user_table.item(row, 4).text() == "Ativo"
            
            if is_active:
                # Desativa o usuário
                success = self.auth_controller.desativar_usuario(user_id)
                if success:
                    self.load_users()  # Recarrega a tabela
                    QMessageBox.information(self, "Sucesso", f"Usuário {user_name} foi desativado com sucesso.")
                else:
                    QMessageBox.warning(self, "Erro", f"Erro ao desativar usuário {user_name}.")
            else:
                # Ativa o usuário
                success = self.auth_controller.reativar_usuario(user_id)
                if success:
                    self.load_users()  # Recarrega a tabela
                    QMessageBox.information(self, "Sucesso", f"Usuário {user_name} foi reativado com sucesso.")
                else:
                    QMessageBox.warning(self, "Erro", f"Erro ao reativar usuário {user_name}.")
                
            # Atualiza o botão após a operação
            self.update_toggle_button()
                
        except Exception as e:
            logger.error(f"Erro ao alterar status do usuário: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao alterar status do usuário: {str(e)}")

    def remove_selected_user(self):
        """Remove permanentemente o usuário selecionado na tabela"""
        try:
            selected_rows = self.user_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um usuário na tabela.")
                return
                
            row = selected_rows[0].row()
            user_id = int(self.user_table.item(row, 0).text())
            user_name = self.user_table.item(row, 1).text()
            
            # Confirmação com ícone de alerta e texto em vermelho
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle('Confirmação de Exclusão Permanente')
            msg_box.setText(f'<p style="color: red;">ATENÇÃO: Esta ação não pode ser desfeita!</p>')
            msg_box.setInformativeText(f'Tem certeza que deseja excluir permanentemente o usuário {user_name}?')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            if msg_box.exec_() == QMessageBox.Yes:
                conn = self.db_models.db.get_connection()
                cursor = conn.cursor()
                
                # Verifica se é o último admin
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM usuarios 
                    WHERE tipo_acesso = 'admin' 
                    AND id != ?
                    """, 
                    (user_id,)
                )
                admin_count = cursor.fetchone()[0]
                
                user_type = self.user_table.item(row, 3).text()
                if user_type == 'admin' and admin_count == 0:
                    QMessageBox.warning(
                        self,
                        "Erro",
                        "Não é possível excluir o último administrador do sistema!"
                    )
                    return
                
                # Exclui o usuário
                cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
                conn.commit()
                
                self.load_users()
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Usuário {user_name} foi excluído permanentemente do sistema."
                )
                
        except Exception as e:
            logger.error(f"Erro ao excluir usuário permanentemente: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao excluir usuário: {str(e)}"
            )

    def update_toggle_button(self):
        """Atualiza o botão de ativar/desativar baseado no usuário selecionado"""
        try:
            selected_rows = self.user_table.selectedItems()
            if not selected_rows:
                self.toggle_user_button.setEnabled(False)
                self.toggle_user_button.setText("Selecione um usuário")
                self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['disable']))
                self.toggle_user_button.setStyleSheet("""
                    QPushButton {
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        height: 36px;
                    }
                """)
                return
                
            row = selected_rows[0].row()
            is_active = self.user_table.item(row, 4).text() == "Ativo"
            
            if is_active:
                self.toggle_user_button.setText("Desativar Usuário")
                self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['disable']))
                self.toggle_user_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        height: 36px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #bd2130;
                    }
                """)
            else:
                self.toggle_user_button.setText("Ativar Usuário")
                self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['enable']))
                self.toggle_user_button.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        height: 36px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                    QPushButton:pressed {
                        background-color: #1e7e34;
                    }
                """)
            
            self.toggle_user_button.setEnabled(True)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar botão de ativar/desativar: {str(e)}")
            logger.error(traceback.format_exc())

    def filter_users(self, text):
        """Filtra os usuários na tabela baseado no texto de pesquisa"""
        try:
            search_text = text.lower()
            for row in range(self.user_table.rowCount()):
                should_show = False
                for col in range(self.user_table.columnCount()):
                    item = self.user_table.item(row, col)
                    if item and search_text in item.text().lower():
                        should_show = True
                        break
                self.user_table.setRowHidden(row, not should_show)
                
        except Exception as e:
            logger.error(f"Erro ao filtrar usuários: {str(e)}")
            logger.error(traceback.format_exc())

    def select_report_file(self):
        """Abre um diálogo para selecionar um arquivo para o relatório"""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
                    self, 
            "Selecionar Arquivo de Relatório",
            "",
            "Arquivos PDF (*.pdf);;Documentos (*.doc *.docx);;Imagens (*.png *.jpg *.jpeg);;Todos os Arquivos (*)",
            options=options
        )
        if filename:
            self.report_arquivo_input.setText(filename)
            
    def save_report(self):
        """Salva um novo relatório ou atualiza um existente"""
        try:
            # Valida os campos obrigatórios
            if not self.report_titulo_input.text().strip():
                QMessageBox.warning(self, "Atenção", "O título do relatório é obrigatório.")
                return
                
            if self.report_inspecao_combo.count() == 0:
                QMessageBox.warning(self, "Atenção", "Não há inspeções disponíveis para criar um relatório.")
                return
                
            # Coleta os dados do formulário
            report_data = {
                'titulo': self.report_titulo_input.text().strip(),
                'inspecao_id': self.report_inspecao_combo.currentData(),
                'equipamento_id': self.get_equipment_id_from_inspection(self.report_inspecao_combo.currentData()),
                'tipo_relatorio': self.report_tipo_combo.currentText(),
                'data_emissao': self.report_data_input.date().toString("yyyy-MM-dd"),
                'data_validade': self.report_validade_input.date().toString("yyyy-MM-dd"),
                'status': self.report_status_combo.currentText(),
                'conformidade': 1 if self.report_conformidade_combo.currentText() == "Conforme" else 0,
                'nivel_risco': self.report_risco_combo.currentText(),
                'link_arquivo': self.report_arquivo_input.text(),
                'observacoes': self.report_obs_input.toPlainText(),
                'recomendacoes': self.report_recomendacoes_input.toPlainText(),
                'responsavel_id': 1,  # ID do usuário logado
            }
            
            # Verifica se é uma edição ou nova inserção
            editing_id = getattr(self, 'editing_report_id', None)
            
            if editing_id:
                # Atualiza um relatório existente
                success = self.report_controller.atualizar_relatorio(
                    id=editing_id,
                    **report_data
                )
                message = "Relatório atualizado com sucesso!" if success else "Erro ao atualizar relatório."
            else:
                # Cria um novo relatório
                success, message = self.report_controller.criar_relatorio(**report_data)
                
            if success:
                QMessageBox.information(self, "Sucesso", message if isinstance(message, str) else "Operação realizada com sucesso!")
                self.clear_report_form()
                self.load_reports()
            else:
                QMessageBox.warning(self, "Erro", message if isinstance(message, str) else "Erro ao processar operação.")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao salvar relatório: {str(e)}")
            
    def clear_report_form(self):
        """Limpa o formulário de relatório"""
        try:
            # Reseta o ID do relatório atual
            self.current_report_id = None
            
            # Limpa os campos do formulário
            self.report_inspecao_combo.setCurrentIndex(0)
            self.report_data_input.setDate(QDate.currentDate())
            self.report_arquivo_input.clear()
            self.report_observacoes_input.clear()
            
            # Atualiza o título do formulário
            self.report_form_title.setText("Novo Relatório")
            
            # Atualiza o texto do botão
            self.report_save_btn.setText("Salvar")
            
            logger.debug("Formulário de relatório limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar formulário de relatório: {str(e)}")

    def toggle_report_form_mode(self, is_editing=False):
        """Alterna o modo do formulário entre criação e edição"""
        form_title = self.findChild(QLabel, "form_title")
        if form_title:
            form_title.setText("Editar Relatório" if is_editing else "Novo Relatório")
            
        # Atualiza o texto do botão de salvar
        self.report_save_btn.setText("Atualizar" if is_editing else "Salvar")
        
    def load_report_details(self):
        """Carrega os detalhes de um relatório selecionado na tabela"""
        selected_items = self.reports_list.selectedItems()
        if not selected_items:
                return
                
        row = selected_items[0].row()
        report_id = int(self.reports_list.item(row, 0).text())
        
        # Busca os detalhes do relatório no banco de dados
        report = self.report_controller.get_report_by_id(report_id)
        
        if not report:
            return
                
        # Preenche o formulário com os dados do relatório
        self.editing_report_id = report_id
        self.toggle_report_form_mode(is_editing=True)
        
        # Preenche os campos
        self.report_titulo_input.setText(report.get('titulo', ''))
        
        # Seleciona a inspeção correta no combobox
        inspecao_id = report.get('inspecao_id')
        if inspecao_id:
            index = self.report_inspecao_combo.findData(inspecao_id)
            if index >= 0:
                self.report_inspecao_combo.setCurrentIndex(index)
        
        # Data de emissão
        if 'data_emissao' in report:
            data_str = report['data_emissao']
            if isinstance(data_str, str):
                try:
                    data_obj = QDate.fromString(data_str, "yyyy-MM-dd")
                    self.report_data_input.setDate(data_obj)
                except:
                    pass
                        
        # Data de validade
        if 'data_validade' in report:
            data_str = report['data_validade']
            if isinstance(data_str, str):
                try:
                    data_obj = QDate.fromString(data_str, "yyyy-MM-dd")
                    self.report_validade_input.setDate(data_obj)
                except:
                    pass
        
        # Tipo de relatório
        tipo = report.get('tipo_relatorio', '')
        index = self.report_tipo_combo.findText(tipo)
        if index >= 0:
            self.report_tipo_combo.setCurrentIndex(index)
            
        # Status
        status = report.get('status', '')
        index = self.report_status_combo.findText(status)
        if index >= 0:
            self.report_status_combo.setCurrentIndex(index)
            
        # Conformidade
        conformidade = "Conforme" if report.get('conformidade', 0) == 1 else "Não Conforme"
        index = self.report_conformidade_combo.findText(conformidade)
        if index >= 0:
            self.report_conformidade_combo.setCurrentIndex(index)
            
        # Nível de risco
        risco = report.get('nivel_risco', '')
        index = self.report_risco_combo.findText(risco)
        if index >= 0:
            self.report_risco_combo.setCurrentIndex(index)
            
        # Arquivo
        self.report_arquivo_input.setText(report.get('link_arquivo', ''))
        
        # Observações e recomendações
        self.report_obs_input.setPlainText(report.get('observacoes', ''))
        self.report_recomendacoes_input.setPlainText(report.get('recomendacoes', ''))
        
    def edit_selected_report(self):
        """Edita o relatório selecionado"""
        try:
            selected_items = self.report_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um relatório para editar.")
                return
            
            row = selected_items[0].row()
            report_id = int(self.report_table.item(row, 0).text())
            
            # Busca os dados do relatório
            report = self.report_controller.get_report_by_id(report_id)
            if not report:
                QMessageBox.warning(self, "Erro", "Relatório não encontrado.")
                return
            
            # Cria e configura o modal
            modal = ReportModal(self, self.is_dark)
            modal.setWindowTitle("Editar Relatório")
            
            # Carrega as inspeções no combo
            inspecoes = self.inspection_controller.get_all_inspections()
            modal.inspecao_combo.clear()
            
            for insp in inspecoes:
                data_str = insp.get('data_inspecao', '')
                if isinstance(data_str, str) and len(data_str) >= 10:
                    try:
                        data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                        data_str = data_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        data_str = 'Data inválida'
                
                display_text = f"#{insp['id']} - {insp.get('tipo_inspecao', '')} ({data_str})"
                modal.inspecao_combo.addItem(display_text, insp['id'])
            
            # Seleciona a inspeção atual
            index = modal.inspecao_combo.findData(report['inspecao_id'])
            if index >= 0:
                modal.inspecao_combo.setCurrentIndex(index)
            
            # Preenche os outros campos
            if report.get('data_emissao'):
                try:
                    data = QDate.fromString(report['data_emissao'][:10], 'yyyy-MM-dd')
                    modal.data_input.setDate(data)
                except:
                    pass
            
            modal.arquivo_input.setText(report.get('link_arquivo', ''))
            modal.observacoes_input.setPlainText(report.get('observacoes', ''))
            
            if modal.exec_() == QDialog.Accepted:
                # Obtém os dados atualizados
                data = modal.get_data()
                
                # Atualiza o relatório
                success = self.report_controller.atualizar_relatorio(
                    report_id,
                    data['inspecao_id'],
                    data['data_emissao'],
                    data['link_arquivo'],
                    data['observacoes']
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Relatório atualizado com sucesso!")
                    self.load_reports()
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível atualizar o relatório.")
                    
        except Exception as e:
            logger.error(f"Erro ao editar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao editar relatório: {str(e)}")

    def delete_selected_report(self):
        """Exclui o relatório selecionado"""
        try:
            selected_items = self.report_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um relatório para excluir.")
                return
            
            row = selected_items[0].row()
            report_id = int(self.report_table.item(row, 0).text())
            
            # Confirmação
            reply = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                "Tem certeza que deseja excluir este relatório?\nEsta ação não pode ser desfeita.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.report_controller.excluir_relatorio(report_id)
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Relatório excluído com sucesso!")
                    self.load_reports()
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível excluir o relatório.")
                    
        except Exception as e:
            logger.error(f"Erro ao excluir relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao excluir relatório: {str(e)}")

    def view_selected_report(self):
        """Visualiza o arquivo do relatório selecionado"""
        try:
            selected_items = self.report_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um relatório para visualizar.")
                return
            
            row = selected_items[0].row()
            arquivo = self.report_table.item(row, 3).text()
            
            if not arquivo:
                QMessageBox.warning(self, "Atenção", "Este relatório não possui arquivo anexado.")
                return
            
            if not os.path.exists(arquivo):
                QMessageBox.warning(self, "Erro", "O arquivo não foi encontrado no caminho especificado.")
                return
            
            # Abre o arquivo com o programa padrão do sistema
            import subprocess
            import platform
            
            try:
                if platform.system() == 'Windows':
                    os.startfile(arquivo)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', arquivo])
                else:  # Linux e outros
                    subprocess.run(['xdg-open', arquivo])
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo: {str(e)}")
                
        except Exception as e:
            logger.error(f"Erro ao visualizar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao visualizar relatório: {str(e)}")

    def filter_reports(self):
        """Filtra os relatórios na tabela com base nos critérios de filtro"""
        try:
            search_text = self.report_search_input.text().lower()
            
            for row in range(self.report_table.rowCount()):
                should_show = False
                
                # Verifica cada coluna da linha
                for col in range(self.report_table.columnCount()):
                    item = self.report_table.item(row, col)
                    if item and search_text in item.text().lower():
                        should_show = True
                        break
                
                # Mostra ou esconde a linha
                self.report_table.setRowHidden(row, not should_show)
                
        except Exception as e:
            logger.error(f"Erro ao filtrar relatórios: {str(e)}")
            logger.error(traceback.format_exc())

    def load_reports(self):
        """Carrega os relatórios na tabela"""
        try:
            logger.debug("Carregando relatórios")
            reports = self.report_controller.get_all_reports()
            self.report_table.setRowCount(len(reports))
            
            for i, report in enumerate(reports):
                try:
                    # ID
                    id_item = QTableWidgetItem(str(report.get('id', '')))
                    self.report_table.setItem(i, 0, id_item)
                    
                    # Inspeção (combina tipo e equipamento)
                    inspecao_info = f"{report.get('tipo_inspecao', 'N/A')} - {report.get('equipamento_tag', 'N/A')}"
                    insp_item = QTableWidgetItem(inspecao_info)
                    self.report_table.setItem(i, 1, insp_item)
                    
                    # Data
                    data_str = report.get('data_emissao', '')
                    if isinstance(data_str, str) and len(data_str) >= 10:
                        try:
                            data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                            data_str = data_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            pass
                    data_item = QTableWidgetItem(data_str)
                    self.report_table.setItem(i, 2, data_item)
                    
                    # Arquivo
                    arquivo_item = QTableWidgetItem(report.get('link_arquivo', ''))
                    self.report_table.setItem(i, 3, arquivo_item)
                    
                    # Observações
                    obs_item = QTableWidgetItem(report.get('observacoes', ''))
                    self.report_table.setItem(i, 4, obs_item)
                    
                    # Status (baseado na existência do arquivo)
                    tem_arquivo = bool(report.get('link_arquivo'))
                    status_item = QTableWidgetItem("Concluído" if tem_arquivo else "Pendente")
                    status_item.setForeground(QColor('#28a745' if tem_arquivo else '#dc3545'))
                    self.report_table.setItem(i, 5, status_item)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar relatório {i}: {str(e)}")
                    continue
            
            logger.debug(f"Carregados {len(reports)} relatórios")
            
        except Exception as e:
            logger.error(f"Erro ao carregar relatórios: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar relatórios: {str(e)}")

    def load_inspecoes_combo(self):
        """Carrega as inspeções disponíveis no combobox"""
        try:
            logger.debug("Carregando inspeções no combobox")
            self.report_inspecao_combo.clear()
            
            # Busca todas as inspeções
            inspecoes = self.inspection_controller.get_all_inspections()
            
            # Adiciona as inspeções ao combobox
            for insp in inspecoes:
                # Formata a data
                data_str = insp.get('data_inspecao', '')
                if isinstance(data_str, str) and len(data_str) >= 10:
                    try:
                        data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                        data_str = data_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        data_str = 'Data inválida'
                
                # Cria o texto de exibição
                display_text = f"#{insp['id']} - {insp.get('tipo_inspecao', '')} ({data_str})"
                
                # Adiciona ao combobox
                self.report_inspecao_combo.addItem(display_text, insp['id'])
            
            logger.debug(f"Carregadas {len(inspecoes)} inspeções no combobox")
            
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções no combobox: {str(e)}")
            logger.error(traceback.format_exc())

    def add_engineer(self):
        """Abre o modal para adicionar um engenheiro"""
        try:
            logger.debug("Abrindo modal para adicionar engenheiro")
            modal = UserModal(self, self.is_dark)
            
            # Define o tipo como engenheiro
            tipo_idx = modal.tipo_input.findText("eng")
            if tipo_idx < 0:  # Se não existe "eng" no combobox, adiciona
                modal.tipo_input.addItem("eng")
                tipo_idx = modal.tipo_input.findText("eng")
            modal.tipo_input.setCurrentIndex(tipo_idx)
            
            if modal.exec_():
                data = modal.get_data()
                logger.debug(f"Dados do engenheiro: {data}")
                
                success, message = self.auth_controller.criar_usuario(
                    nome=data["nome"],
                    email=data["email"],
                    senha=data["senha"],
                    tipo_acesso="eng",  # Forçando o tipo como engenheiro
                    empresa=data["empresa"]
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_engineers()  # Recarrega a lista de engenheiros
                    self.load_users()      # Atualiza também a lista geral de usuários
                else:
                    QMessageBox.critical(self, "Erro", message)
        except Exception as e:
            logger.error(f"Erro ao adicionar engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar engenheiro: {str(e)}")

    def edit_selected_engineer(self):
        """Edita o engenheiro selecionado"""
        try:
            selected_rows = self.engineers_table.selectionModel().selectedRows()
            
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Selecione um engenheiro para editar.")
                return
                
            row = selected_rows[0].row()
            user_id = int(self.engineers_table.item(row, 0).text())
            
            # Reutiliza a função de editar usuário, mas garante que mantenha o tipo como engenheiro
            self.edit_selected_user(user_id=user_id, force_type="eng")
        except Exception as e:
            logger.error(f"Erro ao editar engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao editar engenheiro: {str(e)}")
        
    def toggle_selected_engineer(self):
        """Ativa/desativa o engenheiro selecionado"""
        try:
            selected_rows = self.engineers_table.selectionModel().selectedRows()
            
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Selecione um engenheiro para ativar/desativar.")
                return
                
            row = selected_rows[0].row()
            user_id = int(self.engineers_table.item(row, 0).text())
            is_active = self.engineers_table.item(row, 4).text() == "Sim"
            user_name = self.engineers_table.item(row, 1).text()
            
            if is_active:
                # Desativar engenheiro
                message = f"Deseja realmente desativar o engenheiro '{user_name}'?"
                if QMessageBox.question(self, "Confirmar desativação", message, 
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    success = self.auth_controller.desativar_usuario(user_id)
                    
                    if success:
                        QMessageBox.information(self, "Sucesso", f"Engenheiro '{user_name}' desativado com sucesso!")
                        self.load_engineers()
                        self.load_users()  # Atualiza a lista geral também
                    else:
                        QMessageBox.critical(self, "Erro", f"Erro ao desativar o engenheiro '{user_name}'.")
            else:
                # Ativar engenheiro
                message = f"Deseja realmente ativar o engenheiro '{user_name}'?"
                if QMessageBox.question(self, "Confirmar ativação", message, 
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    success = self.auth_controller.reativar_usuario(user_id)
                    
                    if success:
                        QMessageBox.information(self, "Sucesso", f"Engenheiro '{user_name}' ativado com sucesso!")
                        self.load_engineers()
                        self.load_users()  # Atualiza a lista geral também
                    else:
                        QMessageBox.critical(self, "Erro", f"Erro ao ativar o engenheiro '{user_name}'.")
        except Exception as e:
            logger.error(f"Erro ao alternar estado do engenheiro: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao alternar estado do engenheiro: {str(e)}")

    def load_engineers(self):
        """Carrega os engenheiros do banco de dados"""
        try:
            logger.debug("Carregando engenheiros")
            self.engineers_table.setRowCount(0)
            
            # Busca todos os usuários
            users = self.auth_controller.get_all_users()
            
            # Filtra apenas os engenheiros
            engineers = [user for user in users if user.get('tipo_acesso') == 'eng']
            
            # Preenche a tabela
            for i, engineer in enumerate(engineers):
                self.engineers_table.insertRow(i)
                
                # ID
                id_item = QTableWidgetItem(str(engineer.get('id', '')))
                self.engineers_table.setItem(i, 0, id_item)
                
                # Nome
                name_item = QTableWidgetItem(engineer.get('nome', ''))
                self.engineers_table.setItem(i, 1, name_item)
                
                # Email
                email_item = QTableWidgetItem(engineer.get('email', ''))
                self.engineers_table.setItem(i, 2, email_item)
                
                # Empresa
                company_item = QTableWidgetItem(engineer.get('empresa', ''))
                self.engineers_table.setItem(i, 3, company_item)
                
                # Ativo
                is_active = engineer.get('ativo', False)
                active_item = QTableWidgetItem("Sim" if is_active else "Não")
                active_item.setForeground(QColor('#28a745' if is_active else '#dc3545'))
                self.engineers_table.setItem(i, 4, active_item)
                
            logger.debug(f"Carregados {len(engineers)} engenheiros")
            
        except Exception as e:
            logger.error(f"Erro ao carregar engenheiros: {str(e)}")
            logger.error(traceback.format_exc())
            
    def filter_engineers(self, text):
        """Filtra a lista de engenheiros com base no texto digitado"""
        try:
            search_text = text.lower().strip()
            for row in range(self.engineers_table.rowCount()):
                visible = False
                for col in range(self.engineers_table.columnCount()):
                    item = self.engineers_table.item(row, col)
                    if item and search_text in item.text().lower():
                        visible = True
                        break
                self.engineers_table.setRowHidden(row, not visible)
        except Exception as e:
            logger.error(f"Erro ao filtrar engenheiros: {str(e)}")
            logger.error(traceback.format_exc())

    def show_add_report_modal(self):
        """Abre o modal para adicionar um novo relatório"""
        try:
            logger.debug("Abrindo modal para adicionar relatório")
            modal = ReportModal(self, self.is_dark)
            
            # Carrega as inspeções no combobox do modal
            inspecoes = self.inspection_controller.get_all_inspections()
            modal.inspecao_combo.clear()
            
            for insp in inspecoes:
                # Formata a data
                data_str = insp.get('data_inspecao', '')
                if isinstance(data_str, str) and len(data_str) >= 10:
                    try:
                        data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                        data_str = data_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        data_str = 'Data inválida'
                
                # Cria o texto de exibição
                display_text = f"#{insp['id']} - {insp.get('tipo_inspecao', '')} ({data_str})"
                modal.inspecao_combo.addItem(display_text, insp['id'])
            
            if modal.exec_() == QDialog.Accepted:
                # Obtém os dados do formulário
                data = modal.get_data()
                
                # Cria o relatório
                success, message = self.report_controller.criar_relatorio(
                    inspecao_id=data['inspecao_id'],
                    data_emissao=data['data_emissao'],
                    link_arquivo=data['link_arquivo'],
                    observacoes=data['observacoes']
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_reports()  # Recarrega a tabela
                else:
                    QMessageBox.warning(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao abrir modal de relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao abrir modal: {str(e)}")
