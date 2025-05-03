#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface gráfica do cliente do sistema.
"""

import logging
import traceback
import os
import sys
import subprocess
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QFileDialog, QToolButton,
    QHeaderView, QDialog
)
from PyQt5.QtCore import Qt, QDate, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor

from controllers.auth_controller import AuthController
from database.models import DatabaseModels
from controllers.equipment_controller import EquipmentController
from controllers.inspection_controller import InspectionController
from controllers.report_controller import ReportController
from ui.modals import InspectionModal, ReportModal, MaintenanceModal
from ui.styles import Styles

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
                'browse': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>''',
                'equipment': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="7"></circle>
                    <circle cx="12" cy="12" r="3"></circle>
                    <line x1="12" y1="5" x2="12" y2="1"></line>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="5" y1="12" x2="1" y2="12"></line>
                    <line x1="19" y1="12" x2="23" y2="12"></line>
                </svg>''',
                'maintenance': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 10h-4v4h4v-4z"></path>
                    <path d="M14 14h-4v4h4v-4z"></path>
                    <path d="M14 18h-4v4h4v-4z"></path>
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
            
            # Estilos padrão para botões
            self.button_style = {
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
            
            logger.debug("Iniciando setup da UI")
            self.initUI()
            self.apply_theme()
            
            # Carregar equipamentos na inicialização
            self.load_equipment()
            
            # Configurar timer para atualização
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_all_tables)
            self.refresh_timer.start(10000)  # Atualiza a cada 10 segundos
            
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

    def apply_theme(self):
        """Aplica o tema escuro ou claro à interface"""
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
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #3a3d40;
                        color: #ffffff;
                    }
                """
                
                # Estilo para o botão de tema
                theme_button_style = """
                    QPushButton {
                        background-color: #aaaaaa;
                        color: #121212;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #999999;
                    }
                    QPushButton:pressed {
                        background-color: #888888;
                    }
                """
                
                self.theme_button.setStyleSheet(theme_button_style)
                
                # Aplica às tabelas
                if hasattr(self, 'equipment_table'):
                    self.equipment_table.setStyleSheet(table_style)
                    self.equipment_table.setAlternatingRowColors(True)
                
                # Atualiza ícones
                if hasattr(self, 'theme_button'):
                    self.theme_button.setIcon(self.create_icon_from_svg(self.icons['theme']))
                if hasattr(self, 'logout_button'):
                    self.logout_button.setIcon(self.create_icon_from_svg(self.icons['logout']))
                
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
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #e0e0e0;
                        color: #000000;
                    }
                """
                
                # Estilo para o botão de tema
                theme_button_style = """
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
                """
                
                self.theme_button.setStyleSheet(theme_button_style)
                
                # Aplica às tabelas
                if hasattr(self, 'equipment_table'):
                    self.equipment_table.setStyleSheet(table_style)
                    self.equipment_table.setAlternatingRowColors(True)
                
                # Atualiza ícones
                if hasattr(self, 'theme_button'):
                    self.theme_button.setIcon(self.create_icon_from_svg(self.icons['theme']))
                if hasattr(self, 'logout_button'):
                    self.logout_button.setIcon(self.create_icon_from_svg(self.icons['logout']))
                
        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar tema: {str(e)}")

    def toggle_theme(self):
        """Alterna entre tema escuro e claro"""
        self.is_dark = not self.is_dark
        self.apply_theme()

    def initUI(self):
        """Inicializa a interface do usuário."""
        try:
            self.setWindowTitle(f"Sistema de Inspeções NR-13 - {self.company}")
            self.setMinimumSize(1024, 768)
            
            # Definir ícone da janela com o logo da empresa
            self.setWindowIcon(QIcon("ui/CTREINA_LOGO.png"))
            
            # Widget central
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
            title = QLabel(f"Painel do Cliente - {self.company}")
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
            
            # Criação das abas (apenas equipamentos)
            self.tabs = QTabWidget()
            
            # Criar aba de equipamentos
            self.create_equipment_tab()
            
            # Adicionar ao layout principal
            layout.addWidget(self.tabs)
            
        except Exception as e:
            logger.error(f"Erro ao inicializar UI: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar interface: {str(e)}")
            raise

    def create_equipment_tab(self):
        """Cria a aba de equipamentos"""
        try:
            # Criar widget para a aba de equipamentos
            equipment_tab = QWidget()
            equipment_layout = QVBoxLayout(equipment_tab)
            
            # Container para barra de pesquisa
            top_container = QHBoxLayout()
            
            # Adicionar espaçamento e título da seção
            equipment_title = QLabel("Equipamentos da Empresa")
            equipment_title.setStyleSheet("font-size: 18px; font-weight: bold;")
            top_container.addWidget(equipment_title)
            
            top_container.addStretch()
            
            # Barra de pesquisa
            search_container = QHBoxLayout()
            search_label = QLabel("Pesquisar:")
            search_container.addWidget(search_label)
            
            self.equipment_search_box = QLineEdit()
            self.equipment_search_box.setPlaceholderText("Digite para filtrar...")
            self.equipment_search_box.textChanged.connect(self.filter_equipment)
            search_container.addWidget(self.equipment_search_box)
            
            top_container.addLayout(search_container)
            
            equipment_layout.addLayout(top_container)
            
            # Tabela de equipamentos
            self.equipment_table = QTableWidget()
            self.equipment_table.setColumnCount(16)  # Mesmo número de colunas que o admin_ui
            self.equipment_table.setHorizontalHeaderLabels([
                "Tag", "Categoria", "Empresa", "Fabricante", "Ano", "P. Projeto",
                "P. Trabalho", "Volume", "Fluido", "Status", "Cat. NR13", "PMTA", "Placa ID", 
                "Nº Registro", "Última Manutenção", "Próxima Manutenção"
            ])
            
            # Configurações da tabela
            self.equipment_table.verticalHeader().setVisible(False)
            self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.equipment_table.setSelectionMode(QTableWidget.SingleSelection)
            self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Ajustar tamanho de algumas colunas
            equipment_header = self.equipment_table.horizontalHeader()
            equipment_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tag
            equipment_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Categoria
            equipment_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Empresa
            
            equipment_layout.addWidget(self.equipment_table)
            
            # Adicionar a aba ao TabWidget
            self.tabs.addTab(equipment_tab, QIcon("ui/equipamentos.png"), "Equipamentos")
            
        except Exception as e:
            logger.error(f"Erro ao criar aba de equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao criar aba de equipamentos: {str(e)}")
            raise

    def logout(self):
        """Emite sinal de logout."""
        logger.info("Logout solicitado pelo usuário")
        self.logout_requested.emit()
        
    def refresh_all_tables(self):
        """Atualiza todas as tabelas com dados recentes"""
        try:
            # Forçar sincronização com o banco
            self.equipment_controller.force_sync()
            
            # Recarregar os dados
            self.load_equipment()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar tabelas: {str(e)}")
            logger.error(traceback.format_exc()) 

    def load_equipment(self):
        """Carrega equipamentos da empresa do usuário logado."""
        try:
            logger.debug(f"Carregando equipamentos da empresa {self.company}")
            self.equipment_table.setRowCount(0)
            
            # Obter o ID da empresa do usuário logado
            company_id = self.auth_controller.get_company_id_by_name(self.company)
            if not company_id:
                logger.error(f"Não foi possível encontrar o ID da empresa {self.company}")
                return
                
            # Obter equipamentos apenas da empresa do usuário
            equipments = self.equipment_controller.get_equipment_by_company(company_id)
            logger.debug(f"Obtidos {len(equipments)} equipamentos")
            
            # Preencher a tabela
            self.equipment_table.setRowCount(len(equipments))
            
            for row, equipment in enumerate(equipments):
                # Tag
                tag_item = QTableWidgetItem(equipment.get('tag', ''))
                tag_item.setData(Qt.UserRole, equipment.get('id'))
                self.equipment_table.setItem(row, 0, tag_item)
                
                # Categoria
                category_item = QTableWidgetItem(equipment.get('categoria', ''))
                category_item.setData(Qt.UserRole, equipment.get('categoria_id'))
                self.equipment_table.setItem(row, 1, category_item)
                
                # Empresa
                company_data = self.auth_controller.get_company_by_id(equipment.get('empresa_id'))
                company_name = company_data.get('nome', '') if company_data else ''
                company_item = QTableWidgetItem(company_name)
                company_item.setData(Qt.UserRole, equipment.get('empresa_id'))
                self.equipment_table.setItem(row, 2, company_item)
                
                # Fabricante
                manufacturer_item = QTableWidgetItem(equipment.get('fabricante', ''))
                self.equipment_table.setItem(row, 3, manufacturer_item)
                
                # Ano
                year_item = QTableWidgetItem(str(equipment.get('ano_fabricacao', '')))
                self.equipment_table.setItem(row, 4, year_item)
                
                # Pressão de Projeto
                p_projeto_item = QTableWidgetItem(str(equipment.get('pressao_projeto', '')))
                self.equipment_table.setItem(row, 5, p_projeto_item)
                
                # Pressão de Trabalho
                p_trabalho_item = QTableWidgetItem(str(equipment.get('pressao_trabalho', '')))
                self.equipment_table.setItem(row, 6, p_trabalho_item)
                
                # Volume
                volume_item = QTableWidgetItem(str(equipment.get('volume', '')))
                self.equipment_table.setItem(row, 7, volume_item)
                
                # Fluido
                fluid_item = QTableWidgetItem(equipment.get('fluido_trabalho', ''))
                self.equipment_table.setItem(row, 8, fluid_item)
                
                # Status
                status = equipment.get('ativo', 1)
                status_text = "Ativo" if status == 1 else "Inativo"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor('#28a745' if status == 1 else '#dc3545'))
                self.equipment_table.setItem(row, 9, status_item)
                
                # Categoria NR13
                nr13_category = equipment.get('categoria_nr13', '')
                nr13_item = QTableWidgetItem(nr13_category)
                self.equipment_table.setItem(row, 10, nr13_item)
                
                # PMTA
                pmta_item = QTableWidgetItem(str(equipment.get('pmta', '')))
                self.equipment_table.setItem(row, 11, pmta_item)
                
                # Placa de Identificação
                placa_item = QTableWidgetItem(equipment.get('placa_identificacao', ''))
                self.equipment_table.setItem(row, 12, placa_item)
                
                # Número de Registro
                registro_item = QTableWidgetItem(equipment.get('numero_registro', ''))
                self.equipment_table.setItem(row, 13, registro_item)
                
                # Última Manutenção
                ultima_man = equipment.get('data_ultima_manutencao')
                ultima_man_text = ultima_man if ultima_man else "Não realizada"
                ultima_man_item = QTableWidgetItem(ultima_man_text)
                self.equipment_table.setItem(row, 14, ultima_man_item)
                
                # Próxima Manutenção e Coloração da Linha
                dias_ate_manutencao = equipment.get('dias_ate_manutencao')
                row_color = None
                text_color = None
                
                if ultima_man and equipment.get('frequencia_manutencao'):
                    proxima_data = None
                    if isinstance(dias_ate_manutencao, int):
                        # Calcular a próxima manutenção a partir dos dias restantes
                        proxima_data = datetime.now() + timedelta(days=dias_ate_manutencao)
                        proxima_man = proxima_data.strftime("%Y-%m-%d")
                        
                        # Definir cores de acordo com a urgência e o tema
                        if dias_ate_manutencao <= 7:  # Vermelho: 1 semana ou menos
                            if self.is_dark:
                                row_color = QColor(90, 20, 20)  # Vermelho escuro para tema escuro
                                text_color = QColor(255, 150, 150)  # Texto vermelho claro
                            else:
                                row_color = QColor(255, 200, 200)  # Vermelho claro para tema claro
                                text_color = QColor(139, 0, 0)  # Texto vermelho escuro
                            logger.debug(f"Equipamento {equipment.get('tag')} com manutenção URGENTE (≤ 7 dias)")
                        elif dias_ate_manutencao <= 15:  # Laranja: 15 dias ou menos
                            if self.is_dark:
                                row_color = QColor(90, 60, 10)  # Laranja escuro para tema escuro
                                text_color = QColor(255, 200, 120)  # Texto laranja claro
                            else:
                                row_color = QColor(255, 230, 180)  # Laranja claro para tema claro
                                text_color = QColor(102, 51, 0)  # Texto marrom escuro
                            logger.debug(f"Equipamento {equipment.get('tag')} com manutenção ALTA (≤ 15 dias)")
                        elif dias_ate_manutencao <= 30:  # Amarelo: 30 dias ou menos
                            if self.is_dark:
                                row_color = QColor(90, 90, 10)  # Amarelo escuro para tema escuro
                                text_color = QColor(255, 255, 150)  # Texto amarelo claro
                            else:
                                row_color = QColor(255, 255, 180)  # Amarelo claro para tema claro
                                text_color = QColor(102, 102, 0)  # Texto amarelo escuro
                            logger.debug(f"Equipamento {equipment.get('tag')} com manutenção MÉDIA (≤ 30 dias)")
                    else:
                        # Tentar calcular a partir da data_ultima_manutencao e frequencia_manutencao
                        try:
                            data_ultima = datetime.strptime(ultima_man, "%Y-%m-%d")
                            frequencia = int(equipment.get('frequencia_manutencao'))
                            proxima_data = data_ultima + timedelta(days=frequencia)
                            proxima_man = proxima_data.strftime("%Y-%m-%d")
                            
                            # Calcular dias até a próxima manutenção
                            dias_restantes = (proxima_data - datetime.now()).days
                            
                            # Definir cores de acordo com a urgência e o tema
                            if dias_restantes <= 7:  # Vermelho: 1 semana ou menos
                                if self.is_dark:
                                    row_color = QColor(90, 20, 20)  # Vermelho escuro para tema escuro
                                    text_color = QColor(255, 150, 150)  # Texto vermelho claro
                                else:
                                    row_color = QColor(255, 200, 200)  # Vermelho claro para tema claro
                                    text_color = QColor(139, 0, 0)  # Texto vermelho escuro
                                logger.debug(f"Equipamento {equipment.get('tag')} com manutenção URGENTE (≤ 7 dias)")
                            elif dias_restantes <= 15:  # Laranja: 15 dias ou menos
                                if self.is_dark:
                                    row_color = QColor(90, 60, 10)  # Laranja escuro para tema escuro
                                    text_color = QColor(255, 200, 120)  # Texto laranja claro
                                else:
                                    row_color = QColor(255, 230, 180)  # Laranja claro para tema claro
                                    text_color = QColor(102, 51, 0)  # Texto marrom escuro
                                logger.debug(f"Equipamento {equipment.get('tag')} com manutenção ALTA (≤ 15 dias)")
                            elif dias_restantes <= 30:  # Amarelo: 30 dias ou menos
                                if self.is_dark:
                                    row_color = QColor(90, 90, 10)  # Amarelo escuro para tema escuro
                                    text_color = QColor(255, 255, 150)  # Texto amarelo claro
                                else:
                                    row_color = QColor(255, 255, 180)  # Amarelo claro para tema claro
                                    text_color = QColor(102, 102, 0)  # Texto amarelo escuro
                                logger.debug(f"Equipamento {equipment.get('tag')} com manutenção MÉDIA (≤ 30 dias)")
                        except Exception as e:
                            logger.error(f"Erro ao calcular próxima manutenção: {str(e)}")
                            proxima_man = "Erro no cálculo"
                else:
                    proxima_man = "Não agendada"
                
                proxima_man_item = QTableWidgetItem(proxima_man)
                self.equipment_table.setItem(row, 15, proxima_man_item)
                
                # Aplicar cor à linha de acordo com a urgência
                if row_color and text_color:
                    for col in range(self.equipment_table.columnCount()):
                        item = self.equipment_table.item(row, col)
                        if item:
                            item.setBackground(row_color)
                            item.setForeground(text_color)
            
            logger.debug(f"Tabela de equipamentos carregada com {self.equipment_table.rowCount()} linhas")
            
            # Ajustar altura das linhas
            for row in range(self.equipment_table.rowCount()):
                self.equipment_table.setRowHeight(row, 36)
                
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
    
    def filter_equipment(self):
        """Filtra a tabela de equipamentos com base no texto de pesquisa."""
        try:
            search_text = self.equipment_search_box.text().lower()
            logger.debug(f"Filtrando equipamentos com texto: '{search_text}'")
            
            for row in range(self.equipment_table.rowCount()):
                should_show = False
                
                # Verificar em todas as colunas visíveis
                for col in range(self.equipment_table.columnCount()):
                    item = self.equipment_table.item(row, col)
                    if item and search_text in item.text().lower():
                        should_show = True
                        break
                
                # Mostrar ou esconder a linha
                self.equipment_table.setRowHidden(row, not should_show)
        
        except Exception as e:
            logger.error(f"Erro ao filtrar equipamentos: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar equipamentos: {str(e)}") 