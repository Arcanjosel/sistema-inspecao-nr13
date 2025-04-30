from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction, QMessageBox
from PyQt5.QtGui import QIcon

from ui.login_ui import LoginWindow
from ui.equipment_ui import EquipmentTab
from ui.engineer_ui import EngineerTab
from ui.admin_ui import AdminTab
from ui.inspection_ui import InspectionTab
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, db_models, user_data, is_dark=False):
        super().__init__()
        self.db_models = db_models
        self.user_data = user_data
        self.is_dark = is_dark
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a UI da janela principal"""
        self.setWindowTitle("Sistema de Inspeções NR-13")
        self.setMinimumSize(800, 600)
        
        # Definir ícone da janela com o logo da empresa
        self.setWindowIcon(QIcon("ui/CTREINA_LOGO.png"))
        
        # Criar o widget de abas
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Adicionar abas
        self.add_tabs()
        
        # Configurar o menu
        self.setup_menu()
        
        # Mostrar a janela
        self.show()
        
    def add_tabs(self):
        """Adiciona as abas ao widget de abas"""
        # Aba de Equipamentos
        self.equipment_tab = EquipmentTab(self.db_models, self.is_dark)
        self.tab_widget.addTab(self.equipment_tab, "Equipamentos")
        
        # Aba de Engenheiros
        self.engineer_tab = EngineerTab(self.db_models, self.is_dark)
        self.tab_widget.addTab(self.engineer_tab, "Engenheiros")
        
        # Aba de Inspeções
        self.inspection_tab = InspectionTab(self.db_models, self.is_dark)
        self.tab_widget.addTab(self.inspection_tab, "Inspeções")
        
        # Aba de Administração (apenas para administradores)
        if self.user_data['tipo'] == 'adm':
            self.admin_tab = AdminTab(self.db_models, self.is_dark)
            self.tab_widget.addTab(self.admin_tab, "Administração")
            logger.info(f"Usuário {self.user_data['email']} tem acesso à aba de administração")
        
    def setup_menu(self):
        """Configura o menu da aplicação"""
        # Menu Arquivo
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Arquivo")
        
        # Ação Sair
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        
        # Ação Sobre
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_about(self):
        """Exibe a caixa de diálogo 'Sobre'"""
        QMessageBox.about(
            self, 
            "Sobre", 
            "Sistema de Inspeção NR-13\n\nVersão 1.0\n\nDesenvolvido para gerenciar inspeções de equipamentos de acordo com a norma NR-13."
        )
        
    def close_event(self, event):
        """Manipula o evento de fechamento da janela"""
        reply = QMessageBox.question(
            self, 
            "Confirmação", 
            "Tem certeza que deseja sair?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 