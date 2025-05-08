#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar botão de geração de laudos
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer

class TesteButton(QMainWindow):
    """Janela para testar o botão"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste de Botão")
        self.setGeometry(100, 100, 400, 200)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Botão de teste com mesmo estilo
        report_button = QPushButton("Gerar Laudo Técnico")
        report_button.setIcon(self.create_icon_from_svg(self.get_report_svg()))
        report_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 8px 12px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 40px;
            font-size: 14px;
        """)
        report_button.clicked.connect(self.on_click)
        
        # Adiciona ao layout
        main_layout.addWidget(report_button)
    
    def create_icon_from_svg(self, svg_str):
        """Cria um QIcon a partir de uma string SVG"""
        renderer = QSvgRenderer()
        renderer.load(bytes(svg_str, 'utf-8'))
        
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def get_report_svg(self):
        """Retorna o SVG para o ícone de relatório"""
        return """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
    
    def on_click(self):
        """Ação ao clicar no botão"""
        print("Botão clicado!")

if __name__ == "__main__":
    # Inicializa a aplicação
    app = QApplication(sys.argv)
    
    # Cria e exibe a janela
    janela = TesteButton()
    janela.show()
    
    # Executa o loop de eventos
    sys.exit(app.exec_()) 