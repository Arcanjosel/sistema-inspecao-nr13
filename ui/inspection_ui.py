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
            # Verificar se o controller está disponível
            if not self.equipment_controller:
                logger.error("Equipment controller não está disponível")
                self.equipment_combo.addItem("Nenhum equipamento disponível", 0)
                return
                
            # Tentar obter os equipamentos
            equipments = self.equipment_controller.get_all_equipment()
            self.equipment_combo.clear()
            
            if not equipments:
                logger.warning("Nenhum equipamento encontrado")
                self.equipment_combo.addItem("Nenhum equipamento cadastrado", 0)
                return
                
            # Adicionar cada equipamento ao combobox
            for equip in equipments:
                # Usar .get() com valores padrão
                equip_id = equip.get('id', 0)
                equip_tag = equip.get('tag', 'Sem tag')
                equip_nome = equip.get('nome', '')
                
                # Criar o texto de exibição
                if equip_nome:
                    display_text = f"{equip_nome} ({equip_tag})"
                else:
                    display_text = equip_tag
                
                # Adicionar ao combobox
                self.equipment_combo.addItem(display_text, equip_id)
                
            logger.debug(f"Carregados {len(equipments)} equipamentos no combobox")
            
            # Se não há equipamentos, adicionar um item padrão
            if self.equipment_combo.count() == 0:
                self.equipment_combo.addItem("Nenhum equipamento disponível", 0)
                
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos: {str(e)}")
            # Em caso de erro, limpar e adicionar um item padrão
            self.equipment_combo.clear()
            self.equipment_combo.addItem("Erro ao carregar equipamentos", 0)
            QMessageBox.warning(self, "Erro", f"Erro ao carregar equipamentos: {str(e)}")
    
    def load_engineer_options(self):
        """Carrega a lista de engenheiros no combobox"""
        try:
            # Verificar se o controller está disponível
            if not self.engineer_controller:
                logger.error("Engineer controller não está disponível")
                self.engineer_combo.addItem("Nenhum engenheiro disponível", 0)
                return
                
            # Tentar obter os engenheiros
            engineers = self.engineer_controller.get_all_engineers()
            self.engineer_combo.clear()
            
            if not engineers:
                logger.warning("Nenhum engenheiro encontrado")
                self.engineer_combo.addItem("Nenhum engenheiro cadastrado", 0)
                return
                
            # Adicionar cada engenheiro ao combobox
            for eng in engineers:
                # Obter campos com valores padrão se não existirem
                eng_id = eng.get('id', 0)
                eng_nome = eng.get('nome', 'Sem nome')
                eng_crea = eng.get('crea', 'N/A')
                
                # Criar o texto de exibição
                display_text = f"{eng_nome}"
                if eng_crea and eng_crea != 'N/A':
                    display_text += f" - CREA: {eng_crea}"
                
                # Adicionar ao combobox
                self.engineer_combo.addItem(display_text, eng_id)
                
            logger.debug(f"Carregados {len(engineers)} engenheiros no combobox")
            
            # Se não há engenheiros, adicionar um item padrão
            if self.engineer_combo.count() == 0:
                self.engineer_combo.addItem("Nenhum engenheiro disponível", 0)
                
        except Exception as e:
            logger.error(f"Erro ao carregar engenheiros: {str(e)}")
            # Em caso de erro, limpar e adicionar um item padrão
            self.engineer_combo.clear()
            self.engineer_combo.addItem("Erro ao carregar engenheiros", 0)
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
        """Carrega a lista de equipamentos no combobox"""
        try:
            equipments = self.equipment_controller.get_all_equipment()
            
            for equipment in equipments:
                # Usar .get() com valores padrão
                equip_id = equipment.get('id', 0)
                equip_tag = equipment.get('tag', 'Sem tag')
                equip_nome = equipment.get('nome', '')
                
                # Criar texto de exibição adequado
                if equip_nome:
                    display_text = f"{equip_nome} ({equip_tag})"
                else:
                    display_text = equip_tag
                    
                self.equipment_combo.addItem(display_text, equip_id)
                
            logger.debug(f"Carregados {len(equipments)} equipamentos no filtro")
        except Exception as e:
            logger.error(f"Erro ao carregar equipamentos no filtro: {str(e)}")
            # Adicionar item padrão em caso de erro
            self.equipment_combo.addItem("Erro ao carregar equipamentos", None)
    
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
    """Aba de gerenciamento de inspeções técnicas"""
    
    def __init__(self, parent=None, auth_controller=None, equipment_controller=None, inspection_controller=None):
        super().__init__(parent)
        self.parent = parent
        self.auth_controller = auth_controller
        self.equipment_controller = equipment_controller
        self.inspection_controller = inspection_controller
        self.is_dark = True  # Por padrão usa tema escuro
        
        # Adicionar controller de engenheiros
        from controllers.auth_controller import AuthController
        if self.auth_controller is None:
            self.auth_controller = AuthController()
            
        # Se o engineer_controller não tiver o método get_all_engineers, adiciona-o dinamicamente
        self.engineer_controller = self.auth_controller  # Usa o mesmo controller para buscar engenheiros
        
        # Verifica se o método get_all_engineers existe e caso não exista, adiciona-o
        if not hasattr(self.engineer_controller, 'get_all_engineers') or not callable(getattr(self.engineer_controller, 'get_all_engineers', None)):
            logger.debug("Adicionando método get_all_engineers ao engineer_controller")
            self.engineer_controller.get_all_engineers = self.get_engineers_from_auth
            
        # Carrega ícones SVG
        self.icons = {
            'add': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M11 11V5h2v6h6v2h-6v6h-2v-6H5v-2z" fill="white"/></svg>',
            'edit': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M15.728 9.686l-1.414-1.414L5 17.586V19h1.414l9.314-9.314zm1.414-1.414l1.414-1.414-1.414-1.414-1.414 1.414 1.414 1.414zM7.242 21H3v-4.243L16.435 3.322a1 1 0 0 1 1.414 0l2.829 2.829a1 1 0 0 1 0 1.414L7.243 21h-.001z" fill="white"/></svg>',
            'delete': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M7 4V2h10v2h5v2h-2v15a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6H2V4h5zM6 6v14h12V6H6zm3 3h2v8H9V9zm4 0h2v8h-2V9z" fill="white"/></svg>',
            'filter': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M14 14v6l-4 2v-8L4 5V3h16v2l-6 9zM6.404 5L12 13.394 17.596 5H6.404z" fill="white"/></svg>',
            'report': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M20 22H4a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1zm-1-2V4H5v16h14zM8 7h8v2H8V7zm0 4h8v2H8v-2zm0 4h8v2H8v-2z" fill="white"/></svg>',
        }
        
        self.init_ui()
        self.load_inspections()
        
    def init_ui(self):
        """Inicializa a interface da aba de inspeções"""
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Reduzir margens
        
        # Botões de ação secundários
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
        self.filter_button = QPushButton("Filtrar Inspeções")
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
        
        # Adiciona os botões ao layout na ordem desejada
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.filter_button)
        
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
        
        # Layout para o botão principal de Gerar Laudo - Movido para depois da tabela conforme solicitado
        laudo_layout = QHBoxLayout()
        
        # Botão Gerar Laudo Técnico
        self.report_button = QPushButton("GERAR LAUDO TÉCNICO")
        self.report_button.setIcon(self.create_icon_from_svg(self.icons['report']))
        self.report_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 6px 12px;
            font-weight: bold;
            border-radius: 4px;
            min-height: 36px;
            min-width: 200px;
            max-width: 250px;
            font-size: 13px;
        """)
        self.report_button.clicked.connect(self.generate_report)
        
        laudo_layout.addStretch()
        laudo_layout.addWidget(self.report_button)
        laudo_layout.addStretch()
        
        layout.addLayout(laudo_layout)
        
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
            # Limpar tabela
            self.inspection_table.setRowCount(0)
            
            # Definir cabeçalhos das colunas
            # Alterado para ajustar à nova estrutura de dados
            self.inspection_table.setColumnCount(7)
            self.inspection_table.setHorizontalHeaderLabels([
                "ID", "Equipamento", "Engenheiro", "Data", "Tipo", "Resultado", "Recomendações"
            ])
            
            # Buscar todas as inspeções
            inspections = self.inspection_controller.get_all_inspections()
            
            for inspection in inspections:
                row_position = self.inspection_table.rowCount()
                self.inspection_table.insertRow(row_position)
                
                # ID
                id_item = QTableWidgetItem(str(inspection['id']))
                id_item.setData(Qt.UserRole, inspection['id'])  # Armazenar ID como dado do objeto
                self.inspection_table.setItem(row_position, 0, id_item)
                
                # Equipamento
                equip_name = f"{inspection['equipamento_tag']} - {inspection['equipamento_nome']}" if 'equipamento_nome' in inspection else inspection['equipamento_tag']
                self.inspection_table.setItem(row_position, 1, QTableWidgetItem(equip_name))
                
                # Engenheiro
                eng_name = f"{inspection['engenheiro_nome']}" if 'engenheiro_nome' in inspection else "Engenheiro"
                self.inspection_table.setItem(row_position, 2, QTableWidgetItem(eng_name))
                
                # Data
                date_str = inspection['data_inspecao']
                if isinstance(date_str, datetime.date):
                    date_str = date_str.strftime('%d/%m/%Y')
                self.inspection_table.setItem(row_position, 3, QTableWidgetItem(date_str))
                
                # Tipo
                self.inspection_table.setItem(row_position, 4, QTableWidgetItem(inspection['tipo_inspecao']))
                
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
                self.inspection_table.setItem(row_position, 6, QTableWidgetItem(recomendacoes_short))
            
            logger.debug(f"Carregadas {len(inspections)} inspeções")
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
        
        # Obter o ID da inspeção a partir de UserRole no primeiro item da linha
        item = self.inspection_table.item(row, 0)
        if not item:
            QMessageBox.warning(self, "Erro", "Não foi possível identificar a inspeção selecionada.")
            return None
            
        inspection_id = item.data(Qt.UserRole)
        if not inspection_id:
            # Tentar obter o ID a partir do texto como fallback
            try:
                inspection_id = int(item.text())
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Erro", "ID da inspeção não encontrado.")
                return None
        
        try:
            return self.inspection_controller.get_inspection_by_id(inspection_id)
        except Exception as e:
            logger.error(f"Erro ao obter inspeção selecionada: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao obter inspeção: {str(e)}")
            return None
    
    def add_inspection(self):
        """Abre o modal para adicionar uma nova inspeção"""
        try:
            logger.debug("Iniciando criação de nova inspeção")
            
            # Verificar se os controllers estão disponíveis
            if not self.equipment_controller:
                logger.error("EquipmentController não está disponível")
                QMessageBox.warning(self, "Erro", "EquipmentController não inicializado corretamente.")
                return
                
            if not hasattr(self, 'engineer_controller') or not self.engineer_controller:
                logger.error("EngineerController não está disponível")
                
                # Se não tiver o engineer_controller, usar o auth_controller
                if self.auth_controller:
                    logger.debug("Usando auth_controller como engineer_controller")
                    self.engineer_controller = self.auth_controller
                    
                    # Adicionar método necessário se não existir
                    if not hasattr(self.engineer_controller, 'get_all_engineers'):
                        logger.debug("Adicionando método get_all_engineers ao controller")
                        self.engineer_controller.get_all_engineers = self.get_engineers_from_auth
                else:
                    QMessageBox.warning(self, "Erro", "Controller de engenheiros não inicializado.")
                    return
                
            # Verificar se há engenheiros cadastrados
            try:
                engineers = self.engineer_controller.get_all_engineers()
                logger.debug(f"Encontrados {len(engineers) if engineers else 0} engenheiros")
                if not engineers:
                    logger.warning("Nenhum engenheiro encontrado para criar inspeção")
                    QMessageBox.warning(self, "Atenção", "Não há engenheiros cadastrados. Cadastre pelo menos um engenheiro antes.")
                    return
            except Exception as e:
                logger.error(f"Erro ao tentar obter engenheiros: {str(e)}")
                QMessageBox.warning(self, "Erro", f"Não foi possível obter a lista de engenheiros: {str(e)}")
                return
                
            # Verificar se há equipamentos cadastrados
            try:
                equipments = self.equipment_controller.get_all_equipment()
                logger.debug(f"Encontrados {len(equipments) if equipments else 0} equipamentos")
                if not equipments:
                    logger.warning("Nenhum equipamento encontrado para criar inspeção")
                    QMessageBox.warning(self, "Atenção", "Não há equipamentos cadastrados. Cadastre pelo menos um equipamento antes.")
                    return
            except Exception as e:
                logger.error(f"Erro ao tentar obter equipamentos: {str(e)}")
                QMessageBox.warning(self, "Erro", f"Não foi possível obter a lista de equipamentos: {str(e)}")
                return
                
            logger.debug(f"Criando modal com controllers: equipment={self.equipment_controller}, engineer={self.engineer_controller}")
            
            # Criar o modal de inspeção
            dialog = InspectionModal(
                parent=self,
                equipment_controller=self.equipment_controller,
                engineer_controller=self.engineer_controller,
                is_dark=self.is_dark
            )
            
            # Exibir o modal
            logger.debug("Exibindo modal de inspeção")
            if dialog.exec_():
                # Obter os dados do formulário
                inspection_data = dialog.get_form_data()
                logger.debug(f"Dados coletados do formulário: {inspection_data}")
                
                # Criar a inspeção no banco de dados
                success, message = self.inspection_controller.create_inspection(inspection_data)
                
                if success:
                    logger.info(f"Inspeção criada com sucesso: {message}")
                    QMessageBox.information(self, "Sucesso", message)
                    self.load_inspections()
                else:
                    logger.error(f"Erro ao criar inspeção: {message}")
                    QMessageBox.warning(self, "Erro", message)
        except Exception as e:
            logger.error(f"Exceção ao criar inspeção: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao criar inspeção: {str(e)}")
    
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
            dark_mode=self.is_dark
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
        """Gera laudo técnico a partir da inspeção selecionada"""
        inspection = self.get_selected_inspection()
        if not inspection:
            return
            
        try:
            # Converte a data de string para objeto QDate
            from PyQt5.QtCore import QDate
            
            # Verificar quais campos estão disponíveis na inspeção
            logger.debug(f"Campos disponíveis na inspeção: {', '.join(inspection.keys())}")
            
            # Verificar e tratar a data da inspeção
            data_inspecao = None
            if 'data_inspecao' in inspection:
                data_inspecao = inspection['data_inspecao']
            elif 'data' in inspection:
                data_inspecao = inspection['data']
            elif 'data_inspetoria' in inspection:
                data_inspecao = inspection['data_inspetoria']
            elif 'dt_inspecao' in inspection:
                data_inspecao = inspection['dt_inspecao']
            else:
                # Se não encontrou a data, usa a data atual
                logger.warning("Data da inspeção não encontrada, usando data atual")
                data_inspecao = QDate.currentDate().toString("yyyy-MM-dd")
            
            # Converter a data para QDate
            if isinstance(data_inspecao, str):
                insp_date = QDate.fromString(data_inspecao, "yyyy-MM-dd")
            elif isinstance(data_inspecao, datetime.date) or isinstance(data_inspecao, datetime.datetime):
                insp_date = QDate(data_inspecao.year, data_inspecao.month, data_inspecao.day)
            else:
                insp_date = QDate.currentDate()
            
            # Calcula a data da próxima inspeção (1 ano após)
            proxima_date = insp_date.addYears(1)
            
            # Busca dados do equipamento
            equipamento = self.equipment_controller.get_equipment_by_id(inspection['equipamento_id'])
            if not equipamento:
                QMessageBox.warning(self, "Erro", "Não foi possível encontrar os dados do equipamento.")
                return
                
            # Busca dados do engenheiro
            engenheiro = None
            try:
                # Tenta obter o engenheiro pelo controller
                if hasattr(self.engineer_controller, 'get_engineer_by_id'):
                    engenheiro = self.engineer_controller.get_engineer_by_id(inspection['engenheiro_id'])
                else:
                    # Se o método não existir, cria um engenheiro a partir dos dados da inspeção
                    logger.warning("Método get_engineer_by_id não encontrado. Criando dados do engenheiro a partir da inspeção.")
                    engenheiro = {
                        'id': inspection['engenheiro_id'],
                        'nome': inspection.get('engenheiro_nome', "Engenheiro"),
                        'crea': inspection.get('engenheiro_crea', ""),
                        'tipo': 'engenheiro'
                    }
            except Exception as e:
                logger.error(f"Erro ao buscar dados do engenheiro: {str(e)}")
                # Em caso de erro, cria um engenheiro padrão
                engenheiro = {
                    'id': inspection.get('engenheiro_id', 0),
                    'nome': inspection.get('engenheiro_nome', "Engenheiro"),
                    'crea': inspection.get('engenheiro_crea', ""),
                    'tipo': 'engenheiro'
                }
                
            if not engenheiro:
                QMessageBox.warning(self, "Erro", "Não foi possível encontrar os dados do engenheiro.")
                return
            
            # Prepara os dados para o formulário do laudo
            laudo_data = {
                'insp_id': inspection['id'],
                'insp_data': insp_date,
                'insp_tipo': inspection.get('tipo_inspecao', 'Periódica'),
                'insp_responsavel': engenheiro['nome'],
                'insp_resultado': inspection.get('resultado', 'Pendente'),
                'insp_proxima': proxima_date,
                'ensaios_realizados': "Exame Visual Externo, Medição de Espessura",  # Padrão
                'ensaios_adicionais': "",
                'nao_conformidades': "",
                'recomendacoes': inspection.get('recomendacoes', ""),
                'conclusao': f"Inspeção realizada em {data_inspecao} com resultado: {inspection.get('resultado', 'Pendente')}.",
                
                # Dados do equipamento
                'equipamento_id': equipamento['id'],
                'equipamento_tag': equipamento['tag'],
                'equipamento_nome': equipamento.get('nome', ''),
                'equipamento_categoria': equipamento.get('categoria', ''),
                'equipamento_tipo': equipamento.get('tipo', ''),
                'equipamento_localizacao': equipamento.get('localizacao', ''),
                'equipamento_fabricante': equipamento.get('fabricante', ''),
                'equipamento_ano_fabricacao': equipamento.get('ano_fabricacao', ''),
                'equipamento_capacidade': equipamento.get('capacidade', ''),
                'equipamento_pressao_trabalho': equipamento.get('pressao_trabalho', ''),
                
                # Dados da empresa
                'empresa_nome': equipamento.get('cliente_nome', ''),
                'empresa_cnpj': equipamento.get('cliente_cnpj', ''),
                'empresa_endereco': equipamento.get('cliente_endereco', ''),
                'empresa_cidade': equipamento.get('cliente_cidade', ''),
                'empresa_estado': equipamento.get('cliente_estado', ''),
            }
            
            # Importa e abre a janela de geração de laudos
            from ui.laudo_window import LaudoWindow
            self.laudo_window = LaudoWindow(self, laudo_data)
            self.laudo_window.show()
            
            logger.info(f"Gerador de laudo aberto para inspeção ID: {inspection['id']}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar laudo técnico: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao gerar laudo técnico: {str(e)}")

    def get_engineers_from_auth(self):
        """Retorna uma lista de engenheiros a partir dos usuários do auth_controller que têm o tipo 'eng'."""
        try:
            engineers = []
            logger.debug("Buscando engenheiros no auth_controller")
            users = self.auth_controller.get_all_users()
            logger.debug(f"Encontrados {len(users)} usuários no total")
            
            for user in users:
                # Verifica se é um engenheiro (pode estar em 'tipo_acesso' ou 'tipo')
                user_type = user.get('tipo_acesso', user.get('tipo', ''))
                if user_type == 'eng':
                    # Cria dict do engenheiro com valores padrão para campos não existentes
                    engineer = {
                        'id': user.get('id', 0),
                        'nome': user.get('nome', 'Engenheiro'),
                        'crea': user.get('crea', 'N/A'),  # Usa N/A se não tiver CREA
                        'tipo': 'engenheiro'
                    }
                    engineers.append(engineer)
                    logger.debug(f"Adicionado engenheiro: {engineer['nome']}")
            
            logger.debug(f"Retornando {len(engineers)} engenheiros")
            return engineers
        except Exception as e:
            logger.error(f"Erro ao buscar engenheiros: {str(e)}")
            return [] 