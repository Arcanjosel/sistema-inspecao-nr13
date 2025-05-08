#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modal de detalhes da inspeção
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFormLayout, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QDate

logger = logging.getLogger(__name__)

class InspectionDetailsDialog(QDialog):
    """Diálogo para exibir detalhes de uma inspeção"""
    
    def __init__(self, parent=None, inspection_data=None, is_dark=False):
        """Inicializa o diálogo de detalhes"""
        super().__init__(parent)
        self.inspection_data = inspection_data
        self.is_dark = is_dark
        self.setWindowTitle(f"Detalhes da Inspeção #{inspection_data.get('id', '')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface de usuário"""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # === Seção de Equipamento ===
        equipment_group = QGroupBox("Dados do Equipamento")
        equipment_layout = QFormLayout()
        
        # Tag do equipamento
        equip_tag = f"{self.inspection_data.get('equipamento_tag', '')} - {self.inspection_data.get('equipamento_nome', '')}"
        equipment_layout.addRow(QLabel("<b>Tag:</b>"), QLabel(equip_tag))
        
        # Categoria
        equipment_layout.addRow(QLabel("<b>Categoria:</b>"), QLabel(self.inspection_data.get('equipamento_categoria', '')))
        
        # Tipo
        equipment_layout.addRow(QLabel("<b>Tipo:</b>"), QLabel(self.inspection_data.get('equipamento_tipo', '')))
        
        # Localização
        equipment_layout.addRow(QLabel("<b>Localização:</b>"), QLabel(self.inspection_data.get('equipamento_localizacao', '')))
        
        equipment_group.setLayout(equipment_layout)
        layout.addWidget(equipment_group)
        
        # === Seção de Inspeção ===
        inspection_group = QGroupBox("Dados da Inspeção")
        inspection_layout = QFormLayout()
        
        # Data da inspeção
        inspection_layout.addRow(QLabel("<b>Data:</b>"), QLabel(self.inspection_data.get('data_inspecao', '')))
        
        # Tipo de inspeção
        inspection_layout.addRow(QLabel("<b>Tipo:</b>"), QLabel(self.inspection_data.get('tipo_inspecao', '')))
        
        # Engenheiro responsável
        inspection_layout.addRow(QLabel("<b>Engenheiro:</b>"), QLabel(self.inspection_data.get('engenheiro_nome', '')))
        
        # Resultado
        resultado = self.inspection_data.get('resultado', '')
        resultado_label = QLabel(resultado)
        
        if resultado == 'Aprovado':
            resultado_label.setStyleSheet("color: #28a745; font-weight: bold;")
        elif resultado == 'Reprovado':
            resultado_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        else:
            resultado_label.setStyleSheet("color: #ffc107; font-weight: bold;")
            
        inspection_layout.addRow(QLabel("<b>Resultado:</b>"), resultado_label)
        
        inspection_group.setLayout(inspection_layout)
        layout.addWidget(inspection_group)
        
        # === Seção de Recomendações ===
        recommendations_group = QGroupBox("Recomendações")
        recommendations_layout = QVBoxLayout()
        
        recommendations_text = QTextEdit()
        recommendations_text.setReadOnly(True)
        recommendations_text.setText(self.inspection_data.get('recomendacoes', ''))
        recommendations_text.setMinimumHeight(100)
        
        recommendations_layout.addWidget(recommendations_text)
        recommendations_group.setLayout(recommendations_layout)
        layout.addWidget(recommendations_group)
        
        # === Botões ===
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Fechar")
        self.close_button.setStyleSheet("""
            background-color: #6c757d;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        """)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Aplica estilo dark se necessário
        if self.is_dark:
            self.setStyleSheet("""
                QDialog { background-color: #303030; color: #FFFFFF; }
                QLabel { color: #FFFFFF; }
                QTextEdit { background-color: #383838; color: #FFFFFF; border: 1px solid #505050; }
                QGroupBox { color: #FFFFFF; border: 1px solid #505050; }
            """) 