import logging
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QDateEdit, QComboBox, QLineEdit, QFormLayout, QDialog,
                            QTextEdit, QHeaderView, QGroupBox, QDialogButtonBox,
                            QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QDate

from controllers.inspection_controller import InspectionController
from controllers.equipment_controller import EquipmentController
from controllers.engineer_controller import EngineerController
from ui.inspection_details import InspectionDetailsDialog

logger = logging.getLogger(__name__)

class InspectionModal(QDialog):
    """Modal para criação e edição de inspeções"""
    def __init__(self, parent=None, inspection_data=None, equipment_controller=None, 
                engineer_controller=None, is_dark=False):
        super().__init__(parent)
        self.inspection_data = inspection_data
        self.equipment_controller = equipment_controller
        self.engineer_controller = engineer_controller
        self.is_dark = is_dark
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do modal"""
        # Configuração da janela
        self.setWindowTitle("Inspeção" if not self.inspection_data else "Editar Inspeção")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Layout principal
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Campos do formulário
        # 1. Seleção de equipamento
        self.equipment_combo = QComboBox()
        self.load_equipment_options()
        form_layout.addRow("Equipamento:", self.equipment_combo)
        
        # 2. Seleção de engenheiro
        self.engineer_combo = QComboBox()
        self.load_engineer_options()
        form_layout.addRow("Engenheiro:", self.engineer_combo)
        
        # 3. Data da inspeção
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Data da Inspeção:", self.date_edit)
        
        # 4. Tipo de inspeção
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Inicial", "Periódica", "Extraordinária"])
        form_layout.addRow("Tipo de Inspeção:", self.type_combo)
        
        # 5. Resultado
        self.result_combo = QComboBox()
        self.result_combo.addItems(["Aprovado", "Reprovado", "Pendente"])
        form_layout.addRow("Resultado:", self.result_combo)
        
        # 6. Recomendações
        self.recommendations_edit = QTextEdit()
        form_layout.addRow("Recomendações:", self.recommendations_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        """)
        self.save_button.clicked.connect(self.save_inspection)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            background-color: #6c757d;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Preencher formulário se for edição
        if self.inspection_data:
            self.populate_form()
    
    def load_equipment_options(self):
        """Carrega a lista de equipamentos no combobox"""
        try:
            equipments = self.equipment_controller.get_all_equipment()
            self.equipment_combo.clear()
            
            for equip in equipments:
                # Usando o ID como valor e mostrando nome/tag como texto
                self.equipment_combo.addItem(
                    f"{equip['tag']} - {equip['nome']}", 
                    equip['id']
                )
                
            logger.debug(f"Carregados {len(equipments)} equipamentos no combobox")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
    
    def load_engineer_options(self):
        """Carrega a lista de engenheiros no combobox"""
        try:
            engineers = self.engineer_controller.get_all_engineers()
            self.engineer_combo.clear()
            
            for eng in engineers:
                # Usando o ID como valor e mostrando nome/crea como texto
                self.engineer_combo.addItem(
                    f"{eng['nome']} - CREA: {eng['crea']}", 
                    eng['id']
                )
                
            logger.debug(f"Carregados {len(engineers)} engenheiros no combobox")
        except Exception as e:
            logger.error(f"Erro ao carregar engenheiros: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar engenheiros: {str(e)}")
    
    def populate_form(self):
        """Preenche o formulário com os dados da inspeção existente"""
        if not self.inspection_data:
            return
            
        try:
            # Selecionar equipamento
            equipment_id = self.inspection_data['equipamento_id']
            for i in range(self.equipment_combo.count()):
                if self.equipment_combo.itemData(i) == equipment_id:
                    self.equipment_combo.setCurrentIndex(i)
                    break
            
            # Selecionar engenheiro
            engineer_id = self.inspection_data['engenheiro_id']
            for i in range(self.engineer_combo.count()):
                if self.engineer_combo.itemData(i) == engineer_id:
                    self.engineer_combo.setCurrentIndex(i)
                    break
            
            # Data da inspeção
            insp_date = QDate.fromString(self.inspection_data['data_inspecao'], "yyyy-MM-dd")
            self.date_edit.setDate(insp_date)
            
            # Tipo de inspeção
            tipo_index = self.type_combo.findText(self.inspection_data['tipo_inspecao'])
            if tipo_index >= 0:
                self.type_combo.setCurrentIndex(tipo_index)
            
            # Resultado
            result_index = self.result_combo.findText(self.inspection_data['resultado'])
            if result_index >= 0:
                self.result_combo.setCurrentIndex(result_index)
            
            # Recomendações
            if 'recomendacoes' in self.inspection_data and self.inspection_data['recomendacoes']:
                self.recommendations_edit.setText(self.inspection_data['recomendacoes'])
                
            logger.debug(f"Formulário preenchido com dados da inspeção {self.inspection_data.get('id')}")
        except Exception as e:
            logger.error(f"Erro ao preencher formulário: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao preencher formulário: {str(e)}")
    
    def get_form_data(self):
        """Recupera os dados do formulário"""
        data = {}
        
        try:
            # Equipamento
            equipment_idx = self.equipment_combo.currentIndex()
            if equipment_idx >= 0:
                data['equipamento_id'] = self.equipment_combo.itemData(equipment_idx)
            
            # Engenheiro
            engineer_idx = self.engineer_combo.currentIndex()
            if engineer_idx >= 0:
                data['engenheiro_id'] = self.engineer_combo.itemData(engineer_idx)
            
            # Data
            data['data_inspecao'] = self.date_edit.date().toString("yyyy-MM-dd")
            
            # Tipo
            data['tipo_inspecao'] = self.type_combo.currentText()
            
            # Resultado
            data['resultado'] = self.result_combo.currentText()
            
            # Recomendações
            data['recomendacoes'] = self.recommendations_edit.toPlainText()
            
            return data
        except Exception as e:
            logger.error(f"Erro ao obter dados do formulário: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao obter dados do formulário: {str(e)}")
            return None
    
    def save_inspection(self):
        """Salva os dados da inspeção"""
        data = self.get_form_data()
        if not data:
            return
        
        # Validar campos obrigatórios
        if not data.get('equipamento_id') or not data.get('engenheiro_id') or not data.get('data_inspecao'):
            QMessageBox.warning(self, "Validação", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        self.accept()


class FilterDialog(QDialog):
    """Diálogo para configurar filtros de inspeção"""
    
    def __init__(self, parent=None, equipment_controller=None, dark_mode=False):
        super().__init__(parent)
        self.equipment_controller = equipment_controller
        self.dark_mode = dark_mode
        self.setWindowTitle("Filtrar Inspeções")
        self.setMinimumWidth(450)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo de filtro"""
        layout = QVBoxLayout(self)
        
        # === Grupo de filtro por período === 
        date_group = QGroupBox("Período")
        date_layout = QFormLayout()
        
        # Data inicial e final
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        date_layout.addRow("De:", self.date_from)
        date_layout.addRow("Até:", self.date_to)
        
        # Checkbox para habilitar filtro por data
        self.use_date_filter = QCheckBox("Filtrar por data")
        date_layout.insertRow(0, self.use_date_filter)
        
        date_group.setLayout(date_layout)
        
        # === Grupo de filtro por equipamento ===
        equipment_group = QGroupBox("Equipamento")
        equipment_layout = QFormLayout()
        
        self.equipment_combo = QComboBox()
        self.equipment_combo.addItem("Todos", None)
        self.load_equipment_options()
        
        equipment_layout.addRow("Equipamento:", self.equipment_combo)
        equipment_group.setLayout(equipment_layout)
        
        # === Grupo de filtro por tipo de inspeção ===
        type_group = QGroupBox("Tipo de Inspeção")
        type_layout = QFormLayout()
        
        self.inspection_type_combo = QComboBox()
        self.inspection_type_combo.addItem("Todos", None)
        self.inspection_type_combo.addItem("Inicial", "Inicial")
        self.inspection_type_combo.addItem("Periódica", "Periódica")
        self.inspection_type_combo.addItem("Extraordinária", "Extraordinária")
        
        type_layout.addRow("Tipo:", self.inspection_type_combo)
        type_group.setLayout(type_layout)
        
        # === Grupo de filtro por resultado ===
        result_group = QGroupBox("Resultado")
        result_layout = QFormLayout()
        
        self.result_combo = QComboBox()
        self.result_combo.addItem("Todos", None)
        self.result_combo.addItem("Aprovado", "Aprovado")
        self.result_combo.addItem("Aprovado com restrições", "Aprovado com restrições")
        self.result_combo.addItem("Reprovado", "Reprovado")
        
        result_layout.addRow("Resultado:", self.result_combo)
        result_group.setLayout(result_layout)
        
        # Adiciona os grupos ao layout principal
        layout.addWidget(date_group)
        layout.addWidget(equipment_group)
        layout.addWidget(type_group)
        layout.addWidget(result_group)
        
        # Espaçador
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Botões
        button_box = QDialogButtonBox()
        
        self.btn_clear = QPushButton("Limpar Filtros")
        self.btn_clear.clicked.connect(self.clear_filters)
        button_box.addButton(self.btn_clear, QDialogButtonBox.ResetRole)
        
        button_box.addButton(QDialogButtonBox.Cancel)
        button_box.addButton(QDialogButtonBox.Apply)
        
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        
        layout.addWidget(button_box)
        
        # Aplica estilo se estiver em modo escuro
        if self.dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #2D2D30; color: #FFFFFF; }
                QGroupBox { color: #FFFFFF; }
                QLabel { color: #FFFFFF; }
                QCheckBox { color: #FFFFFF; }
            """)

    def load_equipment_options(self):
        """Carrega as opções de equipamentos no combo box"""
        if self.equipment_controller:
            equipments = self.equipment_controller.get_all_equipment()
            for equipment in equipments:
                display_text = f"{equipment['nome']} ({equipment['tag']})"
                self.equipment_combo.addItem(display_text, equipment['id'])
    
    def clear_filters(self):
        """Limpa todos os filtros configurados"""
        self.use_date_filter.setChecked(False)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_to.setDate(QDate.currentDate())
        self.equipment_combo.setCurrentIndex(0)
        self.inspection_type_combo.setCurrentIndex(0)
        self.result_combo.setCurrentIndex(0)
    
    def get_filters(self):
        """Retorna os filtros configurados"""
        filters = {}
        
        # Filtros de data
        if self.use_date_filter.isChecked():
            filters['date_from'] = self.date_from.date().toString("yyyy-MM-dd")
            filters['date_to'] = self.date_to.date().toString("yyyy-MM-dd")
        
        # Filtro de equipamento
        equipment_id = self.equipment_combo.currentData()
        if equipment_id is not None:
            filters['equipment_id'] = equipment_id
        
        # Filtro de tipo de inspeção
        inspection_type = self.inspection_type_combo.currentData()
        if inspection_type is not None:
            filters['tipo_inspecao'] = inspection_type
        
        # Filtro de resultado
        result = self.result_combo.currentData()
        if result is not None:
            filters['resultado'] = result
        
        return filters


