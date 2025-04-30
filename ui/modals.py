#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janelas modais para formulários de cadastro
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit, QTextEdit, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import os
import sys

# Adiciona o diretório raiz ao PATH para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class EquipmentModal(QDialog):
    def __init__(self, parent=None, is_dark=False, equipment_data=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.equipment_data = equipment_data
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do modal"""
        self.setWindowTitle("Equipamento")
        self.setMinimumWidth(450)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Campos do formulário
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Ex: VAP-001")
        
        self.categoria_input = QComboBox()
        self.categoria_input.addItems([
            "Vaso de Pressão", "Caldeira", "Tubulação", "Tanque", "Reator", "Outro"
        ])
        
        self.empresa_input = QComboBox()
        # Preencher com empresas disponíveis depois
        
        self.fabricante_input = QLineEdit()
        self.fabricante_input.setPlaceholderText("Ex: Fabricante Industrial Ltda")
        
        self.ano_fabricacao_input = QLineEdit()
        self.ano_fabricacao_input.setPlaceholderText("Ex: 2020")
        
        self.pressao_projeto_input = QLineEdit()
        self.pressao_projeto_input.setPlaceholderText("Ex: 10.5")
        
        self.pressao_trabalho_input = QLineEdit()
        self.pressao_trabalho_input.setPlaceholderText("Ex: 8.0")
        
        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("Ex: 100.0")
        
        self.fluido_input = QLineEdit()
        self.fluido_input.setPlaceholderText("Ex: Vapor d'água")
        
        # Adicionar campos ao formulário
        form_layout.addRow("Tag:", self.tag_input)
        form_layout.addRow("Categoria:", self.categoria_input)
        form_layout.addRow("Empresa:", self.empresa_input)
        form_layout.addRow("Fabricante:", self.fabricante_input)
        form_layout.addRow("Ano de Fabricação:", self.ano_fabricacao_input)
        form_layout.addRow("Pressão de Projeto (kgf/cm²):", self.pressao_projeto_input)
        form_layout.addRow("Pressão de Trabalho (kgf/cm²):", self.pressao_trabalho_input)
        form_layout.addRow("Volume (m³):", self.volume_input)
        form_layout.addRow("Fluido:", self.fluido_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
        # Carregar dados se for edição
        self.load_empresas()
        if self.equipment_data:
            self.load_equipment_data()
            
    def load_empresas(self):
        """Carrega as empresas no combobox"""
        try:
            # Assumindo que temos acesso ao controller através do parent
            if hasattr(self.parent(), 'auth_controller'):
                users = self.parent().auth_controller.get_all_users()
                empresas = []
                
                # Filtrar apenas as empresas (usuários tipo 'emp')
                for user in users:
                    if user.get('tipo_acesso') == 'emp' and user.get('nome'):
                        empresas.append(user.get('nome'))
                
                # Adicionar ao combobox
                self.empresa_input.clear()
                self.empresa_input.addItems(empresas)
        except Exception as e:
            print(f"Erro ao carregar empresas: {e}")
            
    def load_equipment_data(self):
        """Carrega os dados do equipamento para edição"""
        if not self.equipment_data:
            return
            
        self.tag_input.setText(self.equipment_data.get('tag', ''))
        
        # Selecionar a categoria correta
        categoria_idx = self.categoria_input.findText(self.equipment_data.get('categoria', ''))
        if categoria_idx >= 0:
            self.categoria_input.setCurrentIndex(categoria_idx)
            
        # Selecionar a empresa correta
        empresa_nome = self.equipment_data.get('empresa_nome', '')
        empresa_idx = self.empresa_input.findText(empresa_nome)
        if empresa_idx >= 0:
            self.empresa_input.setCurrentIndex(empresa_idx)
            
        self.fabricante_input.setText(self.equipment_data.get('fabricante', ''))
        self.ano_fabricacao_input.setText(str(self.equipment_data.get('ano_fabricacao', '')))
        self.pressao_projeto_input.setText(str(self.equipment_data.get('pressao_projeto', '')))
        self.pressao_trabalho_input.setText(str(self.equipment_data.get('pressao_trabalho', '')))
        self.volume_input.setText(str(self.equipment_data.get('volume', '')))
        self.fluido_input.setText(self.equipment_data.get('fluido', ''))
        
    def get_data(self):
        """Retorna os dados preenchidos no formulário"""
        return {
            'tag': self.tag_input.text().strip(),
            'categoria': self.categoria_input.currentText(),
            'empresa': self.empresa_input.currentText(),
            'fabricante': self.fabricante_input.text().strip(),
            'ano_fabricacao': self.ano_fabricacao_input.text().strip(),
            'pressao_projeto': self.pressao_projeto_input.text().strip(),
            'pressao_trabalho': self.pressao_trabalho_input.text().strip(),
            'volume': self.volume_input.text().strip(),
            'fluido': self.fluido_input.text().strip()
        }

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
            "data": data_str,
            "tipo": self.tipo_input.currentText(),
            "resultado": self.resultado_input.currentText(),
            "recomendacoes": self.recomendacoes_input.toPlainText().strip()
        }

class ReportModal(QDialog):
    """Modal para adicionar/editar relatórios"""
    
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setup_ui()
        
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
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        button_box.addWidget(self.save_btn)
        
        # Botão Cancelar
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(self.cancel_btn)
        
        layout.addLayout(button_box)
        
        # Aplica o tema
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
                QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                    border: 1px solid #2196F3;
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