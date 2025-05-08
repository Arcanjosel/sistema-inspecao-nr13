#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar diretamente a janela de laudos técnicos
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDate
from ui.laudo_window import LaudoWindow

# Configuração do logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/teste_laudo.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona um handler para mostrar logs no console também
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("=== INICIANDO TESTE DE LAUDO TÉCNICO ===")
        
        # Cria dados de exemplo para o laudo
        dados_teste = {
            'insp_id': 999,
            'insp_data': QDate.currentDate(),
            'insp_tipo': 'Periódica',
            'insp_responsavel': 'Engenheiro de Teste',
            'insp_resultado': 'Aprovado',
            'insp_proxima': QDate.currentDate().addYears(1),
            'ensaios_realizados': "Exame Visual Externo, Medição de Espessura",
            'ensaios_adicionais': "Ultrassom em pontos críticos",
            'nao_conformidades': "Sem não conformidades relevantes",
            'recomendacoes': "Manter plano de manutenção preventiva conforme cronograma",
            'conclusao': "Equipamento em boas condições operacionais, aprovado para operação.",
            
            # Dados do equipamento
            'equipamento_id': 123,
            'equipamento_tag': 'VP-TESTE-001',
            'equipamento_nome': 'Vaso de Pressão de Teste',
            'equipamento_categoria': 'Vaso de Pressão',
            'equipamento_tipo': 'Ar Comprimido',
            'equipamento_localizacao': 'Sala de Compressores',
            'equipamento_fabricante': 'Fabricante de Teste',
            'equipamento_ano_fabricacao': '2020',
            'equipamento_capacidade': '500 L',
            'equipamento_pressao_trabalho': '10 bar',
            
            # Dados da empresa
            'empresa_nome': 'Empresa de Teste LTDA',
            'empresa_cnpj': '12.345.678/0001-99',
            'empresa_endereco': 'Av. Teste, 123',
            'empresa_cidade': 'São Paulo',
            'empresa_estado': 'SP',
        }
        
        # Inicializa o aplicativo Qt
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Estilo mais moderno
        
        # Cria e exibe a janela de laudo
        laudo_window = LaudoWindow(None, dados_teste)
        laudo_window.show()
        
        # Executa o loop de eventos do aplicativo
        logger.info("Interface de laudo técnico iniciada")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicativo: {str(e)}")
        import traceback
        logger.error(traceback.format_exc()) 