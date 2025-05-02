#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janelas modais para formulários de cadastro
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit, QTextEdit, QFormLayout, QFileDialog, QScrollArea, QFrame,
    QWidget, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
import os
import sys
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import logging

# Adiciona o diretório raiz ao PATH para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuração do logger
logger = logging.getLogger(__name__)

from ui.styles import Styles

class BaseModal(QDialog):
    """Classe base para todas as janelas modais"""
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setModal(True)
        
    def apply_theme(self):
        """Aplica o tema atual"""
        if self.is_dark:
            self.setStyleSheet(Styles.get_dark_theme())
        else:
            self.setStyleSheet(Styles.get_light_theme())

class UserModal(BaseModal):
    """Janela modal para cadastro de usuários"""
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent, is_dark)
        self.setWindowTitle("Cadastrar Usuário")
        self.setup_form()
        
    def setup_form(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Campos do formulário
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.nome_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.nome_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.senha_input)
        
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["admin", "cliente", "eng"])
        self.tipo_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.tipo_input)
        
        self.empresa_input = QLineEdit()
        self.empresa_input.setPlaceholderText("Empresa")
        self.empresa_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Empresa:"))
        layout.addWidget(self.empresa_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setMinimumHeight(36)
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
    def get_data(self):
        """Retorna os dados do formulário"""
        return {
            "nome": self.nome_input.text().strip(),
            "email": self.email_input.text().strip(),
            "senha": self.senha_input.text().strip(),
            "tipo": self.tipo_input.currentText(),
            "empresa": self.empresa_input.text().strip()
        }
        
    def accept(self):
        """Validar e aceitar o modal"""
        # Validação básica de campos
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Atenção", "O campo Nome é obrigatório")
            return
            
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Atenção", "O campo Email é obrigatório")
            return
            
        if not self.senha_input.text().strip():
            QMessageBox.warning(self, "Atenção", "O campo Senha é obrigatório")
            return
            
        # Se passou pela validação, aceita o diálogo
        super().accept()

class EquipmentModal(QDialog):
    def __init__(self, parent=None, is_dark=False, equipment_data=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.equipment_data = equipment_data
        self.setWindowTitle("Equipamento")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.resize(650, 750)
        self.setup_ui()
        self.apply_theme()
        # Carregar dados apenas se for edição
        if self.equipment_data:
            self.load_equipment_data()
        
    def setup_ui(self):
        """Configura a interface do modal"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title_label = QLabel("Dados do Equipamento")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(2)
        main_layout.addWidget(line)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 15, 10, 15)
        
        def create_section_title(text):
            section = QLabel(text)
            section_font = section.font()
            section_font.setPointSize(13)
            section_font.setBold(True)
            section.setFont(section_font)
            return section
        
        def setup_input(widget, height=36):
            widget.setMinimumHeight(height)
            return widget
        
        id_section = create_section_title("Identificação")
        form_layout.addRow(id_section)
        
        spacer_widget = QWidget()
        spacer_widget.setMinimumHeight(10)
        form_layout.addRow("", spacer_widget)
        
        self.tag_input = setup_input(QLineEdit())
        self.tag_input.setPlaceholderText("Ex: VAP-001")
        self.tag_input.setToolTip("Código único de identificação do equipamento")
        form_layout.addRow("Tag*:", self.tag_input)
        
        self.categoria_input = setup_input(QComboBox())
        self.categoria_input.addItems([
            "Vaso de Pressão", "Caldeira", "Tubulação", "Tanque", "Reator", 
            "Trocador de Calor", "Compressor", "Filtro", "Outro"
        ])
        self.categoria_input.setToolTip("Tipo/categoria do equipamento")
        form_layout.addRow("Categoria*:", self.categoria_input)
        
        # ---- Adicionar ComboBox de Empresa ----
        self.empresa_combo = setup_input(QComboBox())
        self.empresa_combo.setToolTip("Empresa à qual o equipamento pertence")
        form_layout.addRow("Empresa*:", self.empresa_combo)
        # --------------------------------------
        
        spacer_widget2 = QWidget()
        spacer_widget2.setMinimumHeight(20)
        form_layout.addRow("", spacer_widget2)
        
        tech_section = create_section_title("Dados Técnicos")
        form_layout.addRow(tech_section)
        
        spacer_widget3 = QWidget()
        spacer_widget3.setMinimumHeight(10)
        form_layout.addRow("", spacer_widget3)
        
        self.fabricante_input = setup_input(QComboBox())
        self.fabricante_input.setEditable(True)
        self.fabricante_input.addItems([
            "Fabricante Industrial Ltda",
            "Indústria Mecânica SA",
            "Equipamentos Industriais Brasil",
            "Metalúrgica Brasileira",
            "Caldeiras e Vasos Ltda"
        ])
        self.fabricante_input.setToolTip("Nome do fabricante do equipamento")
        form_layout.addRow("Fabricante:", self.fabricante_input)
        
        self.ano_fabricacao_input = setup_input(QSpinBox())
        self.ano_fabricacao_input.setRange(1900, 2100)
        self.ano_fabricacao_input.setValue(2020)
        self.ano_fabricacao_input.setToolTip("Ano em que o equipamento foi fabricado")
        form_layout.addRow("Ano de Fabricação:", self.ano_fabricacao_input)
        
        self.pressao_projeto_input = setup_input(QDoubleSpinBox())
        self.pressao_projeto_input.setRange(0.1, 1000.0)
        self.pressao_projeto_input.setValue(10.0)
        self.pressao_projeto_input.setSingleStep(0.1)
        self.pressao_projeto_input.setDecimals(2)
        self.pressao_projeto_input.setSuffix(" kgf/cm²")
        self.pressao_projeto_input.setToolTip("Pressão de projeto do equipamento")
        form_layout.addRow("Pressão de Projeto*:", self.pressao_projeto_input)
        
        self.pressao_trabalho_input = setup_input(QDoubleSpinBox())
        self.pressao_trabalho_input.setRange(0.1, 1000.0)
        self.pressao_trabalho_input.setValue(8.0)
        self.pressao_trabalho_input.setSingleStep(0.1)
        self.pressao_trabalho_input.setDecimals(2)
        self.pressao_trabalho_input.setSuffix(" kgf/cm²")
        self.pressao_trabalho_input.setToolTip("Pressão de trabalho do equipamento")
        form_layout.addRow("Pressão de Trabalho*:", self.pressao_trabalho_input)
        
        self.volume_input = setup_input(QDoubleSpinBox())
        self.volume_input.setRange(0.1, 10000.0)
        self.volume_input.setValue(100.0)
        self.volume_input.setSingleStep(1.0)
        self.volume_input.setDecimals(2)
        self.volume_input.setSuffix(" m³")
        self.volume_input.setToolTip("Volume interno do equipamento")
        form_layout.addRow("Volume*:", self.volume_input)
        
        self.fluido_input = setup_input(QComboBox())
        self.fluido_input.setEditable(True)
        self.fluido_input.addItems([
            "Água", "Vapor d'água", "Óleo", "Ar comprimido", 
            "Gás natural", "GLP", "Nitrogênio", "Oxigênio", "Outro"
        ])
        self.fluido_input.setToolTip("Fluido que normalmente contém ou transporta")
        form_layout.addRow("Fluido*:", self.fluido_input)
        
        spacer_widget4 = QWidget()
        spacer_widget4.setMinimumHeight(20)
        form_layout.addRow("", spacer_widget4)
        
        # ---- Adicionar campos NR-13 ----
        nr13_section = create_section_title("Dados NR-13")
        form_layout.addRow(nr13_section)
        nr13_spacer = QWidget()
        nr13_spacer.setMinimumHeight(10)
        form_layout.addRow("", nr13_spacer)

        self.categoria_nr13_input = setup_input(QComboBox())
        self.categoria_nr13_input.addItems([
            "Não se Aplica", "Categoria I", "Categoria II", "Categoria III", "Categoria IV"
        ])
        self.categoria_nr13_input.setToolTip("Categoria NR-13 do equipamento")
        form_layout.addRow("Categoria NR-13:", self.categoria_nr13_input)

        self.pmta_input = setup_input(QLineEdit())
        self.pmta_input.setPlaceholderText("Ex: 123456")
        self.pmta_input.setToolTip("PMTA do equipamento")
        form_layout.addRow("PMTA:", self.pmta_input)

        self.placa_identificacao_input = setup_input(QLineEdit())
        self.placa_identificacao_input.setPlaceholderText("Ex: ABC-1234")
        self.placa_identificacao_input.setToolTip("Placa de identificação do equipamento")
        form_layout.addRow("Placa Identificação:", self.placa_identificacao_input)

        self.numero_registro_input = setup_input(QLineEdit())
        self.numero_registro_input.setPlaceholderText("Ex: 987654")
        self.numero_registro_input.setToolTip("Número de registro do equipamento")
        form_layout.addRow("Nº Registro:", self.numero_registro_input)
        # ---- Fim campos NR-13 ----
        
        self.note_label = QLabel("* Campos obrigatórios")
        self.note_label.setProperty("note", True)
        form_layout.addRow("", self.note_label)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setMinimumHeight(45)
        self.save_button.setMinimumWidth(120)
        self.save_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch(1)
        
        main_layout.addLayout(buttons_layout)
        
        self.load_company_options()
    
    def apply_theme(self):
        """Aplica o tema escuro ou claro ao modal"""
        if self.is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                QLabel {
                    color: #E0E0E0;
                }
                QLabel[note="true"] {
                    font-style: italic;
                    color: #9E9E9E;
                }
                QLineEdit, QComboBox {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 6px;
                    selection-background-color: #3A3A3A;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 6px;
                    selection-background-color: #3A3A3A;
                }
                QSpinBox::up-button, QDoubleSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #505050;
                    border-bottom: 1px solid #505050;
                    border-top-right-radius: 4px;
                    background-color: #404040;
                }
                QSpinBox::down-button, QDoubleSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    border-left: 1px solid #505050;
                    border-top: 1px solid #505050;
                    border-bottom-right-radius: 4px;
                    background-color: #404040;
                }
                QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
                QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #505050;
                }
                QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                    width: 6px;
                    height: 6px;
                    background-color: #E0E0E0;
                }
                QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                    width: 6px;
                    height: 6px;
                    background-color: #E0E0E0;
                }
                /* Garante que o texto na linha de edição é visível */
                QAbstractSpinBox {
                    color: #E0E0E0;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    selection-background-color: #404040;
                    border: 1px solid #505050;
                }
                QComboBox QAbstractItemView::item {
                    color: #E0E0E0;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1C97EA;
                }
                QPushButton:pressed {
                    background-color: #00559B;
                }
                QPushButton[text="Cancelar"] {
                    background-color: #505050;
                }
                QPushButton[text="Cancelar"]:hover {
                    background-color: #606060;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #2D2D2D;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #505050;
                    min-height: 30px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #606060;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QFrame[frameShape="4"] { /* HLine */
                    color: #505050;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                }
                QLabel[note="true"] {
                    font-style: italic;
                    color: #707070;
                }
                QLineEdit, QComboBox {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #C0C0C0;
                    border-radius: 4px;
                    padding: 6px;
                    selection-background-color: #E0E0E0;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #C0C0C0;
                    border-radius: 4px;
                    padding: 6px;
                    selection-background-color: #E0E0E0;
                }
                QSpinBox::up-button, QDoubleSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #C0C0C0;
                    border-bottom: 1px solid #C0C0C0;
                    border-top-right-radius: 4px;
                    background-color: #E8E8E8;
                }
                QSpinBox::down-button, QDoubleSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    border-left: 1px solid #C0C0C0;
                    border-top: 1px solid #C0C0C0;
                    border-bottom-right-radius: 4px;
                    background-color: #E8E8E8;
                }
                QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
                QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #D0D0D0;
                }
                QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                    width: 6px;
                    height: 6px;
                    background-color: #333333;
                }
                QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                    width: 6px;
                    height: 6px;
                    background-color: #333333;
                }
                /* Garante que o texto na linha de edição é visível */
                QAbstractSpinBox {
                    color: #333333;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #333333;
                    selection-background-color: #E0E0E0;
                    border: 1px solid #C0C0C0;
                }
                QComboBox QAbstractItemView::item {
                    color: #333333;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1C97EA;
                }
                QPushButton:pressed {
                    background-color: #00559B;
                }
                QPushButton[text="Cancelar"] {
                    background-color: #E0E0E0;
                    color: #333333;
                }
                QPushButton[text="Cancelar"]:hover {
                    background-color: #D0D0D0;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #F0F0F0;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #C0C0C0;
                    min-height: 30px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #A0A0A0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QFrame[frameShape="4"] { /* HLine */
                    color: #C0C0C0;
                }
            """)
        
        if hasattr(self, 'note_label'):
            self.note_label.setProperty("note", True)
            self.note_label.style().unpolish(self.note_label)
            self.note_label.style().polish(self.note_label)
        
    def load_company_options(self, companies=None):
        """Carrega as opções de empresas no combobox"""
        try:
            logger.debug(f"Carregando {len(companies) if companies else 0} empresas no modal")
            self.empresa_combo.clear()
            # Sempre habilita o ComboBox
            self.empresa_combo.setEnabled(True)
            if companies is None or not companies:
                logger.warning("Nenhuma empresa encontrada para carregar no modal.")
                self.empresa_combo.addItem("Nenhuma empresa cadastrada", 0)
                return
            for company in companies:
                self.empresa_combo.addItem(company['nome'], company['id'])
            logger.debug(f"{len(companies)} empresas carregadas no ComboBox.")
            # Se estiver editando, selecionar a empresa correta
            if self.equipment_data and self.equipment_data.get('empresa_id'):
                empresa_id_edicao = self.equipment_data.get('empresa_id')
                index = self.empresa_combo.findData(empresa_id_edicao)
                if index >= 0:
                    self.empresa_combo.setCurrentIndex(index)
                else:
                    logger.warning(f"Empresa ID {empresa_id_edicao} do equipamento em edição não encontrada na lista.")
        except Exception as e:
            logger.error(f"Erro ao carregar empresas no modal: {str(e)}")

    def load_equipment_data(self):
        """Carrega os dados do equipamento para edição"""
        if not self.equipment_data:
            return
        
        self.tag_input.setText(self.equipment_data.get('tag', ''))
        
        categoria_idx = self.categoria_input.findText(self.equipment_data.get('categoria', ''))
        if categoria_idx >= 0:
            self.categoria_input.setCurrentIndex(categoria_idx)
        
        # A seleção da empresa é feita em load_company_options quando chamado pelo admin_ui
        # Não precisamos definir self.empresa_id aqui explicitamente.
        
        fabricante = self.equipment_data.get('fabricante', '')
        if fabricante:
            idx = self.fabricante_input.findText(fabricante)
            if idx >= 0:
                self.fabricante_input.setCurrentIndex(idx)
            else:
                self.fabricante_input.setCurrentText(fabricante)
                
        try:
            ano = int(self.equipment_data.get('ano_fabricacao', 2020))
            self.ano_fabricacao_input.setValue(ano)
        except (ValueError, TypeError):
            self.ano_fabricacao_input.setValue(2020)
            
        try:
            pressao = float(self.equipment_data.get('pressao_projeto', 10.0))
            self.pressao_projeto_input.setValue(pressao)
        except (ValueError, TypeError):
            self.pressao_projeto_input.setValue(10.0)
            
        try:
            trabalho = float(self.equipment_data.get('pressao_trabalho', 8.0))
            self.pressao_trabalho_input.setValue(trabalho)
        except (ValueError, TypeError):
            self.pressao_trabalho_input.setValue(8.0)
            
        try:
            volume = float(self.equipment_data.get('volume', 100.0))
            self.volume_input.setValue(volume)
        except (ValueError, TypeError):
            self.volume_input.setValue(100.0)
            
        fluido = self.equipment_data.get('fluido', '')
        if fluido:
            idx = self.fluido_input.findText(fluido)
            if idx >= 0:
                self.fluido_input.setCurrentIndex(idx)
            else:
                self.fluido_input.setCurrentText(fluido)
        
        # NR-13
        categoria_nr13 = self.equipment_data.get('categoria_nr13', '')
        if categoria_nr13:
            idx = self.categoria_nr13_input.findText(categoria_nr13)
            if idx >= 0:
                self.categoria_nr13_input.setCurrentIndex(idx)
            else:
                self.categoria_nr13_input.setCurrentText(categoria_nr13)
        self.pmta_input.setText(self.equipment_data.get('pmta', ''))
        self.placa_identificacao_input.setText(self.equipment_data.get('placa_identificacao', ''))
        self.numero_registro_input.setText(self.equipment_data.get('numero_registro', ''))
        
    def get_data(self):
        """Retorna os dados preenchidos no formulário"""
        tag = self.tag_input.text().strip() or None
        categoria = self.categoria_input.currentText() or None
        empresa_id = self.empresa_combo.currentData() 
        fabricante = self.fabricante_input.currentText() or None
        ano_fabricacao = str(self.ano_fabricacao_input.value() or 0)
        pressao_projeto = str(self.pressao_projeto_input.value() or 0)
        pressao_trabalho = str(self.pressao_trabalho_input.value() or 0)
        volume = str(self.volume_input.value() or 0)
        fluido = self.fluido_input.currentText() or None
        categoria_nr13 = self.categoria_nr13_input.currentText() or None
        pmta = self.pmta_input.text().strip() or None
        placa_identificacao = self.placa_identificacao_input.text().strip() or None
        numero_registro = self.numero_registro_input.text().strip() or None
        return {
            'tag': tag,
            'categoria': categoria,
            'empresa_id': empresa_id,
            'fabricante': fabricante,
            'ano_fabricacao': ano_fabricacao,
            'pressao_projeto': pressao_projeto,
            'pressao_trabalho': pressao_trabalho,
            'volume': volume,
            'fluido': fluido,
            'categoria_nr13': categoria_nr13,
            'pmta': pmta,
            'placa_identificacao': placa_identificacao,
            'numero_registro': numero_registro
        }
        
    def validate_data(self):
        """Valida os dados do formulário antes de salvar"""
        if not self.tag_input.text().strip():
            QMessageBox.warning(self, "Campos Obrigatórios", "O campo 'Tag' é obrigatório.")
            self.tag_input.setFocus()
            return False
            
        # Validar se uma empresa foi selecionada
        if self.empresa_combo.currentIndex() < 0 or not self.empresa_combo.currentData():
            QMessageBox.warning(self, "Campos Obrigatórios", "Selecione a empresa à qual o equipamento pertence.")
            self.empresa_combo.setFocus()
            return False
            
        if self.pressao_projeto_input.value() <= 0:
            QMessageBox.warning(self, "Valor Inválido", "A pressão de projeto deve ser maior que zero.")
            self.pressao_projeto_input.setFocus()
            return False
            
        if self.pressao_trabalho_input.value() <= 0:
            QMessageBox.warning(self, "Valor Inválido", "A pressão de trabalho deve ser maior que zero.")
            self.pressao_trabalho_input.setFocus()
            return False
            
        if self.volume_input.value() <= 0:
            QMessageBox.warning(self, "Valor Inválido", "O volume deve ser maior que zero.")
            self.volume_input.setFocus()
            return False
            
        if not self.fluido_input.currentText():
            QMessageBox.warning(self, "Campos Obrigatórios", "O campo 'Fluido' é obrigatório.")
            self.fluido_input.setFocus()
            return False
            
        return True
        
    def accept(self):
        if self.validate_data():
            super().accept()

class InspectionModal(BaseModal):
    """Janela modal para cadastro de inspeções"""
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent, is_dark)
        self.setWindowTitle("Cadastrar Inspeção")
        self.setup_form()
        
    def setup_form(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Campos do formulário
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Equipamento
        self.equipamento_input = QComboBox()
        self.equipamento_input.setMinimumHeight(36)
        form_layout.addRow("Equipamento:", self.equipamento_input)
        
        # Engenheiro
        self.engenheiro_input = QComboBox()
        self.engenheiro_input.setMinimumHeight(36)
        form_layout.addRow("Engenheiro:", self.engenheiro_input)
        
        # Data
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setMinimumHeight(36)
        form_layout.addRow("Data:", self.data_input)
        
        # Tipo de inspeção
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["Visual", "Ultrassom", "Radiografia", "Periódica", "Inicial", "Outro"])
        self.tipo_input.setMinimumHeight(36)
        form_layout.addRow("Tipo:", self.tipo_input)
        
        # Resultado
        self.resultado_input = QComboBox()
        self.resultado_input.addItems(["Aprovado", "Reprovado", "Pendente", "N/A"])
        self.resultado_input.setMinimumHeight(36)
        form_layout.addRow("Resultado:", self.resultado_input)
        
        # Recomendações
        self.recomendacoes_input = QTextEdit()
        self.recomendacoes_input.setPlaceholderText("Recomendações e observações")
        form_layout.addRow("Recomendações:", self.recomendacoes_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setMinimumHeight(36)
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
    
    def load_equipment_options(self, equipamentos):
        """Carrega as opções de equipamentos no combobox"""
        try:
            logger.debug(f"Carregando {len(equipamentos)} equipamentos no modal")
            self.equipamento_input.clear()
            
            for equip in equipamentos:
                equip_id = equip.get('id', 0)
                tag = equip.get('tag', 'Desconhecido')
                categoria = equip.get('categoria', '')
                display_text = f"{tag} - {categoria} (ID: {equip_id})"
                self.equipamento_input.addItem(display_text, equip_id)
                
            logger.debug(f"Equipamentos carregados: {self.equipamento_input.count()}")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos no modal: {str(e)}")
    
    def load_engineer_options(self, engenheiros):
        """Carrega as opções de engenheiros no combobox"""
        try:
            logger.debug(f"Carregando {len(engenheiros)} engenheiros no modal")
            self.engenheiro_input.clear()
            
            for eng in engenheiros:
                eng_id = eng.get('id', 0)
                nome = eng.get('nome', 'Desconhecido')
                display_text = f"{nome} (ID: {eng_id})"
                self.engenheiro_input.addItem(display_text, eng_id)
                
            logger.debug(f"Engenheiros carregados: {self.engenheiro_input.count()}")
        except Exception as e:
            logger.error(f"Erro ao carregar engenheiros no modal: {str(e)}")
        
    def get_data(self):
        """Retorna os dados do formulário"""
        # Obtém o ID do equipamento a partir dos dados do combobox
        equipamento_id = self.equipamento_input.currentData()
        if equipamento_id is None:
            # Se não houver dados, tenta extrair da string
            try:
                texto = self.equipamento_input.currentText()
                if "ID:" in texto:
                    # Extrai o ID da string (formato: "Nome (ID: 123)")
                    equipamento_id = int(texto.split("ID:")[1].split(")")[0].strip())
                else:
                    # Se não conseguir extrair, usa o primeiro item do texto
                    equipamento_id = int(texto.split(" - ")[0].strip())
            except (ValueError, IndexError):
                equipamento_id = 0
                
        # Obtém o ID do engenheiro a partir dos dados do combobox
        engenheiro_id = self.engenheiro_input.currentData()
        if engenheiro_id is None:
            # Se não houver dados, tenta extrair da string
            try:
                texto = self.engenheiro_input.currentText()
                if "ID:" in texto:
                    # Extrai o ID da string (formato: "Nome (ID: 123)")
                    engenheiro_id = int(texto.split("ID:")[1].split(")")[0].strip())
                else:
                    # Se não conseguir extrair, usa o primeiro item do texto
                    engenheiro_id = 0
            except (ValueError, IndexError):
                engenheiro_id = 0
        
        # Formata a data para o formato ISO
        data_str = self.data_input.date().toString("yyyy-MM-dd")
        
        return {
            "equipamento_id": equipamento_id,
            "engenheiro_id": engenheiro_id,
            "data_inspecao": data_str,
            "tipo_inspecao": self.tipo_input.currentText(),
            "resultado": self.resultado_input.currentText(),
            "recomendacoes": self.recomendacoes_input.toPlainText().strip()
        }
        
    def accept(self):
        """Valida os campos antes de aceitar o modal"""
        # Verifica se um equipamento foi selecionado
        if self.equipamento_input.currentIndex() == -1 or self.equipamento_input.currentText() == "":
            QMessageBox.warning(self, "Campos Obrigatórios", "Selecione um equipamento.")
            self.equipamento_input.setFocus()
            return
            
        # Verifica se um engenheiro foi selecionado
        if self.engenheiro_input.currentIndex() == -1 or self.engenheiro_input.currentText() == "":
            QMessageBox.warning(self, "Campos Obrigatórios", "Selecione um engenheiro.")
            self.engenheiro_input.setFocus()
            return
            
        # Se passou por todas as validações, aceita o modal
        super().accept()

class ReportModal(QDialog):
    """Modal para adicionar/editar relatórios"""
    
    # Adicionar sinal para indicar quando um relatório é salvo
    reportSaved = pyqtSignal()
    
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Configura a interface do modal"""
        self.setWindowTitle("Novo Relatório")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Campo de inspeção
        self.inspecao_combo = QComboBox()
        self.inspecao_combo.setMinimumHeight(36)
        form_layout.addRow("Inspeção:", self.inspecao_combo)
        
        # Campo de data
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setMinimumHeight(36)
        form_layout.addRow("Data:", self.data_input)
        
        # Campo de arquivo
        arquivo_container = QHBoxLayout()
        self.arquivo_input = QLineEdit()
        self.arquivo_input.setPlaceholderText("Link do arquivo")
        self.arquivo_input.setMinimumHeight(36)
        arquivo_container.addWidget(self.arquivo_input)
        
        self.browse_btn = QPushButton("Procurar")
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.clicked.connect(self.browse_file)
        arquivo_container.addWidget(self.browse_btn)
        
        form_layout.addRow("Arquivo:", arquivo_container)
        
        # Campo de observações
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setPlaceholderText("Observações")
        self.observacoes_input.setMinimumHeight(100)
        form_layout.addRow("Observações:", self.observacoes_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_box = QHBoxLayout()
        
        # Botão Salvar
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self.accept)
        button_box.addWidget(self.save_btn)
        
        # Botão Cancelar
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(self.cancel_btn)
        
        layout.addLayout(button_box)
            
    def apply_theme(self):
        """Aplica o tema escuro ou claro ao modal"""
        if self.is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QComboBox, QLineEdit, QDateEdit, QTextEdit {
                    background-color: #333333;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #333333;
                    color: #ffffff;
                    selection-background-color: #505050;
                    border: 1px solid #555555;
                }
                QComboBox QAbstractItemView::item {
                    color: #ffffff;
                }
                QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                    border: 1px solid #2196F3;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1C97EA;
                }
                QPushButton:pressed {
                    background-color: #00559B;
                }
                QPushButton[text="Cancelar"] {
                    background-color: #6c757d;
                }
                QPushButton[text="Cancelar"]:hover {
                    background-color: #5a6268;
                }
                QPushButton[text="Salvar"] {
                    background-color: #28a745;
                }
                QPushButton[text="Salvar"]:hover {
                    background-color: #218838;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                }
                QComboBox, QLineEdit, QDateEdit, QTextEdit {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #333333;
                    selection-background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                }
                QComboBox QAbstractItemView::item {
                    color: #333333;
                }
                QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                    border: 1px solid #0078D7;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1C97EA;
                }
                QPushButton:pressed {
                    background-color: #00559B;
                }
                QPushButton[text="Cancelar"] {
                    background-color: #6c757d;
                }
                QPushButton[text="Cancelar"]:hover {
                    background-color: #5a6268;
                }
                QPushButton[text="Salvar"] {
                    background-color: #28a745;
                }
                QPushButton[text="Salvar"]:hover {
                    background-color: #218838;
                }
            """)
            
    def browse_file(self):
        """Abre diálogo para selecionar arquivo"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Todos os Arquivos (*);;Documentos PDF (*.pdf);;Documentos Word (*.doc *.docx)"
        )
        if file_name:
            self.arquivo_input.setText(file_name)
            
    def get_data(self):
        """Retorna os dados do formulário"""
        return {
            'inspecao_id': self.inspecao_combo.currentData(),
            'data_emissao': self.data_input.date().toString("yyyy-MM-dd"),
            'link_arquivo': self.arquivo_input.text(),
            'observacoes': self.observacoes_input.toPlainText()
        } 

    def accept(self):
        """Sobrescreve o método accept para validar o formulário antes de fechar"""
        # Valida campos obrigatórios
        if self.inspecao_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Atenção", "Selecione uma inspeção.")
            return
            
        if not self.arquivo_input.text().strip():
            QMessageBox.warning(self, "Atenção", "Selecione um arquivo para o relatório.")
            return
            
        # Emite o sinal indicando que o relatório foi salvo
        self.reportSaved.emit()
        
        # Aceita o diálogo e fecha
        super().accept() 

class MaintenanceModal(QDialog):
    """Modal para registrar manutenção de equipamento"""
    
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self.is_dark = is_dark
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Registrar Manutenção")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Data da manutenção
        data_layout = QHBoxLayout()
        data_label = QLabel("Data da Manutenção:")
        data_layout.addWidget(data_label)
        
        self.data_date = QDateEdit()
        self.data_date.setCalendarPopup(True)
        self.data_date.setDate(QDate.currentDate())  # Data atual como padrão
        self.data_date.setDisplayFormat("dd/MM/yyyy")
        data_layout.addWidget(self.data_date)
        
        layout.addLayout(data_layout)
        
        # Frequência de manutenção
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Frequência (dias):")
        freq_layout.addWidget(freq_label)
        
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("180")
        freq_layout.addWidget(self.freq_input)
        
        layout.addLayout(freq_layout)
        
        # Observações
        layout.addWidget(QLabel("Observações:"))
        self.observacoes_text = QTextEdit()
        self.observacoes_text.setMaximumHeight(100)
        layout.addWidget(self.observacoes_text)
        
        # Botões
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.submit_btn = QPushButton("Registrar")
        self.submit_btn.clicked.connect(self.accept)
        self.submit_btn.setDefault(True)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)
        
        # Estilo
        if self.is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2D2D30;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QLineEdit, QTextEdit, QDateEdit {
                    background-color: #1E1E1E;
                    border: 1px solid #3F3F46;
                    color: white;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0063B1;
                }
                QPushButton:pressed {
                    background-color: #004E8C;
                }
                QPushButton#cancel_btn {
                    background-color: #3F3F46;
                }
                QPushButton#cancel_btn:hover {
                    background-color: #505054;
                }
                QPushButton#cancel_btn:pressed {
                    background-color: #606064;
                }
            """)
        
    def get_data(self):
        """Retorna os dados do formulário"""
        data_manutencao = self.data_date.date().toPyDate()
        
        # Tenta converter a frequência para um número inteiro
        frequencia = None
        if self.freq_input.text().strip():
            try:
                frequencia = int(self.freq_input.text().strip())
            except ValueError:
                pass
                
        observacoes = self.observacoes_text.toPlainText()
        
        return {
            'data_manutencao': data_manutencao,
            'frequencia': frequencia,
            'observacoes': observacoes
        } 