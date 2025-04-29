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

    def get_tab_icon(self, icon_name):
        """Retorna o ícone apropriado para a aba"""
        try:
            logger.debug(f"Obtendo ícone: {icon_name}")
            # Tenta carregar o ícone do arquivo
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
            self.setWindowTitle('Sistema de Inspeções NR-13 - Administrador')
            self.setMinimumSize(800, 600)
            
            # Widget central
            logger.debug("Criando widget central")
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
            logger.debug("Criando abas")
            self.tabs = QTabWidget()
            
            # Aba de Usuários
            logger.debug("Configurando aba de usuários")
            user_tab = QWidget()
            user_layout = QVBoxLayout(user_tab)
            
            # Botões de ação para usuários
            user_buttons = QHBoxLayout()
            self.add_user_button = QPushButton("Adicionar Usuário")
            self.add_user_button.setMinimumHeight(36)
            self.add_user_button.clicked.connect(self.add_user)
            user_buttons.addWidget(self.add_user_button)
            
            # Menu de debug
            self.debug_button = QPushButton("Debug")
            self.debug_menu = QMenu(self)
            
            # Opções de popular dados
            self.debug_menu.addSection("Popular Dados")
            self.action_popular_usuarios = self.debug_menu.addAction("Popular Usuários")
            self.action_popular_usuarios.triggered.connect(self.inserir_usuarios_debug)
            self.action_popular_equipamentos = self.debug_menu.addAction("Popular Equipamentos")
            self.action_popular_equipamentos.triggered.connect(self.inserir_equipamentos_debug)
            self.action_popular_inspecoes = self.debug_menu.addAction("Popular Inspeções")
            self.action_popular_inspecoes.triggered.connect(self.inserir_inspecoes_debug)
            self.action_popular_relatorios = self.debug_menu.addAction("Popular Relatórios")
            self.action_popular_relatorios.triggered.connect(self.inserir_relatorios_debug)
            
            # Opções de limpar dados
            self.debug_menu.addSection("Limpar Dados (preserva admins)")
            self.action_limpar_usuarios = self.debug_menu.addAction("Limpar Usuários")
            self.action_limpar_usuarios.triggered.connect(lambda: self.limpar_dados_debug("usuarios"))
            self.action_limpar_equipamentos = self.debug_menu.addAction("Limpar Equipamentos")
            self.action_limpar_equipamentos.triggered.connect(lambda: self.limpar_dados_debug("equipamentos"))
            self.action_limpar_inspecoes = self.debug_menu.addAction("Limpar Inspeções")
            self.action_limpar_inspecoes.triggered.connect(lambda: self.limpar_dados_debug("inspecoes"))
            self.action_limpar_relatorios = self.debug_menu.addAction("Limpar Relatórios")
            self.action_limpar_relatorios.triggered.connect(lambda: self.limpar_dados_debug("relatorios"))
            self.action_limpar_tudo = self.debug_menu.addAction("Limpar Tudo")
            self.action_limpar_tudo.triggered.connect(lambda: self.limpar_dados_debug("tudo"))
            
            self.debug_button.setMenu(self.debug_menu)
            user_buttons.addWidget(self.debug_button)
            user_layout.addLayout(user_buttons)
            
            # Tabela de usuários
            self.user_table = QTableWidget()
            self.user_table.setColumnCount(5)
            self.user_table.setHorizontalHeaderLabels([
                "ID", "Nome", "Email", "Tipo", "Empresa"
            ])
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            logger.debug("Carregando inspeções")
            self.load_inspections()
            inspection_layout.addWidget(self.inspection_table)
            
            # Aba de Relatórios
            logger.debug("Configurando aba de relatórios")
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
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels([
                "ID", "Equipamento", "Data", "Tipo Inspeção", "Resultado", "Arquivo"
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            logger.debug("Carregando relatórios")
            self.load_reports()
            report_layout.addWidget(self.report_table)
            
            # Adiciona as abas com ícones
            logger.debug("Adicionando abas ao TabWidget")
            self.tabs.addTab(user_tab, self.get_tab_icon("user.png"), "Usuários")
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
            else:
                self.setStyleSheet(Styles.get_light_theme())
            # Atualiza os ícones das abas ao trocar o tema
            self.tabs.setTabIcon(0, self.get_tab_icon("user.png"))
            self.tabs.setTabIcon(1, self.get_tab_icon("equipamentos.png"))
            self.tabs.setTabIcon(2, self.get_tab_icon("inspecoes.png"))
            self.tabs.setTabIcon(3, self.get_tab_icon("relatorios.png"))
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
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
                self.user_table.setItem(i, 1, QTableWidgetItem(user['nome']))
                self.user_table.setItem(i, 2, QTableWidgetItem(user['email']))
                self.user_table.setItem(i, 3, QTableWidgetItem(user['tipo_acesso']))
                self.user_table.setItem(i, 4, QTableWidgetItem(user['empresa'] or ""))
                
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
        """Abre a janela modal para adicionar equipamento"""
        modal = EquipmentModal(self, self.is_dark)
        if modal.exec_() == QDialog.Accepted:
            data = modal.get_data()
            success, message = self.equipment_controller.criar_equipamento(
                tag=data['tipo'],
                categoria=data['tipo'],
                empresa_id=self.get_empresa_id_by_name(data['empresa']),
                fabricante=data['localizacao'],
                ano_fabricacao=2023,
                pressao_projeto=float(data['pressao'] or 0),
                pressao_trabalho=float(data['pressao'] or 0) * 0.8,
                volume=100.0,
                fluido=data['codigo']
            )
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_equipment()
            else:
                QMessageBox.warning(self, "Erro", message)
                
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
        """Adiciona uma nova inspeção"""
        try:
            modal = InspectionModal(self, self.is_dark)
            
            # Carrega os equipamentos disponíveis
            equipment = self.equipment_controller.get_all_equipment()
            for equip in equipment:
                modal.equipamento_input.addItem(f"{equip['id']} - {equip.get('tag', '')} ({equip.get('empresa_id', '')})")
                
            # Carrega os engenheiros disponíveis
            engineers = self.auth_controller.get_all_engineers()
            for eng in engineers:
                modal.engenheiro_input.addItem(eng['nome'], eng['id'])
                
            if modal.exec_() == QDialog.Accepted:
                data = modal.get_data()
                success, message = self.inspection_controller.criar_inspecao(
                    equipamento_id=data['equipamento_id'],
                    engenheiro_id=data['engenheiro'],
                    data_inspecao=data['data'],
                    tipo_inspecao=data['tipo'],
                    resultado=data['resultado'],
                    recomendacoes=data['recomendacoes']
                )
                
                if success:
                    self.load_inspections()
                    QMessageBox.information(self, "Sucesso", message)
                else:
                    QMessageBox.warning(self, "Erro", message)
                    
        except Exception as e:
            logger.error(f"Erro ao criar inspeção: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao criar inspeção: {str(e)}")
            
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
        """Carrega as inspeções na tabela"""
        try:
            logger.debug("Carregando inspeções")
            inspections = self.inspection_controller.get_all_inspections()
            self.inspection_table.setRowCount(len(inspections))
            
            for i, item in enumerate(inspections):
                self.inspection_table.setItem(i, 0, QTableWidgetItem(str(item['id'])))
                self.inspection_table.setItem(i, 1, QTableWidgetItem(item.get('equipamento_tag', '')))
                
                # Trata a data verificando seu tipo
                data = item.get('data', '')
                data_str = ""
                if data:
                    if isinstance(data, str):
                        # Tenta converter a string para datetime para formatação
                        try:
                            data_obj = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                            data_str = data_obj.strftime("%d/%m/%Y")
                        except (ValueError, TypeError):
                            # Se não conseguir converter no formato padrão, tenta outros formatos comuns
                            try:
                                data_obj = datetime.strptime(data, "%Y-%m-%d")
                                data_str = data_obj.strftime("%d/%m/%Y")
                            except (ValueError, TypeError):
                                data_str = data  # Mantém a string original se não conseguir converter
                    elif isinstance(data, datetime):
                        # Se for um objeto datetime, formata diretamente
                        data_str = data.strftime("%d/%m/%Y")
                    else:
                        data_str = str(data)  # Para qualquer outro tipo, converte para string
                
                self.inspection_table.setItem(i, 2, QTableWidgetItem(data_str))
                self.inspection_table.setItem(i, 3, QTableWidgetItem(item.get('tipo', '')))
                self.inspection_table.setItem(i, 4, QTableWidgetItem(item.get('engenheiro_nome', '')))
                self.inspection_table.setItem(i, 5, QTableWidgetItem(item.get('resultado', '')))
                
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
            
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        try:
            logger.debug("Carregando relatórios")
            reports = self.report_controller.get_all_reports()
            self.report_table.setRowCount(len(reports))
            
            for i, item in enumerate(reports):
                self.report_table.setItem(i, 0, QTableWidgetItem(str(item['id'])))
                self.report_table.setItem(i, 1, QTableWidgetItem(item.get('equipamento_tag', '')))
                
                # Trata a data verificando seu tipo
                data = item.get('data', '')
                data_str = ""
                if data:
                    if isinstance(data, str):
                        # Tenta converter a string para datetime para formatação
                        try:
                            data_obj = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                            data_str = data_obj.strftime("%d/%m/%Y")
                        except (ValueError, TypeError):
                            # Se não conseguir converter no formato padrão, tenta outros formatos comuns
                            try:
                                data_obj = datetime.strptime(data, "%Y-%m-%d")
                                data_str = data_obj.strftime("%d/%m/%Y")
                            except (ValueError, TypeError):
                                data_str = data  # Mantém a string original se não conseguir converter
                    elif isinstance(data, datetime):
                        # Se for um objeto datetime, formata diretamente
                        data_str = data.strftime("%d/%m/%Y")
                    else:
                        data_str = str(data)  # Para qualquer outro tipo, converte para string
                
                self.report_table.setItem(i, 2, QTableWidgetItem(data_str))
                self.report_table.setItem(i, 3, QTableWidgetItem(item.get('tipo_inspecao', '')))
                self.report_table.setItem(i, 4, QTableWidgetItem(item.get('inspecao_resultado', '')))
                self.report_table.setItem(i, 5, QTableWidgetItem(item.get('arquivo', '')))
                
        except Exception as e:
            logger.error(f"Erro ao carregar relatórios: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar relatórios: {str(e)}")

    def inserir_usuarios_debug(self):
        """Adiciona usuários de exemplo ao banco de dados"""
        try:
            logger.info("Populando usuários de debug...")
            # Usuários fictícios
            self.auth_controller.criar_usuario(
                nome="Engenheiro Teste", email="eng@teste.com", senha="123456", 
                tipo_acesso="engenheiro", empresa="Empresa Teste"
            )
            self.auth_controller.criar_usuario(
                nome="Cliente Teste", email="cliente@teste.com", senha="123456", 
                tipo_acesso="cliente", empresa="Empresa Teste"
            )
            self.auth_controller.criar_usuario(
                nome="Outro Admin", email="admin2@teste.com", senha="123456", 
                tipo_acesso="admin"
            )
            self.auth_controller.criar_usuario(
                nome="Engenheiro Beta", email="eng2@teste.com", senha="123456", 
                tipo_acesso="engenheiro", empresa="Empresa Beta"
            )
            self.auth_controller.criar_usuario(
                nome="Cliente Beta", email="cliente2@teste.com", senha="123456", 
                tipo_acesso="cliente", empresa="Empresa Beta"
            )
            QMessageBox.information(self, "Debug", "Usuários de exemplo adicionados com sucesso!")
            self.load_users()
        except Exception as e:
            logger.error(f"Erro ao inserir usuários de debug: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inserir usuários de debug: {str(e)}")
            
    def inserir_equipamentos_debug(self):
        """Adiciona equipamentos de exemplo ao banco de dados"""
        try:
            logger.info("Populando equipamentos de debug...")
            # Equipamentos fictícios
            self.equipment_controller.criar_equipamento(
                tag="TAG-001", categoria="Vaso de Pressão", empresa_id=1, 
                fabricante="FabricaX", ano_fabricacao=2020,
                pressao_projeto=10.0, pressao_trabalho=8.0, 
                volume=100.0, fluido="Água"
            )
            self.equipment_controller.criar_equipamento(
                tag="TAG-002", categoria="Caldeira", empresa_id=1, 
                fabricante="FabricaY", ano_fabricacao=2019,
                pressao_projeto=15.0, pressao_trabalho=12.0, 
                volume=200.0, fluido="Vapor"
            )
            self.equipment_controller.criar_equipamento(
                tag="TAG-003", categoria="Tubulação", empresa_id=2, 
                fabricante="FabricaZ", ano_fabricacao=2021,
                pressao_projeto=8.0, pressao_trabalho=6.0, 
                volume=50.0, fluido="Óleo"
            )
            QMessageBox.information(self, "Debug", "Equipamentos de exemplo adicionados com sucesso!")
            self.load_equipment()
        except Exception as e:
            logger.error(f"Erro ao inserir equipamentos de debug: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inserir equipamentos de debug: {str(e)}")
            
    def inserir_inspecoes_debug(self):
        """Adiciona inspeções de exemplo ao banco de dados"""
        try:
            logger.info("Populando inspeções de debug...")
            # Inspeções fictícias
            from datetime import datetime, timedelta
            data_atual = datetime.now().strftime("%Y-%m-%d 00:00:00")
            data_anterior = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
            data_futura = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
            
            self.inspection_controller.criar_inspecao(
                equipamento_id=1, engenheiro_id=1, 
                data_inspecao=data_anterior, tipo_inspecao="Visual"
            )
            self.inspection_controller.criar_inspecao(
                equipamento_id=2, engenheiro_id=1, 
                data_inspecao=data_atual, tipo_inspecao="Completa"
            )
            self.inspection_controller.criar_inspecao(
                equipamento_id=3, engenheiro_id=4, 
                data_inspecao=data_futura, tipo_inspecao="Periódica"
            )
            QMessageBox.information(self, "Debug", "Inspeções de exemplo adicionadas com sucesso!")
            self.load_inspections()
        except Exception as e:
            logger.error(f"Erro ao inserir inspeções de debug: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inserir inspeções de debug: {str(e)}")
            
    def inserir_relatorios_debug(self):
        """Adiciona relatórios de exemplo ao banco de dados"""
        try:
            logger.info("Populando relatórios de debug...")
            
            # Verifica se existem inspeções
            inspections = self.inspection_controller.get_all_inspections()
            if not inspections:
                QMessageBox.warning(
                    self, 
                    "Atenção", 
                    "Não há inspeções cadastradas. Adicione inspeções primeiro usando a opção 'Popular Inspeções'."
                )
                return
                
            # Seleciona a primeira inspeção disponível
            inspecao_id = inspections[0]['id']
            logger.info(f"Usando inspeção ID: {inspecao_id}")
            
            # Relatórios fictícios
            from datetime import datetime, timedelta
            data_atual = datetime.now().strftime("%Y-%m-%d 00:00:00")
            
            sucesso, mensagem = self.report_controller.criar_relatorio(
                inspecao_id=inspecao_id,
                data_emissao=data_atual,
                link_arquivo="/relatorios/inspecao_exemplo.pdf",
                observacoes="Relatório de teste criado automaticamente"
            )
            
            if sucesso:
                logger.info("Relatório de exemplo criado com sucesso")
                QMessageBox.information(self, "Debug", "Relatório de exemplo adicionado com sucesso!")
                self.load_reports()
            else:
                logger.error(f"Erro ao criar relatório: {mensagem}")
                QMessageBox.warning(self, "Erro", f"Erro ao criar relatório: {mensagem}")
            
        except Exception as e:
            logger.error(f"Erro ao inserir relatórios de debug: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inserir relatórios de debug: {str(e)}")
            
    def limpar_dados_debug(self, tipo: str):
        """Limpa dados do banco de dados, preservando usuários admin
        
        Args:
            tipo (str): Tipo de dados a limpar - "usuarios", "equipamentos", "inspecoes", "relatorios" ou "tudo"
        """
        try:
            conn = self.db_models.db.get_connection()
            cursor = conn.cursor()
            
            # Pede confirmação
            msg = f"ATENÇÃO: Isso irá remover todos os dados de {tipo}. Deseja continuar?"
            if tipo == "tudo":
                msg = "ATENÇÃO: Isso irá remover TODOS OS DADOS (exceto admins). Deseja continuar?"
                
            confirm = QMessageBox.question(
                self, "Confirmação", msg, 
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
                
            logger.info(f"Limpando dados de {tipo}...")
            
            # Limpa os dados específicos, respeitando a ordem das chaves estrangeiras
            if tipo == "equipamentos" or tipo == "tudo":
                # Primeiro remove os relatórios
                cursor.execute("DELETE FROM relatorios")
                logger.info("Relatórios removidos")
                
                # Depois remove as inspeções
                cursor.execute("DELETE FROM inspecoes")
                logger.info("Inspeções removidas")
                
                # Por último remove os equipamentos
                cursor.execute("DELETE FROM equipamentos")
                logger.info("Equipamentos removidos")
                
            elif tipo == "inspecoes" or tipo == "tudo":
                # Primeiro remove os relatórios
                cursor.execute("DELETE FROM relatorios")
                logger.info("Relatórios removidos")
                
                # Depois remove as inspeções
                cursor.execute("DELETE FROM inspecoes")
                logger.info("Inspeções removidas")
                
            elif tipo == "relatorios" or tipo == "tudo":
                cursor.execute("DELETE FROM relatorios")
                logger.info("Relatórios removidos")
                
            elif tipo == "usuarios" or tipo == "tudo":
                # Preserva usuários admin
                cursor.execute("DELETE FROM usuarios WHERE tipo_acesso != 'admin'")
                logger.info("Usuários não-admin removidos")
                
            conn.commit()
            
            # Recarga as tabelas
            self.load_users()
            self.load_equipment()
            self.load_inspections()
            self.load_reports()
            
            QMessageBox.information(self, "Debug", f"Dados de {tipo} limpos com sucesso!")
                
        except Exception as e:
            logger.error(f"Erro ao limpar dados de {tipo}: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao limpar dados: {str(e)}")
            
        finally:
            cursor.close() 