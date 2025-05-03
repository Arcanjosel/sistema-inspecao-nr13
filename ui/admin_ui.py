"""
Interface gráfica do administrador do sistema.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QFileDialog, QToolButton, QMenu,
    QHeaderView, QDialog, QGridLayout, QFormLayout, QInputDialog,
    QAction, QApplication
)
from PyQt5.QtCore import Qt, QDate, QSize, QTimer, pyqtSignal
from datetime import datetime, timedelta
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.styles import Styles
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from ui.modals import UserModal, EquipmentModal, InspectionModal, ReportModal, MaintenanceModal
from controllers.equipment_controller import EquipmentController
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController
import traceback
import os
import threading

logger = logging.getLogger(__name__)

class AdminWindow(QMainWindow):
    """
    Janela principal do administrador.
    """
    
    logout_requested = pyqtSignal()
    
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
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
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
                </svg>''',
                'theme': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>''',
                'logout': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>''',
                'maintenance': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 10h-4v4h4v-4z"></path>
                    <path d="M14 14h-4v4h4v-4z"></path>
                    <path d="M14 18h-4v4h4v-4z"></path>
                </svg>'''
            }
            
            logger.debug("Iniciando setup da UI")
            self.initUI()
            logger.debug("Aplicando tema")
            self.apply_theme()
            
            logger.debug("Carregando dados iniciais")
            # Carrega os dados iniciais antes de iniciar o timer
            self.load_users()
            self.load_equipment()
            self.load_inspections()
            self.load_reports()
            
            # Configurar o timer para atualização das tabelas a cada 5 segundos
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_all_tables)
            self.refresh_timer.start(5000)  # 5000ms = 5 segundos
            
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
            # Caso especial para o ícone de tema no modo escuro (preto em vez de branco)
            if "circle cx=\"12\" cy=\"12\" r=\"5\"" in svg_str:  # Identificador do ícone de tema
                svg_str = svg_str.replace("currentColor", "black")
            else:
                svg_str = svg_str.replace("currentColor", "white")
        else:
            svg_str = svg_str.replace("currentColor", "#333333")
            
        svg_bytes = svg_str.encode('utf-8')
        pixmap = QPixmap()
        pixmap.loadFromData(svg_bytes)
        return QIcon(pixmap)

    def get_tab_icon(self, icon_name):
        """Retorna o ícone apropriado para a aba diretamente do arquivo PNG"""
        try:
            logger.debug(f"Obtendo ícone: {icon_name}")
            
            # Carregar diretamente do arquivo PNG sem tentar usar SVG
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
        
    def create_crud_button(self, button_type, tooltip, callback, show_text=False, text=None):
        """Cria um botão padronizado para ações CRUD (Create, Read, Update, Delete)
        
        Args:
            button_type: Tipo do botão ('add', 'edit', 'delete', 'toggle', 'view', 'theme')
            tooltip: Texto da dica de ferramenta
            callback: Função a ser chamada quando o botão for clicado
            show_text: Se True, exibe texto no botão além do ícone
            text: Texto a ser exibido no botão (se None, usa o tooltip)
            
        Returns:
            QPushButton: Botão configurado
        """
        # Definir ícone com base no tipo
        icon_key = button_type
        if button_type == 'view':
            icon_key = 'browse'  # Usa o ícone 'browse' para botões de visualização
        elif button_type == 'toggle':
            # Usa o ícone 'disable' para botões de ativar/desativar
            icon_key = 'disable'
            
        # Criar botão com ou sem texto
        if show_text:
            button_text = text if text else tooltip
            button = QPushButton(button_text)
        else:
            button = QPushButton()
            
        button.setIcon(self.create_icon_from_svg(self.icons[icon_key]))
        button.setIconSize(QSize(24, 24))
        
        if not show_text:
            button.setFixedSize(40, 40)  # Tamanho quadrado para botões sem texto
        else:
            button.setMinimumSize(150, 40)  # Tamanho mínimo para botões com texto (aumentado de 100 para 150)
            
        button.setToolTip(tooltip)  # Adiciona dica ao passar o mouse
        button.clicked.connect(callback)
        
        # Define o estilo apropriado
        if button_type in self.button_style:
            button.setStyleSheet(self.button_style[button_type])
        else:
            # Para botões não definidos, usa o estilo 'toggle'
            button.setStyleSheet(self.button_style['toggle'])
        
        return button
    
    def initUI(self):
        """Inicializa a interface do usuário."""
        try:
            logger.debug("Iniciando setup da interface")
            self.setWindowTitle("Administração do Sistema")
            self.resize(1024, 768)
            
            # Estilos padrão para botões CRUD (adiciona estilo para logout)
            self.button_style = {
                'add': """
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                    QPushButton:pressed {
                        background-color: #1e7e34;
                    }
                """,
                'edit': """
                    QPushButton {
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                    QPushButton:pressed {
                        background-color: #004085;
                    }
                """,
                'delete': """
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #bd2130;
                    }
                """,
                'toggle': """
                    QPushButton {
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #5a6268;
                    }
                    QPushButton:pressed {
                        background-color: #545b62;
                    }
                """,
                'view': """
                    QPushButton {
                        background-color: #17a2b8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #138496;
                    }
                    QPushButton:pressed {
                        background-color: #117a8b;
                    }
                """,
                'theme': """
                    QPushButton {
                        background-color: #000000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #333333;
                    }
                    QPushButton:pressed {
                        background-color: #222222;
                    }
                """,
                'logout': """
                    QPushButton {
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #5a6268;
                    }
                    QPushButton:pressed {
                        background-color: #545b62;
                    }
                """,
                'maintenance': """
                    QPushButton {
                        background-color: #fd7e14;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #e86d0a;
                    }
                    QPushButton:pressed {
                        background-color: #d96308;
                    }
                """
            }
            
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
            
            # Container do título com logo e botões de controle
            title_container = QHBoxLayout()
            
            # Logo
            logo_label = QLabel()
            logo_pixmap = QPixmap("ui/CTREINA_LOGO_FIT.png")
            logo_label.setPixmap(logo_pixmap.scaled(150, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
            title_container.addStretch() # Empurra os botões para a direita
            
            # Botão de Tema
            self.theme_button = QToolButton()
            self.theme_button.setIcon(self.create_icon_from_svg(self.icons['theme']))
            self.theme_button.setIconSize(QSize(24, 24))
            self.theme_button.setToolTip("Alternar tema claro/escuro")
            self.theme_button.clicked.connect(self.toggle_theme)
            self.theme_button.setStyleSheet("QToolButton { border: none; padding: 5px; }")
            title_container.addWidget(self.theme_button)
            
            # Botão de Logout
            self.logout_button = QToolButton()
            self.logout_button.setIcon(self.create_icon_from_svg(self.icons['logout']))
            self.logout_button.setIconSize(QSize(24, 24))
            self.logout_button.setToolTip("Sair do Sistema")
            self.logout_button.clicked.connect(self.logout)
            self.logout_button.setStyleSheet("QToolButton { border: none; padding: 5px; }")
            title_container.addWidget(self.logout_button)
            
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
            self.add_user_button = self.create_crud_button("add", "Adicionar", self.add_user)
            buttons_container.addWidget(self.add_user_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Editar
            self.edit_user_button = self.create_crud_button("edit", "Editar", self.edit_selected_user)
            buttons_container.addWidget(self.edit_user_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Ativar/Desativar
            self.toggle_user_button = self.create_crud_button("toggle", "Ativar/Desativar", self.toggle_selected_user, show_text=True, text="Ativar/Desativar")
            buttons_container.addWidget(self.toggle_user_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Remover Usuário
            self.remove_user_button = self.create_crud_button("delete", "Remover Usuário", self.remove_selected_user)
            buttons_container.addWidget(self.remove_user_button)
            
            # Inicialmente esconder botões de ação que precisam de seleção
            self.toggle_user_button.setVisible(False)
            self.remove_user_button.setVisible(False)
            
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
            self.user_table.setColumnCount(5)  # Aumentado para 5 colunas (adicionado Empresa)
            self.user_table.setHorizontalHeaderLabels([
                "Nome", "Email", "Tipo Acesso", "Status", "Empresa"
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
            
            # Container para botões e barra de pesquisa
            equipment_top_container = QHBoxLayout()
            
            # Container para botões (lado esquerdo)
            equipment_buttons_container = QHBoxLayout()
            
            # Botão Adicionar
            logger.debug("Criando botão adicionar equipamento")
            self.add_equipment_button = self.create_crud_button('add', "Adicionar Equipamento", self.add_equipment)
            equipment_buttons_container.addWidget(self.add_equipment_button)
            
            # Botão Editar
            logger.debug("Criando botão editar equipamento")
            self.edit_equipment_button = self.create_crud_button('edit', "Editar Equipamento", self.edit_equipment)
            equipment_buttons_container.addWidget(self.edit_equipment_button)
            
            # Botão Ativar/Desativar
            logger.debug("Criando botão toggle equipamento")
            self.toggle_equipment_button = self.create_crud_button('toggle', "Alternar Estado", self.toggle_equipment, show_text=True, text="Ativar/Desativar")
            equipment_buttons_container.addWidget(self.toggle_equipment_button)
            
            # Botão Excluir
            logger.debug("Criando botão excluir equipamento")
            self.delete_equipment_button = self.create_crud_button('delete', "Excluir Equipamento", self.delete_equipment)
            equipment_buttons_container.addWidget(self.delete_equipment_button)
            
            # Botão Manutenção
            logger.debug("Criando botão de manutenção de equipamento")
            self.maintenance_button = self.create_crud_button('maintenance', "Registrar Manutenção", self.register_maintenance)
            equipment_buttons_container.addWidget(self.maintenance_button)
            
            # Definir visibilidade inicial dos botões que requerem seleção
            self.edit_equipment_button.setEnabled(False)
            self.toggle_equipment_button.setEnabled(False)
            self.delete_equipment_button.setEnabled(False)
            self.maintenance_button.setEnabled(False)
            
            equipment_top_container.addLayout(equipment_buttons_container)
            equipment_top_container.addStretch()
            
            # Container para barra de pesquisa (lado direito)
            equipment_search_container = QHBoxLayout()
            
            # Label para pesquisa
            equipment_search_label = QLabel("Pesquisar:")
            equipment_search_container.addWidget(equipment_search_label)
            
            # Campo de pesquisa
            self.equipment_search_box = QLineEdit()
            self.equipment_search_box.setPlaceholderText("Digite para filtrar...")
            self.equipment_search_box.textChanged.connect(self.filter_equipment)
            equipment_search_container.addWidget(self.equipment_search_box)
            
            # Filtro por empresa
            equipment_company_label = QLabel("Empresa:")
            equipment_search_container.addWidget(equipment_company_label)
            
            self.equipment_company_selector = QComboBox()
            self.equipment_company_selector.currentIndexChanged.connect(self.filter_equipment_by_company)
            equipment_search_container.addWidget(self.equipment_company_selector)
            
            equipment_top_container.addLayout(equipment_search_container)
            
            equipment_layout.addLayout(equipment_top_container)
            
            # Carregar empresas no combobox de filtro
            self.load_companies_to_equipment_combobox()
            
            # Tabela de Equipamentos
            logger.debug("Criando tabela de equipamentos")
            self.equipment_table = QTableWidget()
            self.equipment_table.setColumnCount(16)  # Ajustado para os campos de manutenção
            self.equipment_table.setHorizontalHeaderLabels([
                "Tag", "Categoria", "Empresa", "Fabricante", "Ano", "P. Projeto",
                "P. Trabalho", "Volume", "Fluido", "Status", "Cat. NR13", "PMTA", "Placa ID", 
                "Nº Registro", "Última Manutenção", "Próxima Manutenção"
            ])
            
            # Configurar tabela para não mostrar números de linha
            self.equipment_table.verticalHeader().setVisible(False)
            
            # Configurar comportamento de seleção
            self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.equipment_table.setSelectionMode(QTableWidget.SingleSelection)
            
            # Configurar cabeçalhos para preencher a tabela
            self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Ajustar tamanho específico para colunas comuns
            equipment_header = self.equipment_table.horizontalHeader()
            equipment_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tag
            equipment_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Categoria
            equipment_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Empresa
            
            # Conectar sinal de seleção alterada para atualizar botões
            self.equipment_table.itemSelectionChanged.connect(self.update_toggle_equipment_button)
            
            equipment_layout.addWidget(self.equipment_table)
            
            # Aba de Inspeções
            logger.debug("Configurando aba de inspeções")
            inspection_tab = QWidget()
            inspection_layout = QVBoxLayout(inspection_tab)
            
            # Container para botões e barra de pesquisa
            top_container = QHBoxLayout()
            
            # Container para botões (lado esquerdo)
            buttons_container = QHBoxLayout()
            
            # Botão Adicionar Inspeção
            self.add_inspection_btn = self.create_crud_button("add", "Adicionar Inspeção", self.add_inspection)
            buttons_container.addWidget(self.add_inspection_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Editar Inspeção
            self.edit_inspection_btn = self.create_crud_button("edit", "Editar", self.edit_selected_inspection)
            buttons_container.addWidget(self.edit_inspection_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Excluir Inspeção
            self.delete_inspection_btn = self.create_crud_button("delete", "Excluir", self.delete_selected_inspection)
            buttons_container.addWidget(self.delete_inspection_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Gerar Relatório
            self.generate_report_btn = self.create_crud_button("add", "Gerar Relatório", self.generate_report_from_inspection)
            buttons_container.addWidget(self.generate_report_btn)
            
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
            self.inspection_table.setColumnCount(5)  # Reduzido para 5 colunas (removido ID)
            self.inspection_table.setHorizontalHeaderLabels([
                "Equipamento", "Data", "Tipo", "Engenheiro", "Resultado"
            ])
            self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.inspection_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.inspection_table.setSelectionMode(QTableWidget.SingleSelection)
            self.inspection_table.setAlternatingRowColors(True)
            self.inspection_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.inspection_table.verticalHeader().setVisible(False)  # Já está oculto
            
            # Carrega as inspeções
            self.load_inspections()
            inspection_layout.addWidget(self.inspection_table)
            
            # Aba de Relatórios
            logger.debug("Configurando aba de relatórios")
            report_tab = QWidget()
            report_layout = QVBoxLayout(report_tab)
            
            # Container para busca, filtros e botões
            top_container = QHBoxLayout()
            top_container.setContentsMargins(0, 0, 0, 0)
            
            # Container para botões (lado esquerdo)
            buttons_container = QHBoxLayout()
            
            # Botão Adicionar Relatório
            self.add_report_btn = self.create_crud_button("add", "Adicionar Relatório", self.show_add_report_modal)
            buttons_container.addWidget(self.add_report_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Editar
            self.edit_report_btn = self.create_crud_button("edit", "Editar", self.edit_selected_report)
            buttons_container.addWidget(self.edit_report_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Excluir
            self.delete_report_btn = self.create_crud_button("delete", "Excluir", self.delete_selected_report)
            buttons_container.addWidget(self.delete_report_btn)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Visualizar
            self.view_report_btn = self.create_crud_button("view", "Visualizar", self.view_selected_report)
            buttons_container.addWidget(self.view_report_btn)
            
            top_container.addLayout(buttons_container)
            top_container.addStretch()
            
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
            
            top_container.addLayout(search_box)
            
            report_layout.addLayout(top_container)
            
            # Tabela de relatórios
            self.report_table = QTableWidget()
            self.report_table.setColumnCount(5)  # Reduzido para 5 colunas (removido ID)
            self.report_table.setHorizontalHeaderLabels([
                "Inspeção", "Data", "Arquivo", "Observações", "Status"
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.report_table.setSelectionMode(QTableWidget.SingleSelection)
            self.report_table.setAlternatingRowColors(True)
            self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.report_table.verticalHeader().setVisible(False)  # Oculta o cabeçalho vertical
            
            logger.debug("Carregando relatórios do banco de dados")
            self.load_reports()
            report_layout.addWidget(self.report_table)
            
            # Adiciona as abas com ícones
            logger.debug("Adicionando abas ao TabWidget")
            self.tabs.addTab(users_tab, self.get_tab_icon("user.png"), "Usuários")
            self.tabs.addTab(equipment_tab, self.get_tab_icon("equipamentos.png"), "Equipamentos")
            self.tabs.addTab(inspection_tab, self.get_tab_icon("inspecoes.png"), "Inspeções")
            self.tabs.addTab(report_tab, self.get_tab_icon("relatorios.png"), "Relatórios")
            
            # Comentado: Não exibir mais a aba de Equipamentos por Empresa
            # company_equipment_tab = self.create_company_equipment_tab()
            # self.tabs.addTab(company_equipment_tab, self.get_tab_icon("equipamentos.png"), "Equipamentos por Empresa")
            
            self.tabs.setIconSize(QSize(35, 35))
            layout.addWidget(self.tabs)
            
            # Barra inferior com versão do sistema
            logger.debug("Configurando barra inferior")
            bottom_bar = QHBoxLayout()
            
            # Informações da versão
            version_label = QLabel("Sistema de Inspeções NR-13 v1.0")
            version_label.setStyleSheet("color: #777777; font-size: 11px;")
            bottom_bar.addWidget(version_label)
            
            # Removido o spacer e o botão de logout para tornar a barra menor
            # Adicionado margem mínima à direita para não cortar o texto
            bottom_bar.setContentsMargins(0, 0, 10, 0)
            
            layout.addLayout(bottom_bar)
            
            logger.debug("Interface inicializada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar UI: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar interface: {str(e)}")
            raise
    
    def apply_theme(self):
        """Aplica o tema escuro ou claro à interface"""
        try:
            logger.debug(f"Aplicando tema {'escuro' if self.is_dark else 'claro'}")
            QApplication.setOverrideCursor(Qt.WaitCursor)  # Mostra cursor de "aguarde" durante a operação
            
            # Bloqueie os sinais das tabelas para evitar atualizações desnecessárias
            self.user_table.blockSignals(True)
            self.equipment_table.blockSignals(True)
            self.inspection_table.blockSignals(True)
            self.report_table.blockSignals(True)
            
            # Cria os estilos antes de aplicar (para melhor performance)
            if self.is_dark:
                app_style = Styles.get_dark_theme()
                
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
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #3a3d40;
                        color: #ffffff;
                    }
                """
                
                # Estilo específico para o botão de tema no modo escuro (cinza claro)
                theme_button_style = """
                    QToolButton {
                        background-color: #aaaaaa;
                        color: #121212;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QToolButton:hover {
                        background-color: #999999;
                    }
                    QToolButton:pressed {
                        background-color: #888888;
                    }
                """
            else:
                app_style = Styles.get_light_theme()
                
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
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #e0e0e0;
                        color: #000000;
                    }
                """
                
                # Estilo específico para o botão de tema no modo claro (preto)
                theme_button_style = """
                    QToolButton {
                        background-color: #000000;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QToolButton:hover {
                        background-color: #333333;
                    }
                    QToolButton:pressed {
                        background-color: #222222;
                    }
                """
            
            # Aplica os estilos a toda a aplicação
            self.setStyleSheet(app_style)
            
            # Aplica estilo ao botão de tema (apenas o do cabeçalho, o da barra inferior foi removido)
            self.theme_button.setStyleSheet(theme_button_style)
            
            # Aplica estilos às tabelas em um único lote
            for table in [self.user_table, self.equipment_table, self.inspection_table, self.report_table]:
                table.setStyleSheet(table_style)
                table.setAlternatingRowColors(True)
            
            # Atualiza os ícones das abas ao trocar o tema
            for idx, icon_name in enumerate(["user.png", "equipamentos.png", "inspecoes.png", "relatorios.png"]):
                self.tabs.setTabIcon(idx, self.get_tab_icon(icon_name))
            
            # Atualiza o botão de ativar/desativar
            self.update_toggle_button()
            
            # Atualizar ícones dos botões
            self.theme_button.setIcon(self.create_icon_from_svg(self.icons['theme']))
            self.logout_button.setIcon(self.create_icon_from_svg(self.icons['logout']))
            
            # Desbloqueia os sinais
            self.user_table.blockSignals(False)
            self.equipment_table.blockSignals(False)
            self.inspection_table.blockSignals(False)
            self.report_table.blockSignals(False)
            
            # Forçar uma atualização visual das tabelas
            for table in [self.user_table, self.equipment_table, self.inspection_table, self.report_table]:
                table.update()
            
            QApplication.restoreOverrideCursor()  # Restaura o cursor normal
            logger.debug(f"Tema {'escuro' if self.is_dark else 'claro'} aplicado com sucesso")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()  # Restaura o cursor em caso de erro
            logger.error(f"Erro ao aplicar tema: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar tema: {str(e)}")

    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        logger.debug("Alternando tema")
        # Altera a flag do tema
        self.is_dark = not self.is_dark
        
        # Aplica o tema com otimizações para melhor performance
        QTimer.singleShot(10, self.apply_theme)  # Executar após 10ms para dar tempo à interface atualizar
        
    def load_users(self):
        """Carrega os usuários na tabela"""
        try:
            logger.debug("Carregando usuários")
            users = self.auth_controller.get_all_users()
            self.user_table.setRowCount(len(users))
            
            for i, user in enumerate(users):
                # Armazena o ID como dados do item (invisível para o usuário)
                user_id = user['id']
                
                # Nome
                nome_item = QTableWidgetItem(user['nome'])
                nome_item.setFlags(nome_item.flags() & ~Qt.ItemIsEditable)
                nome_item.setData(Qt.UserRole, user_id)  # Armazena o ID como dado do item
                self.user_table.setItem(i, 0, nome_item)
                
                # Email
                email_item = QTableWidgetItem(user['email'])
                email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 1, email_item)
                
                # Tipo Acesso
                tipo_item = QTableWidgetItem(user['tipo_acesso'])
                tipo_item.setFlags(tipo_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 2, tipo_item)
                
                # Status
                status_item = QTableWidgetItem("Ativo" if user.get('ativo', 1) else "Inativo")
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 3, status_item)
                
                # Empresa
                empresa_item = QTableWidgetItem(user.get('empresa', ''))
                empresa_item.setFlags(empresa_item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(i, 4, empresa_item)
                
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")
            
    def load_equipment(self):
        """Carrega todos os equipamentos na tabela, incluindo o ID da empresa como UserRole na coluna Empresa"""
        try:
            logger.debug("Carregando equipamentos")
            equipment = self.equipment_controller.get_all_equipment()
            self.equipment_table.setRowCount(len(equipment))
            
            # Obter todas as empresas para usar como mapeamento ID -> Nome
            empresas = self.auth_controller.get_companies()
            empresa_map = {empresa['id']: empresa['nome'] for empresa in empresas}
            
            # Data atual para cálculos de manutenção
            data_atual = datetime.now().date()
            
            for i, item in enumerate(equipment):
                # Armazena o ID como dados do item (invisível para o usuário)
                equip_id = item.get('id', '')
                logger.debug(f"Carregando equipamento ID={equip_id}, Tag={item.get('tag', '')}")
                
                # Tag
                tag_item = QTableWidgetItem(item.get('tag', ''))
                tag_item.setData(Qt.UserRole, equip_id)  # Armazena o ID como dado do item
                tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)  # Remove a flag de editável
                self.equipment_table.setItem(i, 0, tag_item)
                
                # Para debug - verifica se o ID foi armazenado corretamente
                id_stored = tag_item.data(Qt.UserRole)
                logger.debug(f"ID armazenado no item da tabela: {id_stored}")
                
                # Resto dos campos - todos configurados como não editáveis
                categoria_item = QTableWidgetItem(item.get('categoria', ''))
                categoria_item.setFlags(categoria_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 1, categoria_item)
                
                # Empresa - usando o nome em vez do ID
                empresa_id = item.get('empresa_id', '')
                empresa_nome = empresa_map.get(empresa_id, f"ID: {empresa_id}")
                empresa_item = QTableWidgetItem(empresa_nome)
                empresa_item.setData(Qt.UserRole, empresa_id)  # Armazena o ID como dado do item
                empresa_item.setFlags(empresa_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 2, empresa_item)
                
                fabricante_item = QTableWidgetItem(item.get('fabricante', ''))
                fabricante_item.setFlags(fabricante_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 3, fabricante_item)
                
                ano_item = QTableWidgetItem(str(item.get('ano_fabricacao', '')))
                ano_item.setFlags(ano_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 4, ano_item)
                
                pressao_projeto_item = QTableWidgetItem(str(item.get('pressao_projeto', '')))
                pressao_projeto_item.setFlags(pressao_projeto_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 5, pressao_projeto_item)
                
                pressao_trabalho_item = QTableWidgetItem(str(item.get('pressao_trabalho', '')))
                pressao_trabalho_item.setFlags(pressao_trabalho_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 6, pressao_trabalho_item)
                
                volume_item = QTableWidgetItem(str(item.get('volume', '')))
                volume_item.setFlags(volume_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 7, volume_item)
                
                fluido_item = QTableWidgetItem(item.get('fluido', ''))
                fluido_item.setFlags(fluido_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 8, fluido_item)
                
                # Status
                status = "Ativo" if item.get('ativo', 1) else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 9, status_item)
                
                # Novos campos NR-13
                categoria_nr13_item = QTableWidgetItem(item.get('categoria_nr13', ''))
                categoria_nr13_item.setFlags(categoria_nr13_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 10, categoria_nr13_item)
                
                pmta_item = QTableWidgetItem(str(item.get('pmta', '')))
                pmta_item.setFlags(pmta_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 11, pmta_item)
                
                placa_identificacao_item = QTableWidgetItem(item.get('placa_identificacao', ''))
                placa_identificacao_item.setFlags(placa_identificacao_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 12, placa_identificacao_item)
                
                numero_registro_item = QTableWidgetItem(item.get('numero_registro', ''))
                numero_registro_item.setFlags(numero_registro_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 13, numero_registro_item)
                
                # Campos de manutenção
                # Última manutenção
                data_ultima_manutencao = item.get('data_ultima_manutencao', '')
                data_ultima_str = ''
                data_ultima_obj = None
                
                if data_ultima_manutencao:
                    try:
                        if isinstance(data_ultima_manutencao, str):
                            # Tratamento robusto para strings de data
                            if len(data_ultima_manutencao) >= 10:
                                data_ultima_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d').date()
                                data_ultima_str = data_ultima_obj.strftime('%d/%m/%Y')
                            else:
                                data_ultima_str = data_ultima_manutencao
                                logger.warning(f"Formato de data inválido: {data_ultima_manutencao}")
                        elif isinstance(data_ultima_manutencao, datetime):
                            data_ultima_obj = data_ultima_manutencao.date()
                            data_ultima_str = data_ultima_obj.strftime('%d/%m/%Y')
                        else:
                            data_ultima_str = str(data_ultima_manutencao)
                            logger.warning(f"Tipo de data não reconhecido: {type(data_ultima_manutencao)}")
                    except Exception as e:
                        data_ultima_str = str(data_ultima_manutencao)
                        logger.warning(f"Erro ao processar data de manutenção: {str(e)}")
                
                ultima_manutencao_item = QTableWidgetItem(data_ultima_str)
                ultima_manutencao_item.setFlags(ultima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 14, ultima_manutencao_item)
                
                # Próxima manutenção
                data_proxima_str = ''
                frequencia = item.get('frequencia_manutencao', 0)
                dias_restantes = None
                
                if data_ultima_manutencao and frequencia:
                    try:
                        # Se ainda não temos o objeto data_ultima_obj, tentar convertê-lo novamente
                        if data_ultima_obj is None and isinstance(data_ultima_manutencao, str):
                            try:
                                if len(data_ultima_manutencao) >= 10:
                                    data_ultima_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d').date()
                            except Exception:
                                logger.warning(f"Não foi possível converter a data: {data_ultima_manutencao}")
                        
                        if data_ultima_obj:
                            data_proxima = data_ultima_obj + timedelta(days=frequencia)
                            data_proxima_str = data_proxima.strftime('%d/%m/%Y')
                            
                            # Calcular dias restantes
                            dias_restantes = (data_proxima - data_atual).days
                            
                            # Aplicar indicadores visuais baseados na urgência da manutenção
                            proxima_manutencao_item = QTableWidgetItem(data_proxima_str)
                            proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                            self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                            
                            # Verifica se está atrasado ou próximo
                            if dias_restantes < 0 and item.get('ativo', 1):  # Atrasado e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 10, 10)  # Vermelho muito escuro para tema escuro
                                    cor_texto = QColor(255, 130, 130)  # Texto vermelho claro
                                else:
                                    cor_linha = QColor(255, 200, 200)  # Vermelho pastel
                                    cor_texto = QColor(139, 0, 0)  # Vermelho escuro para contraste
                                
                                # Adiciona indicador visual de manutenção atrasada
                                proxima_manutencao_item.setText("❗ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção ATRASADA")
                            elif dias_restantes <= 7 and item.get('ativo', 1):  # Próximo (1 semana) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 20, 20)  # Vermelho escuro para tema escuro
                                    cor_texto = QColor(255, 150, 150)  # Texto vermelho claro
                                else:
                                    cor_linha = QColor(255, 200, 200)  # Vermelho claro
                                    cor_texto = QColor(139, 0, 0)  # Texto escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("❗ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção URGENTE (≤ 7 dias)")
                            elif dias_restantes <= 15 and item.get('ativo', 1):  # Próximo (15 dias) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 60, 10)  # Laranja escuro para tema escuro
                                    cor_texto = QColor(255, 200, 120)  # Texto laranja claro
                                else:
                                    cor_linha = QColor(255, 230, 180)  # Laranja claro
                                    cor_texto = QColor(102, 51, 0)  # Marrom escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("⚠️ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção ALTA (≤ 15 dias)")
                            elif dias_restantes <= 30 and item.get('ativo', 1):  # Próximo (30 dias) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 90, 10)  # Amarelo escuro para tema escuro
                                    cor_texto = QColor(255, 255, 150)  # Texto amarelo claro
                                else:
                                    cor_linha = QColor(255, 255, 180)  # Amarelo claro
                                    cor_texto = QColor(102, 102, 0)  # Amarelo escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("⚠️ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção MÉDIA (≤ 30 dias)")
                        else:
                            proxima_manutencao_item = QTableWidgetItem("Não programada")
                            proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                            self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                    except Exception as e:
                        logger.error(f"Erro ao calcular próxima manutenção: {str(e)}")
                        data_proxima_str = "Erro no cálculo"
                        proxima_manutencao_item = QTableWidgetItem(data_proxima_str)
                        proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                        self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                else:
                    proxima_manutencao_item = QTableWidgetItem("Não programada")
                    proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                    self.equipment_table.setItem(i, 15, proxima_manutencao_item)
            
            # Forçar atualização imediata da tabela
            self.equipment_table.viewport().update()
            logger.debug(f"Carregados {len(equipment)} equipamentos na tabela")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
            
    def load_inspections(self):
        """Carrega as inspeções do banco de dados para a tabela"""
        try:
            logger.debug("Carregando inspeções do banco de dados")
            
            # Força a sincronização antes de carregar
            self.inspection_controller.force_sync()
            
            # Carrega os equipamentos para referência
            equipamentos = self.equipment_controller.get_all_equipment()
            equipamentos_map = {equip['id']: equip for equip in equipamentos}
            logger.debug(f"Carregados {len(equipamentos)} equipamentos")
            
            # Busca todas as inspeções
            inspecoes = self.inspection_controller.get_all_inspections()
            self.inspection_table.setRowCount(len(inspecoes))
            
            for i, inspecao in enumerate(inspecoes):
                # Equipamento (tag)
                equip_tag = inspecao.get('equipamento_tag', f"ID: {inspecao.get('equipamento_id', 0)}")
                equip_item = QTableWidgetItem(equip_tag)
                equip_item.setData(Qt.UserRole, inspecao.get('id', 0))  # Armazena o ID da inspeção para uso posterior
                self.inspection_table.setItem(i, 0, equip_item)
                
                # Data
                data_str = inspecao.get('data_inspecao', '')
                # Garante que data_str seja uma string
                if isinstance(data_str, datetime):
                    data_str = data_str.strftime('%d/%m/%Y')
                elif isinstance(data_str, str) and len(data_str) >= 10:
                    try:
                        data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                        data_str = data_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        pass
                data_item = QTableWidgetItem(str(data_str))
                self.inspection_table.setItem(i, 1, data_item)
                
                # Tipo
                tipo_item = QTableWidgetItem(inspecao.get('tipo_inspecao', ''))
                self.inspection_table.setItem(i, 2, tipo_item)
                
                # Engenheiro (nome)
                eng_nome = inspecao.get('engenheiro_nome', f"ID: {inspecao.get('engenheiro_id', 0)}")
                eng_item = QTableWidgetItem(eng_nome)
                self.inspection_table.setItem(i, 3, eng_item)
                
                # Resultado
                resultado_item = QTableWidgetItem(inspecao.get('resultado', ''))
                self.inspection_table.setItem(i, 4, resultado_item)
            
            logger.debug(f"Carregadas {len(inspecoes)} inspeções")
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
            
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        try:
            logger.debug("Carregando relatórios")
            
            # Força a sincronização antes de carregar
            self.report_controller.force_sync()
            
            reports = self.report_controller.get_all_reports()
            self.report_table.setRowCount(len(reports))
            
            for i, report in enumerate(reports):
                try:
                    # Armazena o ID como dados do item (invisível para o usuário)
                    report_id = report.get('id', '')
                    
                    # Inspeção (combina tipo e equipamento)
                    inspecao_info = f"{report.get('tipo_inspecao', 'N/A')} - {report.get('equipamento_tag', 'N/A')}"
                    insp_item = QTableWidgetItem(inspecao_info)
                    insp_item.setData(Qt.UserRole, report_id)  # Armazena o ID do relatório
                    self.report_table.setItem(i, 0, insp_item)
                    
                    # Data
                    data_str = report.get('data_emissao', '')
                    if isinstance(data_str, str) and len(data_str) >= 10:
                        try:
                            data_obj = datetime.strptime(data_str[:10], '%Y-%m-%d')
                            data_str = data_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            pass
                    data_item = QTableWidgetItem(data_str)
                    self.report_table.setItem(i, 1, data_item)
                    
                    # Arquivo
                    arquivo_item = QTableWidgetItem(report.get('link_arquivo', ''))
                    self.report_table.setItem(i, 2, arquivo_item)
                    
                    # Observações
                    obs_item = QTableWidgetItem(report.get('observacoes', ''))
                    self.report_table.setItem(i, 3, obs_item)
                    
                    # Status (baseado na existência do arquivo)
                    tem_arquivo = bool(report.get('link_arquivo'))
                    status_item = QTableWidgetItem("Concluído" if tem_arquivo else "Pendente")
                    status_item.setForeground(QColor('#28a745' if tem_arquivo else '#dc3545'))
                    self.report_table.setItem(i, 4, status_item)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar relatório {i}: {str(e)}")
                    continue
            
            logger.debug(f"Carregados {len(reports)} relatórios")
            
        except Exception as e:
            logger.error(f"Erro ao carregar relatórios: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar relatórios: {str(e)}")
            
    def add_user(self):
        """Abre o modal para adicionar um novo usuário"""
        try:
            modal = UserModal(self)
            if modal.exec():
                user_data = modal.get_data()
                success, message = self.auth_controller.criar_usuario(
                    nome=user_data['nome'],
                    email=user_data['email'],
                    senha=user_data['senha'],
                    tipo_acesso=user_data['tipo'],
                    empresa=user_data['empresa']
                )
                
                # Força a sincronização
                self.auth_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Erro", message)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar usuário: {str(e)}")
                
    def add_equipment(self):
        """Abre o modal para adicionar um novo equipamento"""
        try:
            modal = EquipmentModal(self, self.is_dark)
            
            # Carrega as empresas no modal
            companies = self.auth_controller.get_companies()
            modal.load_company_options(companies)
            
            if modal.exec() == QDialog.Accepted:
                equipment_data = modal.get_data()
                
                # O ID da empresa já vem do modal
                empresa_id = equipment_data.get('empresa_id')
                
                if not empresa_id:
                    QMessageBox.warning(self, "Erro", "Nenhuma empresa foi selecionada ou o ID é inválido.")
                    return
                
                # Criar o equipamento
                success, message = self.equipment_controller.criar_equipamento(
                    tag=equipment_data['tag'],
                    categoria=equipment_data['categoria'],
                    empresa_id=empresa_id, # Passa o ID diretamente
                    fabricante=equipment_data['fabricante'],
                    ano_fabricacao=equipment_data['ano_fabricacao'],
                    pressao_projeto=equipment_data['pressao_projeto'],
                    pressao_trabalho=equipment_data['pressao_trabalho'],
                    volume=equipment_data['volume'],
                    fluido=equipment_data['fluido'],
                    # Campos NR-13
                    categoria_nr13=equipment_data.get('categoria_nr13'),
                    pmta=equipment_data.get('pmta'),
                    placa_identificacao=equipment_data.get('placa_identificacao'),
                    numero_registro=equipment_data.get('numero_registro')
                )
                
                # Força a sincronização
                self.equipment_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_equipment()
                else:
                    QMessageBox.critical(self, "Erro", message)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar equipamento: {str(e)}")
            logger.error(f"Erro no add_equipment: {traceback.format_exc()}")
            
    def add_inspection(self):
        """Abre o modal para adicionar uma nova inspeção"""
        try:
            logging.info("Abrindo modal para adicionar nova inspeção")
            
            # Verificar se há equipamentos cadastrados
            equipamentos = self.equipment_controller.get_all_equipment()
            if not equipamentos:
                QMessageBox.warning(self, "Atenção", "Não há equipamentos cadastrados. "
                                  "Cadastre pelo menos um equipamento antes de adicionar inspeções.")
                return
                
            # Verificar se há engenheiros cadastrados
            engenheiros = self.auth_controller.get_engineers()
            if not engenheiros:
                QMessageBox.warning(self, "Atenção", "Não há engenheiros cadastrados. "
                                  "Cadastre pelo menos um engenheiro antes de adicionar inspeções.")
                return
                
            # Abre o modal para adicionar inspeção
            dark_mode = False  # Valor padrão para o modo escuro
            try:
                dark_mode = self.is_dark_theme  # Tenta usar a propriedade is_dark_theme
            except:
                pass  # Ignora se não existir
                
            modal = InspectionModal(self, dark_mode)
            
            # Popula o modal com os dados iniciais
            modal.load_equipment_options(equipamentos)
            modal.load_engineer_options(engenheiros)
            
            # Exibe o modal
            if modal.exec():
                # Se o usuário confirmou, obtém os dados
                inspection_data = modal.get_data()
                
                # Cria a inspeção
                success, message = self.inspection_controller.criar_inspecao(
                    equipamento_id=inspection_data['equipamento_id'],
                    engenheiro_id=inspection_data['engenheiro_id'],
                    data_inspecao=inspection_data['data_inspecao'],
                    tipo_inspecao=inspection_data['tipo_inspecao'],
                    resultado=inspection_data.get('resultado', 'Pendente'),
                    recomendacoes=inspection_data.get('recomendacoes', '')
                )
                
                # Força a sincronização
                self.inspection_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_inspections()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logging.error(f"Erro ao adicionar inspeção: {str(e)}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar inspeção: {str(e)}")

    def show_error(self, message):
        """Exibe uma mensagem de erro em uma caixa de diálogo"""
        logging.error(message)
        QMessageBox.critical(self, "Erro", message)
    
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
                success, message = self.inspection_controller.atualizar_inspecao(
                    self.current_inspection_id,
                    inspection_data
                )
                
                # Força a sincronização
                self.inspection_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.clear_inspection_form()
                    self.load_inspections()
                else:
                    QMessageBox.critical(self, "Erro", message)
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
                
                # Força a sincronização
                self.inspection_controller.force_sync()
                
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
        try:
            logger.debug("Limpando formulário de inspeção")
            # Verifica se os componentes existem antes de tentar acessá-los
            if hasattr(self, 'insp_equipamento_combo'):
                self.insp_equipamento_combo.setCurrentIndex(0)
            
            if hasattr(self, 'insp_engenheiro_combo'):
                self.insp_engenheiro_combo.setCurrentIndex(0)
            
            if hasattr(self, 'insp_data_input'):
                self.insp_data_input.setDate(QDate.currentDate())
            
            if hasattr(self, 'insp_tipo_combo'):
                self.insp_tipo_combo.setCurrentIndex(0)
            
            if hasattr(self, 'insp_resultado_combo'):
                self.insp_resultado_combo.setCurrentIndex(0)
            
            if hasattr(self, 'insp_recomendacoes_input'):
                self.insp_recomendacoes_input.clear()
            
            # Reset do ID da inspeção atual
            if hasattr(self, 'current_inspection_id'):
                self.current_inspection_id = None
            
            # Atualiza o título e botão
            if hasattr(self, 'insp_form_title'):
                self.insp_form_title.setText("Nova Inspeção")
            
            if hasattr(self, 'insp_save_btn'):
                self.insp_save_btn.setText("Salvar")
            
            logger.debug("Formulário de inspeção limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar formulário de inspeção: {str(e)}")
            logger.error(traceback.format_exc())
    
    def load_inspection_details(self):
        """Carrega os detalhes da inspeção selecionada no formulário"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            return
        
        # Obtém a linha selecionada
        row = selected_rows[0].row()
        
        try:
            # Obtém o ID da inspeção a partir de UserRole no primeiro item da linha
            equipment_item = self.inspection_table.item(row, 0)
            if not equipment_item:
                logger.warning("Não foi possível identificar o item de equipamento para a inspeção selecionada")
                return
                
            inspection_id = equipment_item.data(Qt.UserRole)
            if not inspection_id:
                logger.warning("ID da inspeção não encontrado nos dados do item")
                return
                
            logger.debug(f"Carregando detalhes da inspeção ID: {inspection_id}")
                
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
            index = self.insp_equipamento_combo.findData(inspection['equipamento_id'])
            if index >= 0:
                self.insp_equipamento_combo.setCurrentIndex(index)
            
            # Seleciona o engenheiro correto
            index = self.insp_engenheiro_combo.findData(inspection['engenheiro_id'])
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
            logger.error(traceback.format_exc())
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
        try:
            # Obter o ID da inspeção selecionada
            if self.inspection_table.selectedItems():
                row = self.inspection_table.currentRow()
                inspection_id_item = self.inspection_table.item(row, 0)
                if inspection_id_item:
                    # Obter o ID da inspeção através do Qt.UserRole
                    inspection_id = inspection_id_item.data(Qt.UserRole)
                    if not inspection_id:
                        QMessageBox.warning(self, "Erro", "ID da inspeção não encontrado.")
                        return
                    
                    # Confirmação
                    reply = QMessageBox.question(
                        self,
                        "Confirmar Exclusão",
                        f"Tem certeza que deseja excluir a inspeção #{inspection_id}?\n\n"
                        "Esta ação não pode ser desfeita e todos os relatórios associados serão excluídos.",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        # Tenta excluir a inspeção
                        success = self.inspection_controller.delete_inspection(inspection_id)
                        
                        if success:
                            QMessageBox.information(self, "Sucesso", f"Inspeção #{inspection_id} excluída com sucesso!")
                            # Atualiza a lista de inspeções
                            self.load_inspections()
                            # Limpa o formulário
                            self.clear_inspection_form()
                            # Atualiza todas as tabelas para refletir as mudanças
                            self.refresh_all_tables()
                        else:
                            QMessageBox.critical(self, "Erro", f"Não foi possível excluir a inspeção #{inspection_id}.")
                else:
                    QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para excluir.")
            else:
                QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para excluir.")
        except Exception as e:
            logger.error(f"Erro ao excluir inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao excluir inspeção: {str(e)}")

    def generate_report_from_inspection(self):
        """Gera um relatório a partir da inspeção selecionada"""
        selected_rows = self.inspection_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma inspeção para gerar o relatório.")
            return
        
        # Obtém a linha selecionada
        row = selected_rows[0].row()
        
        try:
            # Obtém o ID da inspeção a partir de UserRole no primeiro item da linha
            equipment_item = self.inspection_table.item(row, 0)
            if not equipment_item:
                QMessageBox.warning(self, "Erro", "Não foi possível identificar a inspeção.")
                return
                
            inspection_id = equipment_item.data(Qt.UserRole)
            if not inspection_id:
                QMessageBox.warning(self, "Erro", "ID da inspeção não encontrado.")
                return
                
            logger.debug(f"Gerando relatório para inspeção ID: {inspection_id}")
            
            # Busca os detalhes da inspeção
            inspection = self.inspection_controller.get_inspection_by_id(inspection_id)
            
            if not inspection:
                logger.warning(f"Inspeção {inspection_id} não encontrada")
                QMessageBox.warning(self, "Erro", "Inspeção não encontrada no banco de dados.")
                return
            
            # Muda para a aba de relatórios
            self.tabs.setCurrentIndex(3)  # Aba de relatórios
            
            # Preenche o formulário de relatório com dados da inspeção
            
            # Seleciona a inspeção no combo
            index = self.report_inspecao_combo.findData(inspection_id)
            if index >= 0:
                self.report_inspecao_combo.setCurrentIndex(index)
            
            # Define o título automático
            equip_tag = inspection.get('equipamento_tag', 'Equipamento')
            data = QDate.fromString(inspection['data_inspecao'], "yyyy-MM-dd").toString("dd/MM/yyyy")
            self.report_titulo_input.setText(f"Relatório de Inspeção - {equip_tag} - {data}")
            
            # Define o tipo com base na inspeção
            index = self.report_tipo_combo.findText(inspection['tipo_inspecao'])
            if index >= 0:
                self.report_tipo_combo.setCurrentIndex(index)
            
            # Define o resultado com base na inspeção
            index = self.report_resultado_combo.findText(inspection['resultado'])
            if index >= 0:
                self.report_resultado_combo.setCurrentIndex(index)
            
            # Foca no campo de observações para o usuário continuar preenchendo
            self.report_observacoes_input.setFocus()
            
            # Define o modo de edição para criar um novo relatório
            self.toggle_report_form_mode(is_editing=False)
            
            QMessageBox.information(
                self, 
                "Relatório Iniciado", 
                f"Formulário preenchido com dados da inspeção do equipamento {equip_tag}.\n\n"
                "Complete as informações e pressione Salvar para gerar o relatório."
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório a partir da inspeção: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao gerar relatório: {str(e)}")

    def get_selected_user_id(self):
        """Retorna o ID do usuário selecionado na tabela"""
        try:
            # Verifica se há uma linha selecionada
            selected_rows = self.user_table.selectedItems()
            if not selected_rows:
                logger.warning("Nenhuma linha selecionada na tabela de usuários")
                return None
                
            row = selected_rows[0].row()
            logger.debug(f"Linha selecionada na tabela de usuários: {row}")
            
            # Tenta obter o ID do usuário a partir do item da coluna nome (coluna 0)
            nome_item = self.user_table.item(row, 0)
            if not nome_item:
                logger.warning(f"Item da coluna nome é None para a linha {row}")
                return None
                
            user_id = nome_item.data(Qt.UserRole)
            logger.debug(f"ID do usuário obtido: {user_id}, Nome: {nome_item.text()}")
            
            # Se não conseguiu obter o ID, tenta buscar o usuário pelo nome
            if not user_id:
                nome = nome_item.text()
                logger.debug(f"Tentando obter ID pelo nome: {nome}")
                
                users = self.auth_controller.get_all_users()
                for user in users:
                    if user.get('nome') == nome:
                        user_id = user.get('id')
                        logger.debug(f"ID encontrado pelo nome: {user_id}")
                        break
            
            # Se ainda não encontrou, tenta verificar o userData de todas as colunas
            if not user_id:
                logger.debug("Tentando obter ID de todas as colunas")
                for col in range(self.user_table.columnCount()):
                    item = self.user_table.item(row, col)
                    if item and item.data(Qt.UserRole):
                        user_id = item.data(Qt.UserRole)
                        logger.debug(f"ID encontrado na coluna {col}: {user_id}")
                        break
            
            return user_id
        except Exception as e:
            logger.error(f"Erro ao obter ID do usuário: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def edit_selected_user(self, user_id=None, force_type=None):
        """Abre o modal para editar o usuário selecionado"""
        try:
            # Se o user_id não foi passado, tenta obter da linha selecionada
            if not user_id:
                user_id = self.get_selected_user_id()
                if not user_id:
                    QMessageBox.warning(self, "Atenção", "Selecione um usuário na tabela.")
                    return
                logger.debug(f"Editando usuário ID: {user_id}")
            
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
                    success, message = self.auth_controller.atualizar_usuario(
                        user_id, 
                        data['nome'], 
                        data['email'], 
                        tipo_acesso, 
                        data['empresa'], 
                        data['senha'] if data['senha'] else None
                    )
                    
                    if success:
                        QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
                        self.load_users()
                        # Se estamos editando um engenheiro, atualizar a lista de engenheiros também
                        if tipo_acesso == "eng" or user.get('tipo_acesso') == "eng":
                            self.load_engineers()
                    else:
                        QMessageBox.critical(self, "Erro", f"Erro ao atualizar usuário: {message}")
                else:
                    QMessageBox.information(self, "Informação", "Nenhuma alteração foi feita.")
        except Exception as e:
            logger.error(f"Erro ao editar usuário: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Falha ao editar usuário: {str(e)}")

    def toggle_selected_user(self):
        """Ativa ou desativa o usuário selecionado"""
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Atenção", "Selecione um usuário para alterar o status.")
            return
            
        # Obtém o usuário
        user = self.auth_controller.get_user_by_id(user_id)
        if not user:
            QMessageBox.warning(self, "Erro", f"Usuário ID {user_id} não encontrado.")
            return
            
        # Define a ação com base no status atual
        current_status = user.get('ativo', False)
        new_status = not current_status
        action_verb = "desativar" if current_status else "ativar"
        action_past = "desativado" if current_status else "ativado"
        
        # Confirmação
        reply = QMessageBox.question(
            self, 
            f"Confirmar {action_verb}", 
            f"Tem certeza que deseja {action_verb} o usuário {user['nome']}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Executa a ação
        status_action = self.auth_controller.desativar_usuario if current_status else self.auth_controller.reativar_usuario
        success = status_action(user_id)
        
        # Força a sincronização
        self.auth_controller.force_sync()
        
        if success:
            QMessageBox.information(self, "Sucesso", f"Usuário {action_past} com sucesso!")
            self.load_users()
            self.update_toggle_button()
        else:
            QMessageBox.critical(self, "Erro", f"Falha ao {action_verb} usuário.")

    def remove_selected_user(self):
        """Remove o usuário selecionado"""
        try:
            user_id = self.get_selected_user_id()
            if not user_id:
                QMessageBox.warning(self, "Atenção", "Selecione um usuário para remover.")
                return
                
            # Obtém os dados do usuário
            user = self.auth_controller.get_user_by_id(user_id)
            if not user:
                QMessageBox.warning(self, "Erro", f"Usuário ID {user_id} não encontrado.")
                return
                
            # Confirmação
            reply = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                f"Tem certeza que deseja remover permanentemente o usuário '{user['nome']}'?\n\n"
                "Esta ação não pode ser desfeita e todos os dados associados serão perdidos.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Desativa o usuário em vez de excluir permanentemente
                success = self.auth_controller.desativar_usuario(user_id)
                
                # Força a sincronização
                self.auth_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", f"Usuário '{user['nome']}' removido com sucesso!")
                    self.load_users()
                    # Atualizar todas as tabelas após a exclusão
                    self.refresh_all_tables()
                else:
                    QMessageBox.critical(self, "Erro", f"Não foi possível remover o usuário '{user['nome']}'.")
                    
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao remover usuário: {str(e)}")

    def update_toggle_button(self):
        """Atualiza o botão de ativar/desativar baseado no usuário selecionado"""
        try:
            # Certifique-se de que o botão de remover sempre esteja visível
            if not self.remove_user_button.isVisible():
                logger.debug("Restaurando visibilidade do botão de remover")
                self.remove_user_button.setVisible(True)
                
            selected_rows = self.user_table.selectedItems()
            if not selected_rows:
                # Ocultar apenas o botão de ativar/desativar
                self.toggle_user_button.setVisible(False)
                return
            
            # Mostrar o botão de ativar/desativar se estiver oculto
            if not self.toggle_user_button.isVisible():
                self.toggle_user_button.setVisible(True)
                
            # Obter a linha selecionada e verificar o status do usuário
            row = selected_rows[0].row()
            status_item = self.user_table.item(row, 3)  # Coluna status (ajustado após remoção da coluna ID)
            
            if not status_item:
                self.toggle_user_button.setVisible(False)
                return
                
            is_active = status_item.text() == "Ativo"
            
            if is_active:
                self.toggle_user_button.setText("Desativar")
                self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['disable']))
                self.toggle_user_button.setStyleSheet(self.button_style['delete'])  # Usa o estilo de delete para o botão desativar
            else:
                self.toggle_user_button.setText("Ativar")
                self.toggle_user_button.setIcon(self.create_icon_from_svg(self.icons['enable']))
                self.toggle_user_button.setStyleSheet(self.button_style['add'])  # Usa o estilo de add para o botão ativar
            
        except Exception as e:
            logger.error(f"Erro ao atualizar botão de ativar/desativar: {str(e)}")
            logger.error(traceback.format_exc())

    def filter_users(self, text):
        """Filtra os usuários na tabela baseado no texto de pesquisa"""
        try:
            search_text = text.lower()
            
            # Certifique-se de que o botão de remover esteja visível
            if not self.remove_user_button.isVisible():
                logger.debug("Restaurando visibilidade do botão de remover")
                self.remove_user_button.setVisible(True)
            
            # Resetar visibilidade de todas as linhas se a pesquisa estiver vazia
            if not search_text:
                for row in range(self.user_table.rowCount()):
                    self.user_table.setRowHidden(row, False)
                logger.debug("Filtro de usuários limpo - mostrando todas as linhas")
                return
                
            # Aplicar filtro apenas se houver texto de pesquisa
            hidden_count = 0
            for row in range(self.user_table.rowCount()):
                should_show = False
                for col in range(self.user_table.columnCount()):
                    item = self.user_table.item(row, col)
                    if item and search_text in item.text().lower():
                        should_show = True
                        break
                
                self.user_table.setRowHidden(row, not should_show)
                if not should_show:
                    hidden_count += 1
                
            logger.debug(f"Filtro aplicado: '{search_text}' - {hidden_count} linhas ocultas")
                
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
                    report_id=editing_id,
                    inspecao_id=report_data['inspecao_id'],
                    data_emissao=report_data['data_emissao'],
                    link_arquivo=report_data['link_arquivo'],
                    observacoes=report_data['observacoes']
                )
                message = "Relatório atualizado com sucesso!" if success else "Erro ao atualizar relatório."
            else:
                # Cria um novo relatório
                success, message = self.report_controller.criar_relatorio(
                    inspecao_id=report_data['inspecao_id'],
                    data_emissao=report_data['data_emissao'],
                    link_arquivo=report_data['link_arquivo'],
                    observacoes=report_data['observacoes']
                )
                
            if success:
                # Força a sincronização com o banco de dados
                self.report_controller.force_sync()
                
                QMessageBox.information(self, "Sucesso", message if isinstance(message, str) else "Operação realizada com sucesso!")
                self.clear_report_form()
                # Atualiza a tabela de relatórios
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
            selected_rows = self.report_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um relatório para editar.")
                return
            
            row = selected_rows[0].row()
            
            # Obtém o ID do relatório usando Qt.UserRole em vez do texto
            report_item = self.report_table.item(row, 0)
            if not report_item:
                QMessageBox.warning(self, "Erro", "Não foi possível identificar o relatório.")
                return
                
            report_id = report_item.data(Qt.UserRole)
            if not report_id:
                QMessageBox.warning(self, "Erro", "ID do relatório não encontrado.")
                return
                
            logger.debug(f"Editando relatório ID: {report_id}")
            
            # Busca os dados do relatório
            report = self.report_controller.get_report_by_id(report_id)
            if not report:
                QMessageBox.warning(self, "Erro", "Relatório não encontrado.")
                return
            
            # Cria e configura o modal
            modal = ReportModal(self, self.is_dark)
            modal.setWindowTitle("Editar Relatório")
            
            # Conecta o sinal reportSaved ao método load_reports
            modal.reportSaved.connect(self.load_reports)
            
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
                
                # Força a sincronização com o banco de dados
                self.report_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Relatório atualizado com sucesso!")
                    # Garante que a tabela seja atualizada
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
            selected_rows = self.report_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Selecione um relatório para excluir.")
                return
            
            # Obtém a linha selecionada
            row = selected_rows[0].row()
            
            # Obtém o ID do relatório selecionado
            report_id_item = self.report_table.item(row, 0)
            if not report_id_item:
                QMessageBox.warning(self, "Erro", "Não foi possível identificar o relatório.")
                return
                
            report_id = int(report_id_item.text())
            logger.debug(f"Excluindo relatório ID: {report_id}")
            
            # Confirmação
            reply = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o relatório #{report_id}?\n\n"
                "Esta ação não pode ser desfeita.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = self.report_controller.delete_report(report_id)
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_reports()
                    self.clear_report_form()
                    # Atualizar todas as tabelas após a exclusão
                    self.refresh_all_tables()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao excluir relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao excluir relatório: {str(e)}")

    def view_selected_report(self):
        """Visualiza o arquivo do relatório selecionado"""
        try:
            selected_rows = self.report_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Atenção", "Por favor, selecione um relatório para visualizar.")
                return
            
            row = selected_rows[0].row()
            
            # Obter a coluna que contém o caminho do arquivo (geralmente coluna 2 - índice 2)
            arquivo_item = self.report_table.item(row, 2)
            if not arquivo_item:
                QMessageBox.warning(self, "Atenção", "Não foi possível identificar o arquivo do relatório.")
                return
                
            arquivo = arquivo_item.text()
            
            if not arquivo:
                QMessageBox.warning(self, "Atenção", "Este relatório não possui arquivo anexado.")
                return
            
            if not os.path.exists(arquivo):
                QMessageBox.warning(self, "Erro", f"O arquivo não foi encontrado no caminho especificado:\n{arquivo}")
                return
            
            # Abre o arquivo com o programa padrão do sistema
            import subprocess
            import platform
            
            try:
                logger.debug(f"Tentando abrir arquivo: {arquivo}")
                if platform.system() == 'Windows':
                    os.startfile(arquivo)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', arquivo])
                else:  # Linux e outros
                    subprocess.run(['xdg-open', arquivo])
                logger.debug(f"Arquivo aberto com sucesso: {arquivo}")
            except Exception as e:
                logger.error(f"Falha ao abrir arquivo {arquivo}: {str(e)}")
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
        """Abre o modal para adicionar um relatório"""
        try:
            # Cria e configura o modal
            modal = ReportModal(self, self.is_dark)
            modal.setWindowTitle("Novo Relatório")
            
            # Conecta o sinal reportSaved ao método load_reports
            modal.reportSaved.connect(self.load_reports)
            
            # Carrega as inspeções
            inspecoes = self.inspection_controller.get_all_inspections()
            modal.inspecao_combo.clear()
            
            if not inspecoes:
                QMessageBox.warning(self, "Atenção", "Não há inspeções cadastradas. Cadastre uma inspeção primeiro.")
                return
                
            # Adiciona as inspeções ao combo
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

    def filter_equipment(self, text):
        """Filtra os equipamentos na tabela com base no texto inserido e empresa selecionada"""
        try:
            search_text = text.lower()
            logger.debug(f"Filtrando equipamentos com texto: '{search_text}'")
            
            company_id = self.equipment_company_selector.currentData()
            logger.debug(f"Empresa selecionada ID={company_id}")
            
            for row in range(self.equipment_table.rowCount()):
                should_show = True
                
                # Filtro por empresa
                if company_id is not None:
                    item_empresa = self.equipment_table.item(row, 2)  # Coluna Empresa
                    if not item_empresa or int(item_empresa.data(Qt.UserRole)) != company_id:
                        should_show = False
                        
                # Filtro por texto
                if should_show and search_text:
                    found = False
                    for col in range(self.equipment_table.columnCount()):
                        item = self.equipment_table.item(row, col)
                        if item and search_text in item.text().lower():
                            found = True
                            break
                    should_show = found
                    
                self.equipment_table.setRowHidden(row, not should_show)
                
            logger.debug("Filtro de equipamentos aplicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
    
    def get_equipment_id(self, row):
        """
        Obtém o ID do equipamento a partir de uma linha selecionada na tabela.
        Tenta várias abordagens para garantir que o ID seja encontrado.
        
        Args:
            row: Número da linha na tabela
            
        Returns:
            tuple: (equipment_id, tag_text) ou (None, tag_text) se não encontrado
        """
        try:
            # Garantir que estamos obtendo o item da primeira coluna
            tag_item = self.equipment_table.item(row, 0)  # A coluna Tag contém o ID nos dados do item
            if tag_item is None:
                logger.error(f"Item da coluna Tag é None para a linha {row}")
                return None, ""
                
            tag_text = tag_item.text()
            logger.debug(f"Tag do equipamento: {tag_text}")
            
            # Tentativa 1: buscar ID pelo UserRole
            equipment_id = tag_item.data(Qt.UserRole)
            logger.debug(f"Tentativa 1 - ID do equipamento obtido via UserRole: {equipment_id}")
            
            # Tentativa 2: buscar pelo tag se UserRole falhar
            if not equipment_id:
                logger.debug("Tentativa 1 falhou. Tentando buscar pelo tag...")
                equipment = self.equipment_controller.get_equipment_by_tag(tag_text)
                if equipment:
                    equipment_id = equipment.get('id')
                    logger.debug(f"Tentativa 2 - ID encontrado pelo tag: {equipment_id}")
            
            # Tentativa 3: Solicitar ID manualmente
            if not equipment_id:
                logger.debug("Tentativas 1 e 2 falharam. Solicitando ID manualmente...")
                # Listar todos os equipamentos para ajudar o usuário a identificar
                all_equipments = self.equipment_controller.get_all_equipment()
                equipment_info = "\n".join([f"ID: {eq['id']} - Tag: {eq['tag']}" for eq in all_equipments if eq['tag'] == tag_text])
                
                # Se encontramos equipamentos com este tag, mostrar a lista
                if equipment_info:
                    logger.debug(f"Equipamentos encontrados com tag '{tag_text}': {equipment_info}")
                    text, ok = QInputDialog.getText(
                        self, 
                        "Informe o ID do Equipamento",
                        f"Não foi possível obter o ID automaticamente.\nEquipamentos com tag '{tag_text}':\n\n{equipment_info}\n\nInforme o ID:"
                    )
                    if ok and text.strip():
                        try:
                            equipment_id = int(text.strip())
                            logger.debug(f"Tentativa 3 - ID informado manualmente: {equipment_id}")
                        except ValueError:
                            return None, tag_text
                else:
                    logger.warning(f"Não foi possível encontrar equipamentos com tag '{tag_text}'")
                    return None, tag_text
            
            return equipment_id, tag_text
            
        except Exception as e:
            logger.error(f"Erro ao obter ID do equipamento: {str(e)}")
            logger.error(traceback.format_exc())
            return None, ""
            
    def edit_equipment(self):
        """Edita o equipamento selecionado"""
        try:
            equipment_id = self.get_selected_equipment_id()
            if not equipment_id:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para editar.")
                return
                
            # Busca os dados do equipamento
            equipment = self.equipment_controller.get_equipment_by_id(equipment_id)
            if not equipment:
                QMessageBox.warning(self, "Erro", f"Equipamento ID {equipment_id} não encontrado.")
                return
                
            # Cria o modal de edição
            modal = EquipmentModal(self, self.is_dark, equipment)
            
            # Carrega as empresas no modal (importante para permitir edição do campo empresa)
            companies = self.auth_controller.get_companies()
            modal.load_company_options(companies)
            
            if modal.exec_() == QDialog.Accepted:
                # Obtém os novos dados
                new_data = modal.get_data()
                
                # Atualiza o equipamento
                success, message = self.equipment_controller.update_equipment(equipment_id, **new_data)
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    # Recarrega a lista de equipamentos
                    self.load_equipment()
                    # Atualiza todas as tabelas para refletir as mudanças
                    self.refresh_all_tables()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao editar equipamento: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao editar equipamento: {str(e)}")

    def toggle_equipment(self):
        """Ativa ou desativa o equipamento selecionado"""
        try:
            equipment_id = self.get_selected_equipment_id()
            if not equipment_id:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para alterar o status.")
                return
                
            # Busca os dados do equipamento
            equipment = self.equipment_controller.get_equipment_by_id(equipment_id)
            if not equipment:
                QMessageBox.warning(self, "Erro", f"Equipamento ID {equipment_id} não encontrado.")
                return
                
            # Define a ação com base no status atual
            current_status = equipment.get('ativo', False)
            new_status = not current_status
            action_verb = "desativar" if current_status else "ativar"
            
            # Confirmação
            reply = QMessageBox.question(
                self, 
                f"Confirmar {action_verb}", 
                f"Tem certeza que deseja {action_verb} o equipamento {equipment['tag']}?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # Executa a ação
            success, message = self.equipment_controller.toggle_equipment_status(equipment_id, new_status)
            
            # Força a sincronização
            self.equipment_controller.force_sync()
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_equipment()
                self.update_toggle_equipment_button()
            else:
                QMessageBox.critical(self, "Erro", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao alterar status do equipamento: {str(e)}")

    def delete_equipment(self):
        """Remove um equipamento do sistema"""
        try:
            equipment_id = self.get_selected_equipment_id()
            if not equipment_id:
                QMessageBox.warning(self, "Aviso", "Selecione um equipamento para excluir")
                return
                
            # Pedir confirmação antes de excluir
            confirm = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o equipamento ID {equipment_id}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                success, message = self.equipment_controller.delete_equipment(equipment_id)
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    # Atualizar a tabela após exclusão
                    self.load_equipment()
                    # Atualizar as inspeções e relatórios se o equipamento foi excluído com sucesso
                    self.refresh_all_tables()
                else:
                    QMessageBox.warning(self, "Erro", message)
        except Exception as e:
            logger.error(f"Erro ao excluir equipamento: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao excluir equipamento: {str(e)}")

    def update_toggle_equipment_button(self):
        """Atualiza o estado do botão de toggle de acordo com o item selecionado"""
        try:
            # Obter o ID do equipamento selecionado
            equipment_id = self.get_selected_equipment_id()
            
            if not equipment_id:
                # Desabilitar botões se nenhum equipamento estiver selecionado
                self.toggle_equipment_button.setEnabled(False)
                self.edit_equipment_button.setEnabled(False)
                self.delete_equipment_button.setEnabled(False)
                self.maintenance_button.setEnabled(False)
                return
            
            # Habilitar botões de edição e exclusão
            self.edit_equipment_button.setEnabled(True)
            self.delete_equipment_button.setEnabled(True)
            self.maintenance_button.setEnabled(True)
            
            # Buscar o status atual do equipamento
            equipment_data = self.equipment_controller.get_equipment_by_id(equipment_id)
            
            if not equipment_data:
                logger.error(f"Equipamento com ID {equipment_id} não encontrado")
                return
                
            is_active = equipment_data.get('ativo', 1)
            
            # Atualizar o texto e o estilo do botão
            if is_active:
                self.toggle_equipment_button.setText("Desativar")
                self.toggle_equipment_button.setToolTip("Desativar este equipamento")
                new_style = self.button_style['delete'].replace("background-color: #dc3545;", "background-color: #dc3545;")
            else:
                self.toggle_equipment_button.setText("Ativar")
                self.toggle_equipment_button.setToolTip("Ativar este equipamento")
                new_style = self.button_style['add'].replace("background-color: #28a745;", "background-color: #28a745;")
            
            self.toggle_equipment_button.setStyleSheet(new_style)
            self.toggle_equipment_button.setEnabled(True)
        except Exception as e:
            logger.error(f"Erro ao atualizar botão de ativar/desativar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())

    def get_selected_equipment_id(self):
        """Retorna o ID do equipamento selecionado na tabela"""
        try:
            # Verifica se há uma linha selecionada
            selected_items = self.equipment_table.selectedItems()
            if not selected_items:
                logger.warning("Nenhuma linha selecionada na tabela de equipamentos")
                return None
                
            # Obtém a linha selecionada
            row = selected_items[0].row()
            
            # Tentativa 1: Obter via UserRole do próprio item
            id_item = self.equipment_table.item(row, 0)  # Primeira coluna deve ter o ID como dado adicional
            equipment_id = id_item.data(Qt.UserRole)
            
            if equipment_id:
                logger.debug(f"Tentativa 1 - ID do equipamento obtido via UserRole: {equipment_id}")
                return equipment_id
                
            # Tentativa 2: Verificar se temos um ID armazenado para essa linha
            linha_tag = self.equipment_table.model().index(row, 0).data()
            logger.debug(f"Linha {row}, Tag: {linha_tag}")
            
            # Se temos um dicionário de linha -> id, podemos usar aqui
            # Ex: if hasattr(self, 'equipment_ids') and row in self.equipment_ids:
            #        return self.equipment_ids[row]
                    
            # Tentativa 3: Buscar pelo tag
            tag_text = id_item.text()
            if tag_text:
                equipment = self.equipment_controller.get_equipment_by_tag(tag_text)
                if equipment:
                    equipment_id = equipment['id']
                    logger.debug(f"Tentativa 3 - ID do equipamento obtido via tag: {equipment_id}")
                    return equipment_id
            
            logger.warning(f"Não foi possível obter o ID do equipamento na linha {row}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter ID do equipamento: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def show_user_tab(self):
        """Muda para a aba de usuários e destaca o botão de remover"""
        try:
            # Mudar para a aba de Usuários (índice 0)
            self.tabs.setCurrentIndex(0)
            
            # Destacar o botão "Remover Usuário" temporariamente
            original_style = self.remove_user_button.styleSheet()
            
            # Aplicar estilo destacado (borda pulsante)
            highlight_style = """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: 3px solid gold;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                    border: 3px solid yellow;
                }
            """
            self.remove_user_button.setStyleSheet(highlight_style)
            
            # Restaurar o estilo original após 3 segundos
            def restore_style():
                import time
                time.sleep(3)
                self.remove_user_button.setStyleSheet(original_style)
                
            threading.Thread(target=restore_style).start()
            
            # Garantir que o botão está visível
            self.remove_user_button.setVisible(True)
            
            # Log da operação
            logger.debug("Alterado para aba de usuários e destacado botão de remover")
            
        except Exception as e:
            logger.error(f"Erro ao mostrar aba de usuários: {str(e)}")

    def refresh_all_tables(self):
        """Atualiza todas as tabelas do sistema com dados mais recentes"""
        try:
            logger.debug("Atualizando todas as tabelas")
            
            # Obtém o índice da aba atual para manter o foco após atualização
            current_tab = self.tabs.currentIndex()
            
            # Força a sincronização com o banco de dados em todos os controladores
            self.auth_controller.force_sync()
            self.equipment_controller.force_sync()
            self.inspection_controller.force_sync()
            self.report_controller.force_sync()
            
            # Atualiza cada tabela
            self.load_users()
            self.load_equipment()
            self.load_inspections()
            self.load_reports()
            
            # Retorna para a aba que estava selecionada
            self.tabs.setCurrentIndex(current_tab)
            
            logger.debug("Atualização das tabelas concluída")
        except Exception as e:
            logger.error(f"Erro ao atualizar tabelas: {str(e)}")
            logger.error(traceback.format_exc())
    
    def logout(self):
        """Emite o sinal de logout solicitado."""
        logger.info("Botão de logout clicado.")
        self.logout_requested.emit()
    
    def load_equipment_by_company(self, company_id=None):
        """Carrega os equipamentos de uma empresa específica na tabela"""
        # Verificar se a tabela existe

        if not hasattr(self, 'company_equipment_table') or self.company_equipment_table is None:

            logger.warning("Tabela de equipamentos por empresa não foi inicializada. Inicializando...")

            self.company_equipment_table = QTableWidget()

            self.company_equipment_table.setColumnCount(9)

            self.company_equipment_table.setHorizontalHeaderLabels([

                "Tag", "Categoria", "Fabricante", "Ano Fabricação", 

                "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido", "Status"

            ])


        try:
            logger.debug(f"Carregando equipamentos para empresa ID={company_id}")
            if company_id is None:
                # Se nenhuma empresa for selecionada, limpa a tabela
                self.company_equipment_table.setRowCount(0)
                return
                
            # Obter todos os equipamentos
            all_equipment = self.equipment_controller.get_all_equipment()
            
            # Filtrar apenas os da empresa selecionada
            company_equipment = [e for e in all_equipment if e.get('empresa_id') == company_id]
            
            # Configurar a tabela
            self.company_equipment_table.setRowCount(len(company_equipment))
            
            for i, item in enumerate(company_equipment):
                # Armazena o ID como dados do item (invisível para o usuário)
                equip_id = item.get('id', '')
                
                # Tag
                tag_item = QTableWidgetItem(item.get('tag', ''))
                tag_item.setData(Qt.UserRole, equip_id)  # Armazena o ID como dado do item
                tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)  # Remove a flag de editável
                self.company_equipment_table.setItem(i, 0, tag_item)
                
                # Resto dos campos - todos configurados como não editáveis
                categoria_item = QTableWidgetItem(item.get('categoria', ''))
                categoria_item.setFlags(categoria_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 1, categoria_item)
                
                fabricante_item = QTableWidgetItem(item.get('fabricante', ''))
                fabricante_item.setFlags(fabricante_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 2, fabricante_item)
                
                ano_item = QTableWidgetItem(str(item.get('ano_fabricacao', '')))
                ano_item.setFlags(ano_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 3, ano_item)
                
                pressao_projeto_item = QTableWidgetItem(str(item.get('pressao_projeto', '')))
                pressao_projeto_item.setFlags(pressao_projeto_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 4, pressao_projeto_item)
                
                pressao_trabalho_item = QTableWidgetItem(str(item.get('pressao_trabalho', '')))
                pressao_trabalho_item.setFlags(pressao_trabalho_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 5, pressao_trabalho_item)
                
                volume_item = QTableWidgetItem(str(item.get('volume', '')))
                volume_item.setFlags(volume_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 6, volume_item)
                
                fluido_item = QTableWidgetItem(item.get('fluido', ''))
                fluido_item.setFlags(fluido_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 7, fluido_item)
                
                # Status
                status = "Ativo" if item.get('ativo', 1) else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.company_equipment_table.setItem(i, 8, status_item)
                
                # Verificar se há dados de manutenção para colorir a linha
                frequencia = item.get('frequencia_manutencao')
                data_ultima = item.get('data_ultima_manutencao')
                
                if frequencia and data_ultima and item.get('ativo', 1):
                    try:
                        # Calcular próxima manutenção
                        data_atual = datetime.now().date()
                        data_ultima_obj = datetime.strptime(data_ultima, "%Y-%m-%d").date()
                        data_proxima = data_ultima_obj + timedelta(days=int(frequencia))
                        data_proxima_str = data_proxima.strftime("%Y-%m-%d")
                        
                        # Calcular dias restantes
                        dias_restantes = (data_proxima - data_atual).days
                        
                        # Adicionar coluna para data de próxima manutenção
                        proxima_item = QTableWidgetItem(data_proxima_str)
                        proxima_item.setFlags(proxima_item.flags() & ~Qt.ItemIsEditable)
                        
                        # Definir cores para manutenções próximas
                        if dias_restantes < 0:  # Atrasado
                            if self.is_dark:
                                cor_linha = QColor(90, 10, 10)  # Vermelho muito escuro para tema escuro
                                cor_texto = QColor(255, 130, 130)  # Texto vermelho claro
                            else:
                                cor_linha = QColor(255, 200, 200)  # Vermelho pastel
                                cor_texto = QColor(139, 0, 0)  # Vermelho escuro para contraste
                            
                            # Adiciona indicador visual de manutenção atrasada
                            tag_item.setText("❗ " + tag_item.text())
                        elif dias_restantes <= 7:  # Próximo (1 semana)
                            if self.is_dark:
                                cor_linha = QColor(90, 20, 20)  # Vermelho escuro para tema escuro
                                cor_texto = QColor(255, 150, 150)  # Texto vermelho claro
                            else:
                                cor_linha = QColor(255, 200, 200)  # Vermelho claro
                                cor_texto = QColor(139, 0, 0)  # Texto escuro para contraste
                            
                            # Adiciona indicador visual de manutenção próxima
                            tag_item.setText("❗ " + tag_item.text())
                        elif dias_restantes <= 15:  # Próximo (15 dias)
                            if self.is_dark:
                                cor_linha = QColor(90, 60, 10)  # Laranja escuro para tema escuro
                                cor_texto = QColor(255, 200, 120)  # Texto laranja claro
                            else:
                                cor_linha = QColor(255, 230, 180)  # Laranja claro
                                cor_texto = QColor(102, 51, 0)  # Marrom escuro para contraste
                            
                            # Adiciona indicador visual de manutenção próxima
                            tag_item.setText("⚠️ " + tag_item.text())
                        elif dias_restantes <= 30:  # Próximo (30 dias)
                            if self.is_dark:
                                cor_linha = QColor(90, 90, 10)  # Amarelo escuro para tema escuro
                                cor_texto = QColor(255, 255, 150)  # Texto amarelo claro
                            else:
                                cor_linha = QColor(255, 255, 180)  # Amarelo claro
                                cor_texto = QColor(102, 102, 0)  # Amarelo escuro para contraste
                            
                            # Adiciona indicador visual de manutenção próxima
                            tag_item.setText("⚠️ " + tag_item.text())
                        
                        # Se definimos uma cor, aplicar à linha
                        if 'cor_linha' in locals() and 'cor_texto' in locals():
                            for col in range(self.company_equipment_table.columnCount()):
                                cell = self.company_equipment_table.item(row_index, col)
                                if cell:
                                    cell.setBackground(cor_linha)
                                    cell.setForeground(cor_texto)
                    except Exception as e:
                        logger.error(f"Erro ao calcular manutenção para equipamento: {str(e)}")
            
            logger.debug(f"Carregados {len(company_equipment)} equipamentos da empresa na tabela")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos por empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos por empresa: {str(e)}")
    def company_changed(self, index):
        # Chamado quando a empresa selecionada é alterada
        try:
            # Obter o ID da empresa selecionada
            company_id = self.company_selector.currentData()
            
            # Atualizar a tabela de equipamentos
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao mudar empresa selecionada: {str(e)}")
            logger.error(traceback.format_exc())
            
    def add_equipment_to_company(self):
        # Adiciona um novo equipamento à empresa selecionada
        try:
            # Verificar se uma empresa está selecionada
            company_id = self.company_selector.currentData()
            if company_id is None:
                QMessageBox.warning(self, "Atenção", "Selecione uma empresa primeiro.")
                return
                
            # Reutilizar o método existente, mas pré-configurar a empresa
            modal = EquipmentModal(self, self.is_dark)
            
            # Carregar apenas a empresa selecionada no modal
            company_data = {
                'id': company_id,
                'nome': self.company_selector.currentText()
            }
            modal.load_company_options([company_data])
            
            if modal.exec() == QDialog.Accepted:
                equipment_data = modal.get_data()
                
                # Garantir que o ID da empresa está correto
                equipment_data['empresa_id'] = company_id
                
                # Criar o equipamento
                success, message = self.equipment_controller.criar_equipamento(
                    tag=equipment_data['tag'],
                    categoria=equipment_data['categoria'],
                    empresa_id=equipment_data['empresa_id'],
                    fabricante=equipment_data['fabricante'],
                    ano_fabricacao=equipment_data['ano_fabricacao'],
                    pressao_projeto=equipment_data['pressao_projeto'],
                    pressao_trabalho=equipment_data['pressao_trabalho'],
                    volume=equipment_data['volume'],
                    fluido=equipment_data['fluido']
                )
                
                # Força a sincronização
                self.equipment_controller.force_sync()
                
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_equipment_by_company(company_id)
                    # Atualizar também a aba de equipamentos geral
                    self.load_equipment()
                else:
                    QMessageBox.critical(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao adicionar equipamento à empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar equipamento: {str(e)}")
            
    def edit_company_equipment(self):
        # Edita o equipamento selecionado na aba de empresa
        try:
            # Obter o ID do equipamento selecionado
            selected_row = self.company_equipment_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para editar.")
                return
                
            # Obter o ID do equipamento (armazenado no UserRole da coluna Tag)
            item = self.company_equipment_table.item(selected_row, 0)
            if not item:
                QMessageBox.warning(self, "Erro", "Falha ao obter o equipamento selecionado.")
                return
                
            equipment_id = item.data(Qt.UserRole)
            
            # Reusar o método existente
            self.edit_equipment(equipment_id)
            
            # Atualizar a tabela após a edição
            company_id = self.company_selector.currentData()
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao editar equipamento da empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao editar equipamento: {str(e)}")
            
    def delete_company_equipment(self):
        # Remove o equipamento selecionado na aba de empresa
        try:
            # Obter o ID do equipamento selecionado
            selected_row = self.company_equipment_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Atenção", "Selecione um equipamento para remover.")
                return
                
            # Obter o ID do equipamento (armazenado no UserRole da coluna Tag)
            item = self.company_equipment_table.item(selected_row, 0)
            if not item:
                QMessageBox.warning(self, "Erro", "Falha ao obter o equipamento selecionado.")
                return
                
            equipment_id = item.data(Qt.UserRole)
            
            # Reutilizar o método existente
            self.delete_equipment(equipment_id)
            
            # Atualizar a tabela após a remoção
            company_id = self.company_selector.currentData()
            self.load_equipment_by_company(company_id)
            
        except Exception as e:
            logger.error(f"Erro ao remover equipamento da empresa: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao remover equipamento: {str(e)}")
            
    def load_companies_to_combobox(self):
        # Carrega as empresas no combobox de seleção
        try:
            self.company_selector.clear()
            
            # Adicionar item padrão
            self.company_selector.addItem("Selecione uma empresa", None)
            
            # Obter empresas
            companies = self.auth_controller.get_companies()
            
            # Adicionar cada empresa ao combobox
            for company in companies:
                self.company_selector.addItem(company['nome'], company['id'])
                
            logger.debug(f"Carregadas {len(companies)} empresas no combobox")
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no combobox: {str(e)}")
            logger.error(traceback.format_exc())

    
    def create_company_equipment_tab(self):
        """Cria e configura a aba 'Equipamentos por Empresa'"""
        try:
            # Criar widget da aba
            company_equipment_tab = QWidget()
            tab_layout = QVBoxLayout(company_equipment_tab)
            
            # Área superior - seleção de empresa
            top_container = QHBoxLayout()
            
            # Label para seleção de empresa
            company_label = QLabel("Selecione a Empresa:")
            company_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            top_container.addWidget(company_label)
            
            # ComboBox para seleção de empresa
            self.company_selector = QComboBox()
            self.company_selector.setMinimumWidth(250)
            self.company_selector.setMinimumHeight(36)
            self.company_selector.currentIndexChanged.connect(self.company_changed)
            
            # Carregar empresas no combobox
            self.load_companies_to_combobox()
            
            top_container.addWidget(self.company_selector)
            top_container.addStretch()
            
            # Botões de ação para equipamentos
            buttons_container = QHBoxLayout()
            
            # Botão Adicionar Equipamento
            self.add_company_equipment_button = self.create_crud_button("add", "Adicionar Equipamento para esta Empresa", self.add_equipment_to_company)
            buttons_container.addWidget(self.add_company_equipment_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Editar Equipamento
            self.edit_company_equipment_button = self.create_crud_button("edit", "Editar", self.edit_company_equipment)
            buttons_container.addWidget(self.edit_company_equipment_button)
            buttons_container.addSpacing(5)  # Espaçamento entre botões
            
            # Botão Remover Equipamento
            self.remove_company_equipment_button = self.create_crud_button("delete", "Remover", self.delete_company_equipment)
            buttons_container.addWidget(self.remove_company_equipment_button)
            
            buttons_container.addStretch()
            
            # Tabela de equipamentos da empresa
            self.company_equipment_table = QTableWidget()
            self.company_equipment_table.setColumnCount(9)  # Sem a coluna de Empresa
            self.company_equipment_table.setHorizontalHeaderLabels([
                "Tag", "Categoria", "Fabricante", "Ano Fabricação", 
                "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido", "Status"
            ])
            self.company_equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.company_equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.company_equipment_table.setSelectionMode(QTableWidget.SingleSelection)
            self.company_equipment_table.setAlternatingRowColors(True)
            self.company_equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.company_equipment_table.verticalHeader().setVisible(False)
            
            # Adicionar elementos ao layout da aba
            tab_layout.addLayout(top_container)
            tab_layout.addLayout(buttons_container)
            tab_layout.addWidget(self.company_equipment_table)
            
            return company_equipment_tab
            
        except Exception as e:
            logger.error(f"Erro ao criar aba 'Equipamentos por Empresa': {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao criar aba de equipamentos por empresa: {str(e)}")
            # Retorna um widget vazio em caso de erro
            return QWidget()
            
    def load_companies_to_equipment_combobox(self):
        """Carrega as empresas no combobox de filtro da aba Equipamentos"""
        try:
            logger.debug("Carregando empresas no combobox de equipamentos")
            self.equipment_company_selector.blockSignals(True)
            self.equipment_company_selector.clear()
            self.equipment_company_selector.addItem("Todas as empresas", None)
            
            # Obter empresas
            companies = self.auth_controller.get_companies()
            logger.debug(f"Obtidas {len(companies)} empresas")
            
            # Adicionar empresas ao combobox
            for company in companies:
                self.equipment_company_selector.addItem(company['nome'], company['id'])
                
            logger.debug("Empresas carregadas com sucesso no combobox de equipamentos")
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no combobox de equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.equipment_company_selector.blockSignals(False)
    
    def filter_equipment_by_company(self):
        """Filtra a tabela de equipamentos pela empresa selecionada no ComboBox"""
        try:
            company_id = self.equipment_company_selector.currentData()
            logger.debug(f"Filtrando equipamentos por empresa ID={company_id}")
            
            for row in range(self.equipment_table.rowCount()):
                item = self.equipment_table.item(row, 2)  # Coluna Empresa
                if company_id is None or (item and int(item.data(Qt.UserRole)) == company_id):
                    self.equipment_table.setRowHidden(row, False)
                else:
                    self.equipment_table.setRowHidden(row, True)
                    
            # Também aplicar o filtro de texto, se houver
            self.filter_equipment(self.equipment_search_box.text())
            logger.debug("Filtro por empresa aplicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos por empresa: {str(e)}")
            logger.error(traceback.format_exc())
    
    def filter_equipment(self, text):
        """Filtra os equipamentos na tabela com base no texto inserido e empresa selecionada"""
        try:
            search_text = text.lower()
            logger.debug(f"Filtrando equipamentos com texto: '{search_text}'")
            
            company_id = self.equipment_company_selector.currentData()
            logger.debug(f"Empresa selecionada ID={company_id}")
            
            for row in range(self.equipment_table.rowCount()):
                should_show = True
                
                # Filtro por empresa
                if company_id is not None:
                    item_empresa = self.equipment_table.item(row, 2)  # Coluna Empresa
                    if not item_empresa or int(item_empresa.data(Qt.UserRole)) != company_id:
                        should_show = False
                        
                # Filtro por texto
                if should_show and search_text:
                    found = False
                    for col in range(self.equipment_table.columnCount()):
                        item = self.equipment_table.item(row, col)
                        if item and search_text in item.text().lower():
                            found = True
                            break
                    should_show = found
                    
                self.equipment_table.setRowHidden(row, not should_show)
                
            logger.debug("Filtro de equipamentos aplicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
    
    def load_equipment(self):
        """Carrega todos os equipamentos na tabela, incluindo o ID da empresa como UserRole na coluna Empresa"""
        try:
            logger.debug("Carregando equipamentos")
            equipment = self.equipment_controller.get_all_equipment()
            self.equipment_table.setRowCount(len(equipment))
            
            # Obter todas as empresas para usar como mapeamento ID -> Nome
            empresas = self.auth_controller.get_companies()
            empresa_map = {empresa['id']: empresa['nome'] for empresa in empresas}
            
            # Data atual para cálculos de manutenção
            data_atual = datetime.now().date()
            
            for i, item in enumerate(equipment):
                # Armazena o ID como dados do item (invisível para o usuário)
                equip_id = item.get('id', '')
                logger.debug(f"Carregando equipamento ID={equip_id}, Tag={item.get('tag', '')}")
                
                # Tag
                tag_item = QTableWidgetItem(item.get('tag', ''))
                tag_item.setData(Qt.UserRole, equip_id)  # Armazena o ID como dado do item
                tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)  # Remove a flag de editável
                self.equipment_table.setItem(i, 0, tag_item)
                
                # Para debug - verifica se o ID foi armazenado corretamente
                id_stored = tag_item.data(Qt.UserRole)
                logger.debug(f"ID armazenado no item da tabela: {id_stored}")
                
                # Resto dos campos - todos configurados como não editáveis
                categoria_item = QTableWidgetItem(item.get('categoria', ''))
                categoria_item.setFlags(categoria_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 1, categoria_item)
                
                # Empresa - usando o nome em vez do ID
                empresa_id = item.get('empresa_id', '')
                empresa_nome = empresa_map.get(empresa_id, f"ID: {empresa_id}")
                empresa_item = QTableWidgetItem(empresa_nome)
                empresa_item.setData(Qt.UserRole, empresa_id)  # Armazena o ID como dado do item
                empresa_item.setFlags(empresa_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 2, empresa_item)
                
                fabricante_item = QTableWidgetItem(item.get('fabricante', ''))
                fabricante_item.setFlags(fabricante_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 3, fabricante_item)
                
                ano_item = QTableWidgetItem(str(item.get('ano_fabricacao', '')))
                ano_item.setFlags(ano_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 4, ano_item)
                
                pressao_projeto_item = QTableWidgetItem(str(item.get('pressao_projeto', '')))
                pressao_projeto_item.setFlags(pressao_projeto_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 5, pressao_projeto_item)
                
                
                pressao_trabalho_item = QTableWidgetItem(str(item.get('pressao_trabalho', '')))
                pressao_trabalho_item.setFlags(pressao_trabalho_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 6, pressao_trabalho_item)
                
                volume_item = QTableWidgetItem(str(item.get('volume', '')))
                volume_item.setFlags(volume_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 7, volume_item)
                
                fluido_item = QTableWidgetItem(item.get('fluido', ''))
                fluido_item.setFlags(fluido_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 8, fluido_item)
                
                # Status
                status = "Ativo" if item.get('ativo', 1) else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 9, status_item)
                
                # Novos campos NR-13
                categoria_nr13_item = QTableWidgetItem(item.get('categoria_nr13', ''))
                categoria_nr13_item.setFlags(categoria_nr13_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 10, categoria_nr13_item)
                
                pmta_item = QTableWidgetItem(str(item.get('pmta', '')))
                pmta_item.setFlags(pmta_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 11, pmta_item)
                
                placa_identificacao_item = QTableWidgetItem(item.get('placa_identificacao', ''))
                placa_identificacao_item.setFlags(placa_identificacao_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 12, placa_identificacao_item)
                
                numero_registro_item = QTableWidgetItem(item.get('numero_registro', ''))
                numero_registro_item.setFlags(numero_registro_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 13, numero_registro_item)
                
                # Campos de manutenção
                # Última manutenção
                data_ultima_manutencao = item.get('data_ultima_manutencao', '')
                data_ultima_str = ''
                data_ultima_obj = None
                
                if data_ultima_manutencao:
                    try:
                        if isinstance(data_ultima_manutencao, str):
                            # Tratamento robusto para strings de data
                            if len(data_ultima_manutencao) >= 10:
                                data_ultima_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d').date()
                                data_ultima_str = data_ultima_obj.strftime('%d/%m/%Y')
                            else:
                                data_ultima_str = data_ultima_manutencao
                                logger.warning(f"Formato de data inválido: {data_ultima_manutencao}")
                        elif isinstance(data_ultima_manutencao, datetime):
                            data_ultima_obj = data_ultima_manutencao.date()
                            data_ultima_str = data_ultima_obj.strftime('%d/%m/%Y')
                        else:
                            data_ultima_str = str(data_ultima_manutencao)
                            logger.warning(f"Tipo de data não reconhecido: {type(data_ultima_manutencao)}")
                    except Exception as e:
                        data_ultima_str = str(data_ultima_manutencao)
                        logger.warning(f"Erro ao processar data de manutenção: {str(e)}")
                
                ultima_manutencao_item = QTableWidgetItem(data_ultima_str)
                ultima_manutencao_item.setFlags(ultima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                self.equipment_table.setItem(i, 14, ultima_manutencao_item)
                
                # Próxima manutenção
                data_proxima_str = ''
                frequencia = item.get('frequencia_manutencao', 0)
                dias_restantes = None
                
                if data_ultima_manutencao and frequencia:
                    try:
                        # Se ainda não temos o objeto data_ultima_obj, tentar convertê-lo novamente
                        if data_ultima_obj is None and isinstance(data_ultima_manutencao, str):
                            try:
                                if len(data_ultima_manutencao) >= 10:
                                    data_ultima_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d').date()
                            except Exception:
                                logger.warning(f"Não foi possível converter a data: {data_ultima_manutencao}")
                        
                        if data_ultima_obj:
                            data_proxima = data_ultima_obj + timedelta(days=frequencia)
                            data_proxima_str = data_proxima.strftime('%d/%m/%Y')
                            
                            # Calcular dias restantes
                            dias_restantes = (data_proxima - data_atual).days
                            
                            # Aplicar indicadores visuais baseados na urgência da manutenção
                            proxima_manutencao_item = QTableWidgetItem(data_proxima_str)
                            proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                            self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                            
                            # Verifica se está atrasado ou próximo
                            if dias_restantes < 0 and item.get('ativo', 1):  # Atrasado e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 10, 10)  # Vermelho muito escuro para tema escuro
                                    cor_texto = QColor(255, 130, 130)  # Texto vermelho claro
                                else:
                                    cor_linha = QColor(255, 200, 200)  # Vermelho pastel
                                    cor_texto = QColor(139, 0, 0)  # Vermelho escuro para contraste
                                
                                # Adiciona indicador visual de manutenção atrasada
                                proxima_manutencao_item.setText("❗ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção ATRASADA")
                            elif dias_restantes <= 7 and item.get('ativo', 1):  # Próximo (1 semana) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 20, 20)  # Vermelho escuro para tema escuro
                                    cor_texto = QColor(255, 150, 150)  # Texto vermelho claro
                                else:
                                    cor_linha = QColor(255, 200, 200)  # Vermelho claro
                                    cor_texto = QColor(139, 0, 0)  # Texto escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("❗ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção URGENTE (≤ 7 dias)")
                            elif dias_restantes <= 15 and item.get('ativo', 1):  # Próximo (15 dias) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 60, 10)  # Laranja escuro para tema escuro
                                    cor_texto = QColor(255, 200, 120)  # Texto laranja claro
                                else:
                                    cor_linha = QColor(255, 230, 180)  # Laranja claro
                                    cor_texto = QColor(102, 51, 0)  # Marrom escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("⚠️ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção ALTA (≤ 15 dias)")
                            elif dias_restantes <= 30 and item.get('ativo', 1):  # Próximo (30 dias) e ativo
                                # Cores baseadas no tema atual
                                if self.is_dark:
                                    cor_linha = QColor(90, 90, 10)  # Amarelo escuro para tema escuro
                                    cor_texto = QColor(255, 255, 150)  # Texto amarelo claro
                                else:
                                    cor_linha = QColor(255, 255, 180)  # Amarelo claro
                                    cor_texto = QColor(102, 102, 0)  # Amarelo escuro para contraste
                                
                                # Adiciona indicador visual de manutenção próxima
                                proxima_manutencao_item.setText("⚠️ " + data_proxima_str)
                                
                                for col in range(self.equipment_table.columnCount()):
                                    cell = self.equipment_table.item(i, col)
                                    if cell:
                                        cell.setBackground(cor_linha)
                                        cell.setForeground(cor_texto)
                                logger.debug(f"Equipamento {item.get('tag')} com manutenção MÉDIA (≤ 30 dias)")
                        else:
                            proxima_manutencao_item = QTableWidgetItem("Não programada")
                            proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                            self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                    except Exception as e:
                        logger.error(f"Erro ao calcular próxima manutenção: {str(e)}")
                        data_proxima_str = "Erro no cálculo"
                        proxima_manutencao_item = QTableWidgetItem(data_proxima_str)
                        proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                        self.equipment_table.setItem(i, 15, proxima_manutencao_item)
                else:
                    proxima_manutencao_item = QTableWidgetItem("Não programada")
                    proxima_manutencao_item.setFlags(proxima_manutencao_item.flags() & ~Qt.ItemIsEditable)
                    self.equipment_table.setItem(i, 15, proxima_manutencao_item)
            
            # Forçar atualização imediata da tabela
            self.equipment_table.viewport().update()
            logger.debug(f"Carregados {len(equipment)} equipamentos na tabela")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")

    def register_maintenance(self):
        """Abre a janela modal para registrar manutenção de equipamento"""
        try:
            # Verificar se um equipamento está selecionado
            equipment_id = self.get_selected_equipment_id()
            if not equipment_id:
                QMessageBox.warning(self, "Aviso", "Selecione um equipamento para registrar a manutenção")
                return
                
            # Buscar dados do equipamento
            equipment_data = None
            all_equipment = self.equipment_controller.get_all_equipment()
            
            for equip in all_equipment:
                if equip.get('id') == equipment_id:
                    equipment_data = equip
                    break
                    
            if not equipment_data:
                QMessageBox.warning(self, "Erro", f"Não foi possível encontrar o equipamento com ID {equipment_id}")
                return
            
            # Abrir o modal de manutenção
            # Usa tema claro ou escuro conforme o estado atual
            is_dark = self.palette().color(self.backgroundRole()).lightness() < 128
            modal = MaintenanceModal(self, is_dark)
            
            # Preencher o campo de frequência com o valor atual do equipamento (se existir)
            if equipment_data and equipment_data.get('frequencia_manutencao'):
                modal.freq_input.setText(str(equipment_data.get('frequencia_manutencao')))
            
            if modal.exec_() == QDialog.Accepted:
                data = modal.get_data()
                success, message = self.equipment_controller.atualizar_manutencao_equipamento(
                    equipment_id=equipment_id,
                    data_ultima_manutencao=data['data_manutencao'],
                    frequencia_manutencao=data['frequencia']
                )
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Manutenção registrada com sucesso!")
                    self.load_equipment()  # Atualiza a tabela
                else:
                    QMessageBox.warning(self, "Erro", f"Não foi possível registrar a manutenção: {message}")
                    
        except Exception as e:
            logger.error(f"Erro ao registrar manutenção: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.warning(self, "Erro", f"Erro ao registrar manutenção: {str(e)}")
