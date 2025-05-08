#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para geração de laudos técnicos NR-13
"""

import os
import logging
import traceback
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QPushButton,
    QMessageBox, QGroupBox, QScrollArea, QSpinBox, QDoubleSpinBox,
    QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QPixmap

from utils.pdf_generator import LaudoTecnicoPDF

# Configuração do logging
logger = logging.getLogger(__name__)

class LaudoWindow(QMainWindow):
    """Janela para gerar laudos técnicos NR-13"""
    
    def __init__(self, parent=None, inspection_data=None):
        super().__init__(parent)
        self.inspection_data = inspection_data
        self.setWindowTitle("Gerador de Laudos Técnicos - NR-13")
        self.setGeometry(100, 100, 800, 700)
        self.setup_ui()
        self.pdf_generator = LaudoTecnicoPDF()
        
        # Se recebeu dados de inspeção, preenche o formulário
        if self.inspection_data:
            self.preencher_com_dados_inspecao()
        
    def setup_ui(self):
        """Configuração da interface de usuário"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel("Gerador de Laudos Técnicos NR-13")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Área de rolagem para o formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Widget de conteúdo do scroll
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        
        # === Dados do Cliente ===
        client_group = QGroupBox("Dados do Cliente")
        client_layout = QFormLayout()
        scroll_layout.addWidget(client_group)
        client_group.setLayout(client_layout)
        
        # Campos para dados do cliente
        self.cliente_nome = QLineEdit()
        self.cliente_cnpj = QLineEdit()
        self.cliente_endereco = QLineEdit()
        self.cliente_cidade = QLineEdit()
        self.cliente_estado = QComboBox()
        
        # Adiciona estados brasileiros
        estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
                  "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
                  "SP", "SE", "TO"]
        self.cliente_estado.addItems(estados)
        
        # Adiciona campos ao layout
        client_layout.addRow("Nome/Razão Social:", self.cliente_nome)
        client_layout.addRow("CNPJ:", self.cliente_cnpj)
        client_layout.addRow("Endereço:", self.cliente_endereco)
        client_layout.addRow("Cidade:", self.cliente_cidade)
        client_layout.addRow("Estado:", self.cliente_estado)
        
        # === Dados do Equipamento ===
        equipment_group = QGroupBox("Dados do Equipamento")
        equipment_layout = QFormLayout()
        scroll_layout.addWidget(equipment_group)
        equipment_group.setLayout(equipment_layout)
        
        # Campos para dados do equipamento
        self.equip_tag = QLineEdit()
        self.equip_tipo = QComboBox()
        self.equip_tipo.addItems([
            "Vaso de Pressão", 
            "Caldeira", 
            "Tubulação", 
            "Tanque Metálico"
        ])
        
        self.equip_categoria = QComboBox()
        self.equip_categoria.addItems([
            "Categoria I", 
            "Categoria II", 
            "Categoria III", 
            "Categoria IV", 
            "Categoria V"
        ])
        
        self.equip_fabricante = QLineEdit()
        self.equip_ano = QSpinBox()
        self.equip_ano.setRange(1900, datetime.now().year)
        self.equip_ano.setValue(datetime.now().year)
        
        self.equip_pressao = QDoubleSpinBox()
        self.equip_pressao.setRange(0, 1000)
        self.equip_pressao.setSuffix(" kgf/cm²")
        self.equip_pressao.setDecimals(2)
        
        self.equip_volume = QDoubleSpinBox()
        self.equip_volume.setRange(0, 1000000)
        self.equip_volume.setSuffix(" L")
        
        # Adiciona campos ao layout
        equipment_layout.addRow("Tag/Identificação:", self.equip_tag)
        equipment_layout.addRow("Tipo de Equipamento:", self.equip_tipo)
        equipment_layout.addRow("Categoria:", self.equip_categoria)
        equipment_layout.addRow("Fabricante:", self.equip_fabricante)
        equipment_layout.addRow("Ano de Fabricação:", self.equip_ano)
        equipment_layout.addRow("Pressão Máxima:", self.equip_pressao)
        equipment_layout.addRow("Volume:", self.equip_volume)
        
        # === Dados da Inspeção ===
        inspection_group = QGroupBox("Dados da Inspeção")
        inspection_layout = QFormLayout()
        scroll_layout.addWidget(inspection_group)
        inspection_group.setLayout(inspection_layout)
        
        # Campos para dados da inspeção
        self.insp_data = QDateEdit()
        self.insp_data.setDate(QDate.currentDate())
        self.insp_data.setCalendarPopup(True)
        
        self.insp_tipo = QComboBox()
        self.insp_tipo.addItems([
            "Inspeção Inicial", 
            "Inspeção Periódica", 
            "Inspeção Extraordinária"
        ])
        
        self.insp_responsavel = QLineEdit()
        
        self.insp_resultado = QComboBox()
        self.insp_resultado.addItems([
            "Aprovado", 
            "Aprovado com Restrições", 
            "Reprovado"
        ])
        
        self.insp_proxima = QDateEdit()
        # Define a próxima inspeção para 1 ano após a data atual
        prox_data = QDate.currentDate().addYears(1)
        self.insp_proxima.setDate(prox_data)
        self.insp_proxima.setCalendarPopup(True)
        
        # Adiciona campos ao layout
        inspection_layout.addRow("Data da Inspeção:", self.insp_data)
        inspection_layout.addRow("Tipo de Inspeção:", self.insp_tipo)
        inspection_layout.addRow("Engenheiro Responsável:", self.insp_responsavel)
        inspection_layout.addRow("Resultado:", self.insp_resultado)
        inspection_layout.addRow("Próxima Inspeção:", self.insp_proxima)
        
        # === Ensaios Realizados ===
        self.ensaios_group = QGroupBox("Ensaios Realizados")
        ensaios_layout = QVBoxLayout()
        scroll_layout.addWidget(self.ensaios_group)
        self.ensaios_group.setLayout(ensaios_layout)
        
        # Checkbox para cada tipo de ensaio
        self.check_visual = QCheckBox("Exame Visual Externo")
        self.check_visual.setChecked(True)
        
        self.check_dimensional = QCheckBox("Medição de Espessura")
        self.check_dimensional.setChecked(True)
        
        self.check_liquido = QCheckBox("Líquido Penetrante")
        self.check_particula = QCheckBox("Partículas Magnéticas")
        self.check_ultrassom = QCheckBox("Ultrassom")
        self.check_radiografia = QCheckBox("Radiografia")
        self.check_pmtp = QCheckBox("PMTP (Pressão Máxima de Trabalho Permitida)")
        self.check_thi = QCheckBox("Teste Hidrostático")
        
        # Campo para ensaios adicionais
        self.ensaios_adicionais = QTextEdit()
        self.ensaios_adicionais.setPlaceholderText("Descreva aqui outros ensaios realizados...")
        self.ensaios_adicionais.setMaximumHeight(100)
        
        # Adiciona ao layout
        ensaios_layout.addWidget(self.check_visual)
        ensaios_layout.addWidget(self.check_dimensional)
        ensaios_layout.addWidget(self.check_liquido)
        ensaios_layout.addWidget(self.check_particula)
        ensaios_layout.addWidget(self.check_ultrassom)
        ensaios_layout.addWidget(self.check_radiografia)
        ensaios_layout.addWidget(self.check_pmtp)
        ensaios_layout.addWidget(self.check_thi)
        ensaios_layout.addWidget(QLabel("Ensaios Adicionais:"))
        ensaios_layout.addWidget(self.ensaios_adicionais)
        
        # === Campos textuais para informações detalhadas ===
        text_group = QGroupBox("Informações Detalhadas")
        text_layout = QVBoxLayout()
        scroll_layout.addWidget(text_group)
        text_group.setLayout(text_layout)
        
        # Não conformidades
        text_layout.addWidget(QLabel("Não Conformidades:"))
        self.nao_conformidades = QTextEdit()
        self.nao_conformidades.setPlaceholderText("Liste aqui as não conformidades encontradas...")
        text_layout.addWidget(self.nao_conformidades)
        
        # Recomendações
        text_layout.addWidget(QLabel("Recomendações:"))
        self.recomendacoes = QTextEdit()
        self.recomendacoes.setPlaceholderText("Liste aqui as recomendações para o equipamento...")
        text_layout.addWidget(self.recomendacoes)
        
        # Conclusão
        text_layout.addWidget(QLabel("Conclusão:"))
        self.conclusao = QTextEdit()
        self.conclusao.setPlaceholderText("Digite a conclusão do laudo técnico...")
        text_layout.addWidget(self.conclusao)
        
        # === Botões de ação ===
        button_layout = QHBoxLayout()
        scroll_layout.addLayout(button_layout)
        
        # Botão de limpar formulário
        self.btn_limpar = QPushButton("Limpar Formulário")
        self.btn_limpar.clicked.connect(self.limpar_formulario)
        button_layout.addWidget(self.btn_limpar)
        
        # Botão de gerar PDF
        self.btn_gerar_pdf = QPushButton("Gerar Laudo PDF")
        self.btn_gerar_pdf.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_gerar_pdf.clicked.connect(self.gerar_laudo_pdf)
        button_layout.addWidget(self.btn_gerar_pdf)
        
    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        try:
            # Limpa campos de texto
            for field in [self.cliente_nome, self.cliente_cnpj, self.cliente_endereco, 
                        self.cliente_cidade, self.equip_tag, self.equip_fabricante,
                        self.insp_responsavel]:
                field.clear()
                
            # Reseta campos de data
            self.insp_data.setDate(QDate.currentDate())
            self.insp_proxima.setDate(QDate.currentDate().addYears(1))
            
            # Reseta spinners
            self.equip_ano.setValue(datetime.now().year)
            self.equip_pressao.setValue(0)
            self.equip_volume.setValue(0)
            
            # Limpa campos de texto avançados
            for field in [self.ensaios_adicionais, self.nao_conformidades, 
                        self.recomendacoes, self.conclusao]:
                field.clear()
                
            # Desmarca checkboxes
            for check in [self.check_liquido, self.check_particula, self.check_ultrassom,
                        self.check_radiografia, self.check_pmtp, self.check_thi]:
                check.setChecked(False)
                
            # Mantém os visuais e dimensionais marcados por padrão
            self.check_visual.setChecked(True)
            self.check_dimensional.setChecked(True)
            
            # Reseta combos para primeira opção
            self.cliente_estado.setCurrentIndex(0)
            self.equip_tipo.setCurrentIndex(0)
            self.equip_categoria.setCurrentIndex(0)
            self.insp_tipo.setCurrentIndex(0)
            self.insp_resultado.setCurrentIndex(0)
            
            QMessageBox.information(self, "Formulário Limpo", "O formulário foi limpo com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao limpar formulário: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao limpar formulário: {str(e)}")
            
    def gerar_laudo_pdf(self):
        """Gera um laudo técnico em PDF com os dados do formulário"""
        try:
            # Verifica campos obrigatórios
            if not self.cliente_nome.text().strip():
                QMessageBox.warning(self, "Atenção", "O nome do cliente é obrigatório.")
                return
                
            if not self.equip_tag.text().strip():
                QMessageBox.warning(self, "Atenção", "A identificação do equipamento é obrigatória.")
                return
                
            if not self.insp_responsavel.text().strip():
                QMessageBox.warning(self, "Atenção", "O nome do engenheiro responsável é obrigatório.")
                return
            
            # Prepara os dados para o PDF
            dados = self._preparar_dados_laudo()
            
            # Gera o PDF
            caminho_saida = self.pdf_generator.gerar_laudo(dados)
            
            if caminho_saida:
                QMessageBox.information(
                    self, 
                    "Laudo Gerado", 
                    f"O laudo técnico foi gerado com sucesso!\nSalvo em: {caminho_saida}"
                )
                
                # Pergunta se deseja abrir o PDF
                resposta = QMessageBox.question(
                    self,
                    "Abrir PDF",
                    "Deseja abrir o arquivo PDF gerado?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if resposta == QMessageBox.Yes:
                    # Abre o arquivo usando o visualizador padrão do sistema
                    import platform
                    import subprocess
                    
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(('open', caminho_saida))
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(caminho_saida)
                    else:  # Linux e outros
                        subprocess.call(('xdg-open', caminho_saida))
        
        except Exception as e:
            logger.error(f"Erro ao gerar laudo PDF: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Erro", f"Erro ao gerar laudo PDF: {str(e)}")
    
    def _preparar_dados_laudo(self):
        """Prepara os dados do formulário para o PDF"""
        # Coleta os ensaios selecionados
        ensaios = []
        if self.check_visual.isChecked():
            ensaios.append("Exame Visual Externo")
        if self.check_dimensional.isChecked():
            ensaios.append("Medição de Espessura")
        if self.check_liquido.isChecked():
            ensaios.append("Líquido Penetrante")
        if self.check_particula.isChecked():
            ensaios.append("Partículas Magnéticas")
        if self.check_ultrassom.isChecked():
            ensaios.append("Ultrassom")
        if self.check_radiografia.isChecked():
            ensaios.append("Radiografia")
        if self.check_pmtp.isChecked():
            ensaios.append("PMTP (Pressão Máxima de Trabalho Permitida)")
        if self.check_thi.isChecked():
            ensaios.append("Teste Hidrostático")
            
        # Adiciona ensaios adicionais, se houver
        if self.ensaios_adicionais.toPlainText().strip():
            ensaios.append(self.ensaios_adicionais.toPlainText().strip())
            
        # Formata o texto de ensaios
        ensaios_texto = "- " + "\n- ".join(ensaios) if ensaios else "Nenhum ensaio registrado."
        
        # Prepara título automático
        titulo = f"Laudo Técnico - {self.equip_tipo.currentText()} - {self.equip_tag.text()}"
        
        # Monta o dicionário de dados
        return {
            'titulo': titulo,
            
            # Dados do cliente
            'cliente_nome': self.cliente_nome.text(),
            'cliente_cnpj': self.cliente_cnpj.text(),
            'cliente_endereco': self.cliente_endereco.text(),
            'cliente_cidade': self.cliente_cidade.text(),
            'cliente_estado': self.cliente_estado.currentText(),
            
            # Dados do equipamento
            'equipamento_tag': self.equip_tag.text(),
            'equipamento_tipo': self.equip_tipo.currentText(),
            'equipamento_categoria': self.equip_categoria.currentText(),
            'equipamento_fabricante': self.equip_fabricante.text(),
            'equipamento_ano': str(self.equip_ano.value()),
            'equipamento_pressao': str(self.equip_pressao.value()),
            'equipamento_volume': str(self.equip_volume.value()),
            
            # Dados da inspeção
            'inspecao_data': self.insp_data.date().toString("dd/MM/yyyy"),
            'inspecao_tipo': self.insp_tipo.currentText(),
            'inspecao_responsavel': self.insp_responsavel.text(),
            'inspecao_resultado': self.insp_resultado.currentText(),
            'inspecao_proxima': self.insp_proxima.date().toString("dd/MM/yyyy"),
            
            # Informações detalhadas
            'ensaios_realizados': ensaios_texto,
            'nao_conformidades': self.nao_conformidades.toPlainText() or "Nenhuma não conformidade encontrada.",
            'recomendacoes': self.recomendacoes.toPlainText() or "Sem recomendações adicionais.",
            'conclusao': self.conclusao.toPlainText() or f"Equipamento {self.insp_resultado.currentText().lower()}."
        }

    def preencher_com_dados_inspecao(self):
        """Preenche o formulário com dados de inspeção existente"""
        try:
            # Verifica se há dados de inspeção
            if not self.inspection_data:
                return
            
            logger.debug(f"Preenchendo formulário com dados: {self.inspection_data}")
            
            # Preenche dados do cliente
            if 'empresa_nome' in self.inspection_data:
                self.cliente_nome.setText(self.inspection_data.get('empresa_nome', ''))
                self.cliente_cnpj.setText(self.inspection_data.get('empresa_cnpj', ''))
                self.cliente_endereco.setText(self.inspection_data.get('empresa_endereco', ''))
                self.cliente_cidade.setText(self.inspection_data.get('empresa_cidade', ''))
                
                # Estado
                estado = self.inspection_data.get('empresa_estado', '')
                index = self.cliente_estado.findText(estado)
                if index >= 0:
                    self.cliente_estado.setCurrentIndex(index)
            
            # Preenche dados do equipamento
            if 'equipamento_tag' in self.inspection_data:
                self.equip_tag.setText(self.inspection_data.get('equipamento_tag', ''))
                
                # Categoria
                categoria = self.inspection_data.get('equipamento_categoria', '')
                index = self.equip_categoria.findText(categoria)
                if index >= 0:
                    self.equip_categoria.setCurrentIndex(index)
                    
                # Tipo
                tipo = self.inspection_data.get('equipamento_tipo', '')
                index = self.equip_tipo.findText(tipo)
                if index >= 0:
                    self.equip_tipo.setCurrentIndex(index)
                    
                self.equip_fabricante.setText(self.inspection_data.get('equipamento_fabricante', ''))
                
                # Ano de fabricação
                ano = self.inspection_data.get('equipamento_ano_fabricacao', '')
                if ano and str(ano).isdigit():
                    self.equip_ano.setValue(int(ano))
                    
                # Capacidade e pressão
                try:
                    # Para campos QLineEdit usa setText, para QSpinBox e QDoubleSpinBox usa setValue
                    if hasattr(self, 'equip_volume'):
                        volume = self.inspection_data.get('equipamento_capacidade', '')
                        if volume and isinstance(self.equip_volume, QSpinBox):
                            self.equip_volume.setValue(int(volume))
                        elif volume and isinstance(self.equip_volume, QDoubleSpinBox):
                            self.equip_volume.setValue(float(volume))
                        elif volume:
                            self.equip_volume.setText(str(volume))
                            
                    if hasattr(self, 'equip_pressao'):
                        pressao = self.inspection_data.get('equipamento_pressao_trabalho', '')
                        if pressao and isinstance(self.equip_pressao, QSpinBox):
                            self.equip_pressao.setValue(int(pressao))
                        elif pressao and isinstance(self.equip_pressao, QDoubleSpinBox):
                            self.equip_pressao.setValue(float(pressao))
                        elif pressao:
                            self.equip_pressao.setText(str(pressao))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao converter valor: {e}")
                
                # Localização
                if hasattr(self, 'equip_localizacao'):
                    self.equip_localizacao.setText(self.inspection_data.get('equipamento_localizacao', ''))
            
            # Preenche dados da inspeção
            if 'insp_data' in self.inspection_data:
                # Data da inspeção
                if isinstance(self.inspection_data['insp_data'], QDate):
                    self.insp_data.setDate(self.inspection_data['insp_data'])
                
                # Próxima inspeção
                if 'insp_proxima' in self.inspection_data and isinstance(self.inspection_data['insp_proxima'], QDate):
                    self.insp_proxima.setDate(self.inspection_data['insp_proxima'])
                
                # Responsável
                self.insp_responsavel.setText(self.inspection_data.get('insp_responsavel', ''))
                
                # Tipo de inspeção
                tipo_insp = self.inspection_data.get('insp_tipo', '')
                index = self.insp_tipo.findText(tipo_insp)
                if index >= 0:
                    self.insp_tipo.setCurrentIndex(index)
                
                # Resultado
                resultado = self.inspection_data.get('insp_resultado', '')
                index = self.insp_resultado.findText(resultado)
                if index >= 0:
                    self.insp_resultado.setCurrentIndex(index)
            
            # Ensaios e outros textos - verifica se cada campo existe antes de tentar preencher
            if hasattr(self, 'ensaios_realizados'):
                self.ensaios_realizados.setText(self.inspection_data.get('ensaios_realizados', ''))
            if hasattr(self, 'ensaios_adicionais'):
                self.ensaios_adicionais.setPlainText(self.inspection_data.get('ensaios_adicionais', ''))
            if hasattr(self, 'nao_conformidades'):
                self.nao_conformidades.setPlainText(self.inspection_data.get('nao_conformidades', ''))
            if hasattr(self, 'recomendacoes'):
                self.recomendacoes.setPlainText(self.inspection_data.get('recomendacoes', ''))
            if hasattr(self, 'conclusao'):
                self.conclusao.setPlainText(self.inspection_data.get('conclusao', ''))
            
            logger.debug("Formulário preenchido com dados da inspeção.")
            
        except Exception as e:
            logger.error(f"Erro ao preencher formulário com dados da inspeção: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.warning(self, "Erro", f"Erro ao preencher formulário: {str(e)}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = LaudoWindow()
    window.show()
    sys.exit(app.exec_()) 