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
from PyQt5.QtCore import Qt, QDate, QSize, QTimer, pyqtSignal
from datetime import datetime, timedelta
import logging
from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from ui.styles import Styles
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from ui.modals import InspectionModal, ReportModal, MaintenanceModal
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController
from controllers.equipment_controller import EquipmentController
import traceback
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

class ClientWindow(QMainWindow):
    """
    Janela principal do cliente.
    """
    
    logout_requested = pyqtSignal()
    
    def __init__(self, auth_controller: AuthController, user_id: int, company: str):
        try:
            logger.debug("Iniciando construtor do ClientWindow")
            super().__init__()
            self.auth_controller = auth_controller
            self.db_models = DatabaseModels()
            self.user_id = user_id
            self.company = company
            self.equipment_controller = EquipmentController(self.db_models)
            self.inspection_controller = InspectionController(self.db_models)
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
                </svg>'''
            }
            
            logger.debug("Iniciando setup da UI")
            self.initUI()
            logger.debug("Aplicando tema")
            self.apply_theme()
            
            logger.debug("Carregando dados iniciais")
            # Carrega os dados iniciais antes de iniciar o timer
            self.load_equipment()
            self.load_inspections()
            self.load_reports()
            
            # Configurar o timer para atualização das tabelas a cada 5 segundos
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_all_tables)
            self.refresh_timer.start(5000)  # 5000ms = 5 segundos
            
            logger.info("ClientWindow inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar ClientWindow: {str(e)}")
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
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle("Sistema de Inspeções NR-13 - Cliente")
        self.setMinimumSize(900, 600)
        
        # Definir ícone da janela com o logo da empresa
        self.setWindowIcon(QIcon("ui/CTREINA_LOGO.png"))
        
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
        
        # Aba de Equipamentos
        equipment_tab = QWidget()
        equipment_layout = QVBoxLayout(equipment_tab)
        
        # Container para botões e barra de pesquisa
        equipment_top_container = QHBoxLayout()
        
        # Container para botões (lado esquerdo)
        buttons_container = QHBoxLayout()
        
        # Botão Registrar Manutenção
        self.register_maintenance_btn = QPushButton("Registrar Manutenção")
        self.register_maintenance_btn.setIcon(self.create_icon_from_svg(self.icons['add']))
        self.register_maintenance_btn.setMinimumHeight(36)
        self.register_maintenance_btn.clicked.connect(self.register_maintenance)
        buttons_container.addWidget(self.register_maintenance_btn)
        
        # Adiciona os botões ao container principal
        equipment_top_container.addLayout(buttons_container)
        
        # Adiciona um espaçador expansível
        equipment_top_container.addStretch()
        
        # Barra de pesquisa
        search_box = QHBoxLayout()
        self.equipment_search_input = QLineEdit()
        self.equipment_search_input.setPlaceholderText("Pesquisar equipamentos...")
        self.equipment_search_input.setMinimumWidth(200)
        self.equipment_search_input.setMaximumWidth(300)
        self.equipment_search_input.setMinimumHeight(32)
        self.equipment_search_input.textChanged.connect(self.filter_equipment)
        self.equipment_search_input.setStyleSheet("""
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
        
        search_box.addWidget(self.equipment_search_input)
        equipment_top_container.addLayout(search_box)
        
        equipment_layout.addLayout(equipment_top_container)
        
        # Tabela de equipamentos
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(10)
        self.equipment_table.setHorizontalHeaderLabels([
            "Tag", "Categoria", "Fabricante", "Ano Fabricação", 
            "Pressão Projeto", "Pressão Trabalho", "Volume", "Fluido",
            "Última Manutenção", "Próxima Manutenção"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setSelectionMode(QTableWidget.SingleSelection)
        self.equipment_table.setAlternatingRowColors(True)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.equipment_table.verticalHeader().setVisible(False)  # Desativa os numeradores de linha
        
        # Estilo personalizado para a tabela
        self.equipment_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #444;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: 1px solid #34495e;
            }
            QTableWidget::item:alternate {
                background-color: #283747;
            }
        """)
        
        # Carrega os equipamentos
        self.load_equipment()
        equipment_layout.addWidget(self.equipment_table)
        
        # Adiciona a aba de equipamentos
        self.tabs.addTab(equipment_tab, "Equipamentos")
        
        # Aba de Inspeções
        inspection_tab = QWidget()
        inspection_layout = QVBoxLayout(inspection_tab)
        
        # Container para botões e barra de pesquisa
        top_container = QHBoxLayout()
        
        # Container para botões (lado esquerdo)
        buttons_container = QHBoxLayout()
        
        # Botão Adicionar Inspeção
        self.add_inspection_btn = QPushButton("Adicionar Inspeção")
        self.add_inspection_btn.setIcon(self.create_icon_from_svg(self.icons['add']))
        self.add_inspection_btn.setMinimumHeight(36)
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
        self.inspection_table.setColumnCount(5)
        self.inspection_table.setHorizontalHeaderLabels([
            "Equipamento", "Data", "Tipo", "Engenheiro", "Resultado"
        ])
        self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inspection_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inspection_table.setSelectionMode(QTableWidget.SingleSelection)
        self.inspection_table.setAlternatingRowColors(True)
        self.inspection_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inspection_table.verticalHeader().setVisible(False)
        
        # Adiciona a tabela ao layout
        inspection_layout.addWidget(self.inspection_table)
        
        # Adiciona o tab de inspeções
        self.tabs.addTab(inspection_tab, "Inspeções")
        
        # Aba Relatórios
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)
        
        # Container para botões e barra de pesquisa
        report_top_container = QHBoxLayout()
        
        # Container para botões (lado esquerdo)
        report_buttons_container = QHBoxLayout()
        
        # Botão Adicionar Relatório
        self.add_report_btn = QPushButton("Adicionar Relatório")
        self.add_report_btn.setIcon(self.create_icon_from_svg(self.icons['add']))
        self.add_report_btn.setMinimumHeight(36)
        self.add_report_btn.clicked.connect(self.add_report)
        report_buttons_container.addWidget(self.add_report_btn)
        
        # Botão Ver Relatório
        self.view_report_btn = QPushButton("Ver Relatório")
        self.view_report_btn.setMinimumHeight(36)
        self.view_report_btn.clicked.connect(self.view_report)
        report_buttons_container.addWidget(self.view_report_btn)
        
        # Adiciona os botões ao container principal
        report_top_container.addLayout(report_buttons_container)
        
        # Adiciona um espaçador expansível
        report_top_container.addStretch()
        
        # Barra de pesquisa para relatórios
        report_search_container = QHBoxLayout()
        self.report_search_input = QLineEdit()
        self.report_search_input.setPlaceholderText("Pesquisar relatórios...")
        self.report_search_input.setMinimumWidth(200)
        self.report_search_input.setMaximumWidth(300)
        self.report_search_input.setMinimumHeight(32)
        self.report_search_input.textChanged.connect(self.filter_reports)
        
        # Estilo da barra de pesquisa
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
        
        report_search_container.addWidget(self.report_search_input)
        report_top_container.addLayout(report_search_container)
        
        # Adiciona o container principal ao layout da aba
        report_layout.addLayout(report_top_container)
        
        # Lista de relatórios
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "Inspeção", "Data", "Arquivo", "Observações", "Status"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.report_table.setSelectionMode(QTableWidget.SingleSelection)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.report_table.verticalHeader().setVisible(False)
        
        report_layout.addWidget(self.report_table)
        
        self.tabs.addTab(report_tab, "Relatórios")
        
        # Adiciona as abas ao layout principal
        layout.addWidget(self.tabs, 1)  # Stretch factor 1
        
        # Barra de rodapé
        footer = QWidget()
        footer.setMaximumHeight(50)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Adiciona botão de tema na barra inferior
        self.toggle_theme_btn = QPushButton()
        self.toggle_theme_btn.setIcon(self.create_icon_from_svg(self.icons['theme']))
        self.toggle_theme_btn.setIconSize(QSize(24, 24))
        self.toggle_theme_btn.setFlat(True)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        self.toggle_theme_btn.setToolTip("Alternar entre tema claro e escuro")
        footer_layout.addWidget(self.toggle_theme_btn, 0, Qt.AlignLeft)
        
        # Espaçador que ocupa a maior parte do espaço
        footer_layout.addStretch(1)
        
        # Botão de logout no canto direito
        logout_btn = QPushButton("Sair")
        logout_btn.setIcon(self.create_icon_from_svg(self.icons['logout']))
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMinimumHeight(36)
        footer_layout.addWidget(logout_btn, 0, Qt.AlignRight)
        
        layout.addWidget(footer)
        
    def apply_theme(self):
        """Aplica o tema escuro ou claro"""
        # Implementação do tema
        pass
            
    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.apply_theme()
        
    def logout(self):
        """Função para logout"""
        reply = QMessageBox.question(
            self, 'Confirmar Logout', 
            "Tem certeza que deseja sair?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Encerra o timer
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
            
            # Emite o sinal para a aplicação principal
            self.logout_requested.emit()
    
    def get_company_id(self):
        """Obtém o ID da empresa do usuário"""
        try:
            logger.debug(f"Obtendo ID da empresa para o usuário com ID={self.user_id}, empresa={self.company}")
            # Retorna diretamente o user_id no caso de usuário do tipo "cliente"
            # pois no caso de empresas, o ID do usuário é o ID da empresa
            return self.user_id
        except Exception as e:
            logger.error(f"Erro ao obter ID da empresa: {str(e)}")
            logger.error(traceback.format_exc())
            return None
        
    def load_equipment(self):
        """Carrega os equipamentos do cliente na tabela"""
        try:
            # Obtém o ID da empresa/cliente
            company_id = self.get_company_id()
            if company_id is None:
                logger.error(f"Não foi possível obter o ID da empresa '{self.company}'")
                return
                
            # Busca equipamentos pela empresa
            equipment_list = self.equipment_controller.get_equipment_by_company(company_id)
            logger.debug(f"Carregando {len(equipment_list)} equipamentos para exibição")
            
            self.equipment_table.setRowCount(len(equipment_list))
            
            for i, equip in enumerate(equipment_list):
                # Criar itens da tabela
                # Tag
                tag_item = QTableWidgetItem(equip.get('tag', ''))
                self.equipment_table.setItem(i, 0, tag_item)
                
                # Categoria
                self.equipment_table.setItem(i, 1, QTableWidgetItem(equip.get('categoria', '')))
                
                # Fabricante
                self.equipment_table.setItem(i, 2, QTableWidgetItem(equip.get('fabricante', '')))
                
                # Ano Fabricação
                self.equipment_table.setItem(i, 3, QTableWidgetItem(str(equip.get('ano_fabricacao', ''))))
                
                # Pressão Projeto
                self.equipment_table.setItem(i, 4, QTableWidgetItem(str(equip.get('pressao_projeto', ''))))
                
                # Pressão Trabalho
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(equip.get('pressao_trabalho', ''))))
                
                # Volume
                self.equipment_table.setItem(i, 6, QTableWidgetItem(str(equip.get('volume', ''))))
                
                # Fluido
                self.equipment_table.setItem(i, 7, QTableWidgetItem(equip.get('fluido', '')))
                
                # Última Manutenção
                data_ultima_manutencao = equip.get('data_ultima_manutencao')
                if data_ultima_manutencao:
                    # Verificar se data_ultima_manutencao é um objeto datetime ou uma string
                    if isinstance(data_ultima_manutencao, datetime):
                        data_formatada = data_ultima_manutencao.strftime('%d/%m/%Y')
                    else:
                        # Se for string, tentar converter para datetime ou usar diretamente
                        try:
                            if isinstance(data_ultima_manutencao, str) and data_ultima_manutencao:
                                # Tentar converter para datetime se for YYYY-MM-DD
                                if len(data_ultima_manutencao) >= 10:
                                    data_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d')
                                    data_formatada = data_obj.strftime('%d/%m/%Y')
                                else:
                                    data_formatada = data_ultima_manutencao
                            else:
                                data_formatada = str(data_ultima_manutencao)
                        except Exception as e:
                            logger.warning(f"Erro ao formatar data {data_ultima_manutencao}: {str(e)}")
                            data_formatada = str(data_ultima_manutencao)
                    
                    self.equipment_table.setItem(i, 8, QTableWidgetItem(data_formatada))
                else:
                    self.equipment_table.setItem(i, 8, QTableWidgetItem("Não registrada"))
                
                # Calcular e exibir próxima manutenção
                dias_ate_manutencao = equip.get('dias_ate_manutencao')
                proxima_item = None
                cor_linha = None
                cor_texto = None
                
                if dias_ate_manutencao is not None:
                    # Define cores para vermelho se atrasado
                    if dias_ate_manutencao <= 0:
                        proxima_item = QTableWidgetItem("ATRASADA")
                        # Cores mais suaves - vermelho pastel
                        cor_linha = QColor(255, 200, 200)
                        cor_texto = QColor(139, 0, 0)  # Vermelho escuro para contraste
                        logger.debug(f"Equipamento {equip.get('tag')} com manutenção ATRASADA")
                    # Define cores para amarelo se menos de 30 dias
                    elif dias_ate_manutencao <= 30:
                        # Calcular data próxima manutenção
                        if isinstance(data_ultima_manutencao, datetime):
                            data_proxima = (data_ultima_manutencao + timedelta(days=equip.get('frequencia_manutencao', 180))).strftime('%d/%m/%Y')
                        else:
                            try:
                                if isinstance(data_ultima_manutencao, str) and data_ultima_manutencao:
                                    # Tentar converter para datetime se for YYYY-MM-DD
                                    if len(data_ultima_manutencao) >= 10:
                                        data_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d')
                                        data_proxima = (data_obj + timedelta(days=equip.get('frequencia_manutencao', 180))).strftime('%d/%m/%Y')
                                    else:
                                        data_proxima = "Erro no formato de data"
                                else:
                                    data_proxima = "Data inválida"
                            except Exception as e:
                                logger.warning(f"Erro ao calcular próxima data para {data_ultima_manutencao}: {str(e)}")
                                data_proxima = "Erro no cálculo"
                        
                        proxima_item = QTableWidgetItem(f"{data_proxima}")
                        # Cores mais suaves - amarelo pastel
                        cor_linha = QColor(255, 248, 209)
                        cor_texto = QColor(138, 109, 0)  # Âmbar escuro para contraste
                        logger.debug(f"Equipamento {equip.get('tag')} com manutenção PRÓXIMA ({dias_ate_manutencao} dias)")
                    # Normal para os demais casos
                    else:
                        # Calcular data próxima manutenção
                        if isinstance(data_ultima_manutencao, datetime):
                            data_proxima = (data_ultima_manutencao + timedelta(days=equip.get('frequencia_manutencao', 180))).strftime('%d/%m/%Y')
                        else:
                            try:
                                if isinstance(data_ultima_manutencao, str) and data_ultima_manutencao:
                                    # Tentar converter para datetime se for YYYY-MM-DD
                                    if len(data_ultima_manutencao) >= 10:
                                        data_obj = datetime.strptime(data_ultima_manutencao[:10], '%Y-%m-%d')
                                        data_proxima = (data_obj + timedelta(days=equip.get('frequencia_manutencao', 180))).strftime('%d/%m/%Y')
                                    else:
                                        data_proxima = "Erro no formato de data"
                                else:
                                    data_proxima = "Data inválida"
                            except Exception as e:
                                logger.warning(f"Erro ao calcular próxima data para {data_ultima_manutencao}: {str(e)}")
                                data_proxima = "Erro no cálculo"
                        
                        proxima_item = QTableWidgetItem(f"{data_proxima}")
                else:
                    proxima_item = QTableWidgetItem("Não programada")
                    
                self.equipment_table.setItem(i, 9, proxima_item)
                
                # Aplicar cores de alerta se definidas
                if cor_linha and cor_texto:
                    for col in range(self.equipment_table.columnCount()):
                        item = self.equipment_table.item(i, col)
                        if item:
                            item.setBackground(cor_linha)
                            item.setForeground(cor_texto)
                            # Adiciona indicador visual de urgência - um ponto de exclamação no início para manutenções atrasadas
                            if col == 9 and dias_ate_manutencao <= 0:
                                item.setText("❗ " + item.text())
                            # Adiciona indicador visual de alerta - um aviso no início para manutenções próximas
                            elif col == 9 and dias_ate_manutencao <= 30:
                                item.setText("⚠️ " + item.text())
            
            logger.debug(f"Carregados {len(equipment_list)} equipamentos")
            # Forçar atualização imediata da tabela
            self.equipment_table.viewport().update()
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.warning(self, "Erro", f"Não foi possível carregar os equipamentos: {str(e)}")
    
    def filter_equipment(self):
        """Filtra os equipamentos na tabela"""
        text = self.equipment_search_input.text().lower()
        for i in range(self.equipment_table.rowCount()):
            match = False
            # Verifica todas as colunas
            for j in range(self.equipment_table.columnCount()):
                item = self.equipment_table.item(i, j)
                if item and text in item.text().lower():
                    match = True
                    break
            self.equipment_table.setRowHidden(i, not match)
    
    def refresh_all_tables(self):
        """Atualiza todas as tabelas com dados frescos do banco"""
        try:
            self.load_equipment()
            self.load_inspections()
            self.load_reports()
        except Exception as e:
            logger.error(f"Erro ao atualizar tabelas: {str(e)}")
            
    def add_inspection(self):
        """Abre a janela modal para adicionar inspeção"""
        try:
            modal = InspectionModal(self, self.is_dark)
            
            # Obtém o ID da empresa
            company_id = self.get_company_id()
            if company_id is None:
                QMessageBox.warning(self, "Erro", "Não foi possível identificar sua empresa")
                return
            
            # Carrega os equipamentos da empresa no combobox
            equipment = self.equipment_controller.get_equipment_by_company(company_id)
            modal.load_equipment_options(equipment)
            
            # Carrega os engenheiros disponíveis
            engineers = self.auth_controller.get_engineers()
            modal.load_engineer_options(engineers)
            
            if modal.exec_() == QDialog.Accepted:
                data = modal.get_data()
                success, message = self.inspection_controller.create_inspection(
                    equipment_id=data['equipamento_id'],
                    engineer_id=data['engenheiro_id'],
                    date=data['data_inspecao'],
                    inspection_type=data['tipo_inspecao'],
                    result=data['resultado'],
                    recommendations=data['recomendacoes']
                )
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_inspections()
                else:
                    QMessageBox.warning(self, "Erro", message)
        except Exception as e:
            logger.error(f"Erro ao adicionar inspeção: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Não foi possível adicionar a inspeção: {str(e)}")
                
    def add_report(self):
        """Abre a janela modal para adicionar relatório"""
        try:
            modal = ReportModal(self, self.is_dark)
            
            # Obtém o ID da empresa
            company_id = self.get_company_id()
            if company_id is None:
                QMessageBox.warning(self, "Erro", "Não foi possível identificar sua empresa")
                return
            
            # Carrega as inspeções da empresa no combobox
            inspections = self.inspection_controller.get_inspections_by_company(company_id)
            for insp in inspections:
                modal.inspecao_combo.addItem(
                    f"{insp.get('equipamento_tag', '')} - {insp['tipo']} ({insp['data']})", 
                    insp['id']
                )
            
            if modal.exec_() == QDialog.Accepted:
                data = modal.get_data()
                success, message = self.report_controller.create_report(
                    inspection_id=data['inspecao_id'],
                    issue_date=data['data_emissao'],
                    file_link=data['link_arquivo'],
                    observations=data['observacoes']
                )
                if success:
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_reports()
                else:
                    QMessageBox.warning(self, "Erro", message) 
        except Exception as e:
            logger.error(f"Erro ao adicionar relatório: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Não foi possível adicionar o relatório: {str(e)}")
    
    def load_inspections(self):
        """Carrega as inspeções na tabela"""
        # Implementação para carregar inspeções
        pass
        
    def load_reports(self):
        """Carrega os relatórios na tabela"""
        # Implementação para carregar relatórios
        pass
        
    def view_report(self):
        """Abre o relatório selecionado para visualização"""
        try:
            selected_rows = self.report_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "Aviso", "Selecione um relatório para visualizar")
                return
                
            selected_row = selected_rows[0].row()
            # Obter o ID da inspeção associada ao relatório (coluna 0)
            inspection_id = self.report_table.item(selected_row, 0).text()
            
            # Obter o arquivo do relatório (coluna 2)
            arquivo = self.report_table.item(selected_row, 2).text()
            
            if not arquivo:
                QMessageBox.warning(self, "Aviso", "Este relatório não possui arquivo para visualização")
                return
                
            # Buscar todos os relatórios para encontrar o correto
            reports = self.report_controller.get_reports_by_company(self.get_company_id())
            report_data = None
            
            for report in reports:
                if (str(report.get('inspecao_id')) == inspection_id and 
                    report.get('link_arquivo', report.get('arquivo', '')) == arquivo):
                    report_data = report
                    break
                    
            if not report_data:
                QMessageBox.warning(self, "Erro", "Não foi possível encontrar os dados do relatório")
                return
                
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo):
                QMessageBox.warning(self, "Erro", f"O arquivo '{arquivo}' não foi encontrado")
                return
                
            # Abrir o arquivo com o programa padrão do sistema
            try:
                if sys.platform == 'win32':
                    os.startfile(arquivo)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', arquivo], check=True)
                else:  # Linux
                    subprocess.run(['xdg-open', arquivo], check=True)
                    
                logger.info(f"Arquivo aberto com sucesso: {arquivo}")
            except Exception as e:
                logger.error(f"Erro ao abrir arquivo: {str(e)}")
                QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo: {str(e)}")
                
        except Exception as e:
            logger.error(f"Erro ao visualizar relatório: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao visualizar relatório: {str(e)}")
    
    def filter_inspections(self):
        """Filtra as inspeções na tabela"""
        text = self.insp_search_input.text().lower()
        for i in range(self.inspection_table.rowCount()):
            match = False
            # Verifica todas as colunas
            for j in range(self.inspection_table.columnCount()):
                item = self.inspection_table.item(i, j)
                if item and text in item.text().lower():
                    match = True
                    break
            self.inspection_table.setRowHidden(i, not match)
    
    def filter_reports(self):
        """Filtra os relatórios na tabela"""
        text = self.report_search_input.text().lower()
        for i in range(self.report_table.rowCount()):
            match = False
            # Verifica todas as colunas
            for j in range(self.report_table.columnCount()):
                item = self.report_table.item(i, j)
                if item and text in item.text().lower():
                    match = True
                    break
            self.report_table.setRowHidden(i, not match)
    
    def register_maintenance(self):
        """Abre a janela modal para registrar manutenção de equipamento"""
        try:
            # Verificar se um equipamento está selecionado
            selected_rows = self.equipment_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "Aviso", "Selecione um equipamento para registrar a manutenção")
                return
                
            row = selected_rows[0].row()
            tag = self.equipment_table.item(row, 0).text()
            
            # Buscar o ID do equipamento a partir da tag
            company_id = self.get_company_id()
            equipment_list = self.equipment_controller.get_equipment_by_company(company_id)
            
            equipment_id = None
            equipment_data = None
            
            for equip in equipment_list:
                if equip.get('tag') == tag:
                    equipment_id = equip.get('id')
                    equipment_data = equip
                    break
                    
            if not equipment_id:
                QMessageBox.warning(self, "Erro", f"Não foi possível encontrar o equipamento com tag {tag}")
                return
            
            # Abrir o modal de manutenção
            modal = MaintenanceModal(self, self.is_dark)
            
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