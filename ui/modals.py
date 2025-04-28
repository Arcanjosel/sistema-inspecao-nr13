#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janelas modais para formulários de cadastro
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
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
        self.tipo_input.addItems(["admin", "cliente"])
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

class EquipmentModal(BaseModal):
    """Janela modal para cadastro de equipamentos"""
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent, is_dark)
        self.setWindowTitle("Cadastrar Equipamento")
        self.setup_form()
        
    def setup_form(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Campos do formulário
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["caldeira", "vaso_pressao", "tubulacao"])
        self.tipo_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.tipo_input)
        
        self.empresa_input = QLineEdit()
        self.empresa_input.setPlaceholderText("Empresa")
        self.empresa_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Empresa:"))
        layout.addWidget(self.empresa_input)
        
        self.localizacao_input = QLineEdit()
        self.localizacao_input.setPlaceholderText("Localização")
        self.localizacao_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Localização:"))
        layout.addWidget(self.localizacao_input)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código do Projeto")
        self.codigo_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Código:"))
        layout.addWidget(self.codigo_input)
        
        self.pressao_input = QLineEdit()
        self.pressao_input.setPlaceholderText("Pressão Máxima")
        self.pressao_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Pressão:"))
        layout.addWidget(self.pressao_input)
        
        self.temperatura_input = QLineEdit()
        self.temperatura_input.setPlaceholderText("Temperatura Máxima")
        self.temperatura_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Temperatura:"))
        layout.addWidget(self.temperatura_input)
        
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
            "tipo": self.tipo_input.currentText(),
            "empresa": self.empresa_input.text().strip(),
            "localizacao": self.localizacao_input.text().strip(),
            "codigo": self.codigo_input.text().strip(),
            "pressao": self.pressao_input.text().strip(),
            "temperatura": self.temperatura_input.text().strip()
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
        self.equipamento_input = QComboBox()
        self.equipamento_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Equipamento:"))
        layout.addWidget(self.equipamento_input)
        
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Data:"))
        layout.addWidget(self.data_input)
        
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["periodica", "extraordinaria"])
        self.tipo_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.tipo_input)
        
        self.engenheiro_input = QLineEdit()
        self.engenheiro_input.setPlaceholderText("Engenheiro Responsável")
        self.engenheiro_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Engenheiro:"))
        layout.addWidget(self.engenheiro_input)
        
        self.resultado_input = QComboBox()
        self.resultado_input.addItems(["aprovado", "reprovado", "condicional"])
        self.resultado_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Resultado:"))
        layout.addWidget(self.resultado_input)
        
        self.recomendacoes_input = QTextEdit()
        self.recomendacoes_input.setPlaceholderText("Recomendações")
        layout.addWidget(QLabel("Recomendações:"))
        layout.addWidget(self.recomendacoes_input)
        
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
            "equipamento_id": int(self.equipamento_input.currentText().split(" - ")[0]),
            "data": self.data_input.date().toPyDate(),
            "tipo": self.tipo_input.currentText(),
            "engenheiro": self.engenheiro_input.text().strip(),
            "resultado": self.resultado_input.currentText(),
            "recomendacoes": self.recomendacoes_input.toPlainText().strip()
        }

class ReportModal(BaseModal):
    """Janela modal para cadastro de relatórios"""
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent, is_dark)
        self.setWindowTitle("Cadastrar Relatório")
        self.setup_form()
        
    def setup_form(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Campos do formulário
        self.inspecao_input = QComboBox()
        self.inspecao_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Inspeção:"))
        layout.addWidget(self.inspecao_input)
        
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Data:"))
        layout.addWidget(self.data_input)
        
        self.arquivo_input = QLineEdit()
        self.arquivo_input.setPlaceholderText("Link do Arquivo")
        self.arquivo_input.setMinimumHeight(36)
        layout.addWidget(QLabel("Arquivo:"))
        layout.addWidget(self.arquivo_input)
        
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setPlaceholderText("Observações")
        layout.addWidget(QLabel("Observações:"))
        layout.addWidget(self.observacoes_input)
        
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
            "inspecao_id": int(self.inspecao_input.currentText().split(" - ")[0]),
            "data": self.data_input.date().toPyDate(),
            "arquivo": self.arquivo_input.text().strip(),
            "observacoes": self.observacoes_input.toPlainText().strip()
        } 