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
            
            logger.debug("Iniciando setup da UI")
            self.initUI()
            
            logger.info("ClientWindow inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar ClientWindow: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar janela: {str(e)}")
            raise

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
        
        # Adiciona o widget de abas ao layout principal
        layout.addWidget(self.tabs)
        
        # Botão de logout
        logout_container = QHBoxLayout()
        logout_container.addStretch()
        
        self.logout_button = QPushButton("Sair")
        self.logout_button.setFixedSize(100, 40)
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setStyleSheet("""
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
        """)
        
        logout_container.addWidget(self.logout_button)
        layout.addLayout(logout_container)

    def logout(self):
        """Emite sinal de logout."""
        logger.info("Logout solicitado pelo usuário")
        self.logout_requested.emit() 