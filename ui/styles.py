#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estilos compartilhados do sistema
"""

class Styles:
    @staticmethod
    def get_dark_theme():
        return """
            QMainWindow { 
                background-color: #181a1b; 
            }
            QWidget { 
                background-color: #181a1b; 
            }
            QLabel { 
                color: #f1f1f1; 
            }
            QLineEdit {
                background-color: #232629;
                color: #f1f1f1;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus { 
                border: 1.5px solid #007bff; 
            }
            QPushButton {
                background-color: #232629;
                color: #f1f1f1;
                border: 1px solid #444;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover { 
                background-color: #33373a; 
            }
            QPushButton:pressed {
                background-color: #2a2d30;
            }
            QTableWidget {
                background-color: #232629;
                color: #f1f1f1;
                border: 1px solid #444;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: #f1f1f1;
            }
            QHeaderView::section {
                background-color: #2a2d30;
                color: #f1f1f1;
                padding: 8px;
                border: 1px solid #444;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #232629;
            }
            QTabBar::tab {
                background-color: #2a2d30;
                color: #f1f1f1;
                padding: 8px 16px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
            }
            QTabBar::tab:hover {
                background-color: #33373a;
            }
            QComboBox {
                background-color: #232629;
                color: #f1f1f1;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #232629;
                color: #f1f1f1;
                border: 1px solid #444;
                selection-background-color: #007bff;
            }
            QMessageBox {
                background-color: #181a1b;
            }
            QMessageBox QLabel {
                color: #f1f1f1;
            }
            QMessageBox QPushButton {
                min-width: 100px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #33373a;
                border-radius: 4px;
            }
            QToolButton:pressed {
                background-color: #2a2d30;
            }
        """

    @staticmethod
    def get_light_theme():
        return """
            QMainWindow { 
                background-color: #f8f9fa; 
            }
            QWidget { 
                background-color: #f8f9fa; 
            }
            QLabel { 
                color: #212529; 
            }
            QLineEdit {
                background-color: #fff;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus { 
                border: 1.5px solid #007bff; 
            }
            QPushButton {
                background-color: #e9ecef;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover { 
                background-color: #dee2e6; 
            }
            QPushButton:pressed {
                background-color: #d1d5d8;
            }
            QTableWidget {
                background-color: #fff;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: #fff;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                color: #212529;
                padding: 8px;
                border: 1px solid #ced4da;
            }
            QTabWidget::pane {
                border: 1px solid #ced4da;
                background-color: #fff;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #212529;
                padding: 8px 16px;
                border: 1px solid #ced4da;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: #fff;
            }
            QTabBar::tab:hover {
                background-color: #dee2e6;
            }
            QComboBox {
                background-color: #fff;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #fff;
                color: #212529;
                border: 1px solid #ced4da;
                selection-background-color: #007bff;
            }
            QMessageBox {
                background-color: #f8f9fa;
            }
            QMessageBox QLabel {
                color: #212529;
            }
            QMessageBox QPushButton {
                min-width: 100px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #e9ecef;
                border-radius: 4px;
            }
            QToolButton:pressed {
                background-color: #dee2e6;
            }
        """ 