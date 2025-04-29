#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerar dados de teste para o sistema
"""

from datetime import datetime, timedelta
import random

def gerar_vasos_teste(db_models, company_id):
    """Gera vasos de pressão fictícios para testes"""
    
    categorias = ['I', 'II', 'III', 'IV', 'V']
    fluidos = ['Vapor d\'água', 'Ar comprimido', 'Nitrogênio', 'GLP', 'Óleo térmico']
    fabricantes = ['Metalúrgica ABC', 'Caldeiras XYZ', 'Vasos & Cia', 'PressureTech', 'IndustrialVasos']
    
    vasos = []
    for i in range(1, 6):
        tag = f'VP-{company_id:03d}-{i:03d}'
        vaso = {
            'tag': tag,
            'categoria': random.choice(categorias),
            'fluido': random.choice(fluidos),
            'volume': round(random.uniform(1.0, 10.0), 2),
            'pressao_projeto': round(random.uniform(5.0, 30.0), 2),
            'pressao_trabalho': round(random.uniform(3.0, 25.0), 2),
            'temperatura_projeto': round(random.uniform(50.0, 300.0), 2),
            'temperatura_trabalho': round(random.uniform(40.0, 250.0), 2),
            'data_fabricacao': datetime.now() - timedelta(days=random.randint(365*5, 365*20)),
            'fabricante': random.choice(fabricantes),
            'numero_serie': f'SN{random.randint(10000, 99999)}',
            'company_id': company_id,
            'ativo': True
        }
        vasos.append(vaso)
        
    # Insere os vasos no banco
    for vaso in vasos:
        db_models.criar_equipamento(**vaso)
        
    return len(vasos)

def gerar_inspecoes_teste(db_models, company_id, engineer_id):
    """Gera inspeções fictícias para testes"""
    
    # Busca os vasos da empresa
    vasos = db_models.get_equipment_by_company(company_id)
    if not vasos:
        return 0
        
    tipos_inspecao = ['Inicial', 'Periódica', 'Extraordinária']
    resultados = ['Aprovado', 'Reprovado', 'Aprovado com restrições']
    
    inspecoes = []
    for vaso in vasos:
        # Gera 2-4 inspeções por vaso
        for _ in range(random.randint(2, 4)):
            inspecao = {
                'equipment_id': vaso['id'],
                'tipo': random.choice(tipos_inspecao),
                'data': datetime.now() - timedelta(days=random.randint(0, 365*2)),
                'resultado': random.choice(resultados),
                'observacoes': 'Inspeção realizada conforme NR-13',
                'prazo_proxima_inspecao': datetime.now() + timedelta(days=random.randint(30, 365)),
                'engineer_id': engineer_id
            }
            inspecoes.append(inspecao)
            
    # Insere as inspeções no banco
    for inspecao in inspecoes:
        db_models.criar_inspecao(**inspecao)
        
    return len(inspecoes)

def gerar_relatorios_teste(db_models, engineer_id):
    """Gera relatórios fictícios para testes"""
    
    # Busca as inspeções do engenheiro
    inspecoes = db_models.get_inspections_by_engineer(engineer_id)
    if not inspecoes:
        return 0
        
    relatorios = []
    for inspecao in inspecoes:
        if random.random() < 0.7:  # 70% de chance de ter relatório
            relatorio = {
                'inspection_id': inspecao['id'],
                'data': inspecao['data'] + timedelta(days=random.randint(1, 7)),
                'conteudo': f"""
                RELATÓRIO DE INSPEÇÃO
                
                1. IDENTIFICAÇÃO DO EQUIPAMENTO
                Tag: {inspecao['equipment_tag']}
                
                2. INSPEÇÃO REALIZADA
                Tipo: {inspecao['tipo']}
                Data: {inspecao['data'].strftime('%d/%m/%Y')}
                
                3. RESULTADO
                Status: {inspecao['resultado']}
                
                4. CONCLUSÃO
                {inspecao['observacoes']}
                
                5. PRÓXIMA INSPEÇÃO
                Data prevista: {inspecao['prazo_proxima_inspecao'].strftime('%d/%m/%Y')}
                """,
                'engineer_id': engineer_id
            }
            relatorios.append(relatorio)
            
    # Insere os relatórios no banco
    for relatorio in relatorios:
        db_models.criar_relatorio(**relatorio)
        
    return len(relatorios) 