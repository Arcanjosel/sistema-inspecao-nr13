#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para geração de laudos técnicos em PDF conforme NR-13
"""

import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# Configuração do logging
logger = logging.getLogger(__name__)

class LaudoTecnicoPDF:
    """Classe para geração de laudos técnicos NR-13 em PDF"""
    
    def __init__(self):
        """Inicializa o gerador de PDF"""
        self.styles = getSampleStyleSheet()
        # Adiciona estilo personalizado para títulos
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=1,  # Centralizado
            spaceAfter=0.5*cm
        ))
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=0.3*cm
        ))
        # Estilo para campos do formulário
        self.styles.add(ParagraphStyle(
            name='Campo',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=0.5*cm
        ))
        
    def gerar_laudo(self, dados, caminho_saida=None):
        """
        Gera um laudo técnico em PDF.
        
        Args:
            dados (dict): Dicionário com os dados do laudo
            caminho_saida (str, optional): Caminho onde salvar o PDF. Se None, abre diálogo
                                           para o usuário escolher.
        
        Returns:
            str: Caminho do arquivo gerado ou None se falhou
        """
        try:
            # Se não foi informado caminho de saída, solicita ao usuário
            if not caminho_saida:
                caminho_saida, _ = QFileDialog.getSaveFileName(
                    None,
                    "Salvar Laudo Técnico",
                    f"Laudo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "Arquivos PDF (*.pdf)"
                )
                if not caminho_saida:
                    return None  # Usuário cancelou
            
            # Se não termina com .pdf, adiciona a extensão
            if not caminho_saida.lower().endswith('.pdf'):
                caminho_saida += '.pdf'
            
            # Cria o documento
            doc = SimpleDocTemplate(
                caminho_saida,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Conteúdo do documento
            conteudo = []
            
            # Adiciona o título do documento
            titulo = dados.get('titulo', 'Laudo Técnico de Inspeção - NR-13')
            conteudo.append(Paragraph(titulo, self.styles['TituloPrincipal']))
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Adiciona as informações do equipamento
            conteudo.append(Paragraph("Dados do Equipamento", self.styles['Subtitulo']))
            
            # Tabela com dados do equipamento
            dados_equip = [
                ["Tag:", dados.get('equipamento_tag', '')],
                ["Tipo:", dados.get('equipamento_tipo', '')],
                ["Categoria:", dados.get('equipamento_categoria', '')],
                ["Fabricante:", dados.get('equipamento_fabricante', '')],
                ["Ano de Fabricação:", dados.get('equipamento_ano', '')],
                ["Pressão Máxima:", f"{dados.get('equipamento_pressao', '')} kgf/cm²"],
                ["Volume:", f"{dados.get('equipamento_volume', '')} L"]
            ]
            
            t = Table(dados_equip, colWidths=[4*cm, 12*cm])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            conteudo.append(t)
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Dados da inspeção
            conteudo.append(Paragraph("Dados da Inspeção", self.styles['Subtitulo']))
            
            dados_inspecao = [
                ["Data da Inspeção:", dados.get('inspecao_data', '')],
                ["Tipo de Inspeção:", dados.get('inspecao_tipo', '')],
                ["Engenheiro Responsável:", dados.get('inspecao_responsavel', '')],
                ["Resultado:", dados.get('inspecao_resultado', '')],
                ["Próxima Inspeção:", dados.get('inspecao_proxima', '')]
            ]
            
            t = Table(dados_inspecao, colWidths=[4*cm, 12*cm])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            conteudo.append(t)
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Descrição dos ensaios realizados
            conteudo.append(Paragraph("Ensaios Realizados", self.styles['Subtitulo']))
            ensaios = dados.get('ensaios_realizados', 'Nenhum ensaio registrado.')
            conteudo.append(Paragraph(ensaios, self.styles['Normal']))
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Descrição das não conformidades
            conteudo.append(Paragraph("Não Conformidades", self.styles['Subtitulo']))
            nao_conformidades = dados.get('nao_conformidades', 'Nenhuma não conformidade encontrada.')
            conteudo.append(Paragraph(nao_conformidades, self.styles['Normal']))
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Recomendações
            conteudo.append(Paragraph("Recomendações", self.styles['Subtitulo']))
            recomendacoes = dados.get('recomendacoes', 'Nenhuma recomendação.')
            conteudo.append(Paragraph(recomendacoes, self.styles['Normal']))
            conteudo.append(Spacer(1, 0.5*cm))
            
            # Conclusão
            conteudo.append(Paragraph("Conclusão", self.styles['Subtitulo']))
            conclusao = dados.get('conclusao', 'Sem conclusão registrada.')
            conteudo.append(Paragraph(conclusao, self.styles['Normal']))
            conteudo.append(Spacer(1, 1*cm))
            
            # Data e assinatura
            data_atual = datetime.now().strftime("%d/%m/%Y")
            data_texto = f"Documento gerado em {data_atual}"
            conteudo.append(Paragraph(data_texto, self.styles['Normal']))
            
            # Constrói o documento
            doc.build(conteudo)
            
            logger.info(f"Laudo técnico gerado com sucesso: {caminho_saida}")
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao gerar laudo técnico: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.critical(None, "Erro", f"Erro ao gerar laudo técnico: {str(e)}")
            return None 