class InspectionTab(QWidget):
    """Aba de gerenciamento de inspeções"""
    def __init__(self, db_models, is_dark=False):
        super().__init__()
        self.db_models = db_models
        self.is_dark = is_dark
        
        # Controladores
        self.inspection_controller = InspectionController(db_models)
        self.equipment_controller = EquipmentController(db_models)
        self.engineer_controller = EngineerController(db_models)
        
        # Ícones para os botões
        self.icons = {
            'add': """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>""",
            'edit': """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>""",
            'delete': """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>""",
            'filter': """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>""",
            'report': """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
        }
        
        self.init_ui()
        self.load_inspections()
        
    def init_ui(self):
        """Inicializa a interface da aba de inspeções"""
        # Layout principal
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Gestão de Inspeções")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        # Botão Adicionar
        self.add_button = QPushButton("Adicionar Inspeção")
        self.add_button.setIcon(self.create_icon_from_svg(self.icons['add']))
        self.add_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
        """)
        self.add_button.clicked.connect(self.add_inspection)
        
        # Botão Editar
        self.edit_button = QPushButton("Editar Inspeção")
        self.edit_button.setIcon(self.create_icon_from_svg(self.icons['edit']))
        self.edit_button.setStyleSheet("""
            background-color: #007bff;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
        """)
        self.edit_button.clicked.connect(self.edit_inspection)
        
        # Botão Excluir
        self.delete_button = QPushButton("Excluir Inspeção")
        self.delete_button.setIcon(self.create_icon_from_svg(self.icons['delete']))
        self.delete_button.setStyleSheet("""
            background-color: #dc3545;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
        """)
        self.delete_button.clicked.connect(self.delete_inspection)
        
        # Botão Filtrar
        self.filter_button = QPushButton("Filtrar")
        self.filter_button.setIcon(self.create_icon_from_svg(self.icons['filter']))
        self.filter_button.setStyleSheet("""
            background-color: #6c757d;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
        """)
        self.filter_button.clicked.connect(self.show_filter_dialog)
        
        # Botão Gerar Relatório
        self.report_button = QPushButton("Gerar Relatório")
        self.report_button.setIcon(self.create_icon_from_svg(self.icons['report']))
        self.report_button.setStyleSheet("""
            background-color: #17a2b8;
            color: white;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
        """)
        self.report_button.clicked.connect(self.generate_report)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.filter_button)
        button_layout.addWidget(self.report_button)
        
        layout.addLayout(button_layout)
        
        # Tabela de inspeções
        self.inspection_table = QTableWidget()
        self.inspection_table.setColumnCount(7)
        self.inspection_table.setHorizontalHeaderLabels(
            ["ID", "Equipamento", "Engenheiro", "Data", "Tipo", "Resultado", "Recomendações"]
        )
        self.inspection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inspection_table.setAlternatingRowColors(True)
        self.inspection_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inspection_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inspection_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Estilo da tabela
        if self.is_dark:
            self.inspection_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #3a3a3a;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    padding: 5px;
                    border: 1px solid #3a3a3a;
                }
            """)
        else:
            self.inspection_table.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #f2f2f2;
                }
                QHeaderView::section {
                    background-color: #e6e6e6;
                    padding: 5px;
                    border: 1px solid #d4d4d4;
                    font-weight: bold;
                }
            """)
        
        layout.addWidget(self.inspection_table)
        
        self.setLayout(layout)
    
    def create_icon_from_svg(self, svg_str):
        """Cria um QIcon a partir de uma string SVG"""
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtGui import QPixmap, QPainter
        
        renderer = QSvgRenderer()
        renderer.load(bytes(svg_str, 'utf-8'))
        
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def load_inspections(self):
        """Carrega as inspeções na tabela"""
        try:
            inspections = self.inspection_controller.get_all_inspections()
            
            # Limpar tabela
            self.inspection_table.setRowCount(0)
            
            for inspection in inspections:
                row_position = self.inspection_table.rowCount()
                self.inspection_table.insertRow(row_position)
                
                # ID
                self.inspection_table.setItem(row_position, 0, 
                                           QTableWidgetItem(str(inspection['id'])))
                
                # Equipamento
                equip_name = f"{inspection['equipamento_tag']} - {inspection['equipamento_nome']}"
                self.inspection_table.setItem(row_position, 1, 
                                           QTableWidgetItem(equip_name))
                
                # Engenheiro
                eng_name = f"{inspection['engenheiro_nome']}"
                self.inspection_table.setItem(row_position, 2, 
                                           QTableWidgetItem(eng_name))
                
                # Data
                date_str = inspection['data_inspecao']
                if isinstance(date_str, datetime.date):
                    date_str = date_str.strftime('%d/%m/%Y')
                self.inspection_table.setItem(row_position, 3, 
                                           QTableWidgetItem(date_str))
                
                # Tipo
                self.inspection_table.setItem(row_position, 4, 
                                           QTableWidgetItem(inspection['tipo_inspecao']))
                
                # Resultado com cor
                result_item = QTableWidgetItem(inspection['resultado'])
                if inspection['resultado'] == 'Aprovado':
                    result_item.setForeground(QColor('#28a745'))  # Verde
                elif inspection['resultado'] == 'Reprovado':
                    result_item.setForeground(QColor('#dc3545'))  # Vermelho
                else:
                    result_item.setForeground(QColor('#ffc107'))  # Amarelo
                self.inspection_table.setItem(row_position, 5, result_item)
                
                # Recomendações
                recomendacoes = inspection.get('recomendacoes', '')
                # Limitar o texto visível para não sobrecarregar a tabela
                recomendacoes_short = recomendacoes[:50] + '...' if len(recomendacoes) > 50 else recomendacoes
                self.inspection_table.setItem(row_position, 6, 
                                           QTableWidgetItem(recomendacoes_short))
            
            logger.debug(f"Carregadas {len(inspections)} inspeções na tabela")
        except Exception as e:
            logger.error(f"Erro ao carregar inspeções: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar inspeções: {str(e)}")
    
    def get_selected_inspection(self):
        """Retorna a inspeção selecionada ou None se nenhuma estiver selecionada"""
        selected_rows = self.inspection_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione uma inspeção.")
            return None
            
        row = selected_rows[0].row()
        inspection_id = int(self.inspection_table.item(row, 0).text())
        
        try:
            return self.inspection_controller.get_inspection_by_id(inspection_id)
        except Exception as e:
            logger.error(f"Erro ao obter inspeção selecionada: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao obter inspeção: {str(e)}")
            return None
    
    def add_inspection(self):
        """Abre o modal para adicionar uma nova inspeção"""
        dialog = InspectionModal(
            parent=self,
            equipment_controller=self.equipment_controller,
            engineer_controller=self.engineer_controller,
            is_dark=self.is_dark
        )
        
        if dialog.exec_():
            inspection_data = dialog.get_form_data()
            success, message = self.inspection_controller.create_inspection(inspection_data)
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_inspections()
            else:
                QMessageBox.warning(self, "Erro", message)
    
    def edit_inspection(self):
        """Abre o modal para editar uma inspeção existente"""
        inspection = self.get_selected_inspection()
        if not inspection:
            return
            
        dialog = InspectionModal(
            parent=self,
            inspection_data=inspection,
            equipment_controller=self.equipment_controller,
            engineer_controller=self.engineer_controller,
            is_dark=self.is_dark
        )
        
        if dialog.exec_():
            inspection_data = dialog.get_form_data()
            success, message = self.inspection_controller.update_inspection(
                inspection['id'], inspection_data
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_inspections()
            else:
                QMessageBox.warning(self, "Erro", message)
    
    def delete_inspection(self):
        """Exclui a inspeção selecionada"""
        inspection = self.get_selected_inspection()
        if not inspection:
            return
            
        # Confirmação
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a inspeção do equipamento {inspection['equipamento_tag']} realizada em {inspection['data_inspecao']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.inspection_controller.delete_inspection(inspection['id'])
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_inspections()
            else:
                QMessageBox.warning(self, "Erro", message)
    
    def show_filter_dialog(self):
        """Exibe diálogo para filtrar inspeções"""
        dialog = FilterDialog(
            parent=self,
            equipment_controller=self.equipment_controller,
            is_dark=self.is_dark
        )
        
        if dialog.exec_():
            filters = dialog.get_filters()
            try:
                # Carregar inspeções com filtros
                inspections = self.inspection_controller.get_filtered_inspections(filters)
                
                # Limpar tabela
                self.inspection_table.setRowCount(0)
                
                for inspection in inspections:
                    row_position = self.inspection_table.rowCount()
                    self.inspection_table.insertRow(row_position)
                    
                    # ID
                    self.inspection_table.setItem(row_position, 0, 
                                               QTableWidgetItem(str(inspection['id'])))
                    
                    # Equipamento
                    equip_name = f"{inspection['equipamento_tag']} - {inspection['equipamento_nome']}"
                    self.inspection_table.setItem(row_position, 1, 
                                               QTableWidgetItem(equip_name))
                    
                    # Engenheiro
                    eng_name = f"{inspection['engenheiro_nome']}"
                    self.inspection_table.setItem(row_position, 2, 
                                               QTableWidgetItem(eng_name))
                    
                    # Data
                    date_str = inspection['data_inspecao']
                    if isinstance(date_str, datetime.date):
                        date_str = date_str.strftime('%d/%m/%Y')
                    self.inspection_table.setItem(row_position, 3, 
                                               QTableWidgetItem(date_str))
                    
                    # Tipo
                    self.inspection_table.setItem(row_position, 4, 
                                               QTableWidgetItem(inspection['tipo_inspecao']))
                    
                    # Resultado com cor
                    result_item = QTableWidgetItem(inspection['resultado'])
                    if inspection['resultado'] == 'Aprovado':
                        result_item.setForeground(QColor('#28a745'))  # Verde
                    elif inspection['resultado'] == 'Reprovado':
                        result_item.setForeground(QColor('#dc3545'))  # Vermelho
                    else:
                        result_item.setForeground(QColor('#ffc107'))  # Amarelo
                    self.inspection_table.setItem(row_position, 5, result_item)
                    
                    # Recomendações
                    recomendacoes = inspection.get('recomendacoes', '')
                    # Limitar o texto visível para não sobrecarregar a tabela
                    recomendacoes_short = recomendacoes[:50] + '...' if len(recomendacoes) > 50 else recomendacoes
                    self.inspection_table.setItem(row_position, 6, 
                                               QTableWidgetItem(recomendacoes_short))
                
                QMessageBox.information(self, "Filtro Aplicado", f"Exibindo {len(inspections)} inspeções conforme filtros selecionados.")
                logger.debug(f"Filtro aplicado: {filters}")
            except Exception as e:
                logger.error(f"Erro ao aplicar filtros: {str(e)}")
                QMessageBox.warning(self, "Erro", f"Erro ao filtrar inspeções: {str(e)}")
    
    def generate_report(self):
        """Gera relatório das inspeções"""
        # TODO: Implementar geração de relatório
        QMessageBox.information(self, "Relatório", "Funcionalidade de relatório será implementada em breve.") 