#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Dados de Estúdios de Santa Catarina
Insights de Negócio para ERP de Estúdios
"""

import json
import pandas as pd
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

class EstudioBusinessAnalyzer:
    def __init__(self, json_file_path):
        """Inicializa o analisador com os dados do JSON"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.estudios_data = []
        self._extract_all_estudios()
        
    def _extract_all_estudios(self):
        """Extrai todos os estúdios de todas as cidades"""
        for cidade, info in self.data.items():
            for estudio in info.get('results', []):
                estudio['cidade'] = cidade
                self.estudios_data.append(estudio)
    
    def get_basic_stats(self):
        """Estatísticas básicas do mercado"""
        total_estudios = len(self.estudios_data)
        total_cidades = len(self.data)
        
        # Tipos de estúdios
        tipos = [e.get('type', 'N/A') for e in self.estudios_data]
        tipos_counter = Counter(tipos)
        
        # Distribuição por cidade
        cidades_counter = Counter([e['cidade'] for e in self.estudios_data])
        
        return {
            'total_estudios': total_estudios,
            'total_cidades': total_cidades,
            'tipos_estudios': dict(tipos_counter.most_common()),
            'distribuicao_cidades': dict(cidades_counter.most_common(10)),
            'media_estudios_por_cidade': total_estudios / total_cidades
        }
    
    def analyze_ratings_and_reviews(self):
        """Análise de avaliações e reviews"""
        ratings_data = []
        reviews_data = []
        
        for estudio in self.estudios_data:
            rating = estudio.get('rating', '')
            reviews = estudio.get('reviews', '')
            
            if rating and rating != '':
                try:
                    ratings_data.append(float(rating))
                except:
                    pass
            
            if reviews and reviews != '':
                try:
                    reviews_data.append(int(reviews))
                except:
                    pass
        
        return {
            'total_com_rating': len(ratings_data),
            'total_com_reviews': len(reviews_data),
            'rating_medio': sum(ratings_data) / len(ratings_data) if ratings_data else 0,
            'rating_min': min(ratings_data) if ratings_data else 0,
            'rating_max': max(ratings_data) if ratings_data else 0,
            'reviews_medio': sum(reviews_data) / len(reviews_data) if reviews_data else 0,
            'reviews_max': max(reviews_data) if reviews_data else 0
        }
    
    def analyze_operating_hours(self):
        """Análise dos horários de funcionamento"""
        horarios_analysis = {
            'total_com_horarios': 0,
            'horarios_por_dia': defaultdict(int),
            'horarios_24h': 0,
            'horarios_fechados_fim_semana': 0
        }
        
        for estudio in self.estudios_data:
            horarios = estudio.get('operating_hours', {})
            if horarios and horarios != '':
                horarios_analysis['total_com_horarios'] += 1
                
                # Verifica se funciona 24h
                if any('24 hours' in str(horario) for horario in horarios.values()):
                    horarios_analysis['horarios_24h'] += 1
                
                # Verifica se fecha fim de semana
                sabado = horarios.get('saturday', '').lower()
                domingo = horarios.get('sunday', '').lower()
                if 'closed' in sabado and 'closed' in domingo:
                    horarios_analysis['horarios_fechados_fim_semana'] += 1
                
                # Conta dias da semana
                for dia, horario in horarios.items():
                    if horario and horario != '' and 'closed' not in horario.lower():
                        horarios_analysis['horarios_por_dia'][dia] += 1
        
        return horarios_analysis
    
    def analyze_contact_info(self):
        """Análise das informações de contato"""
        contact_stats = {
            'total_com_telefone': 0,
            'total_com_website': 0,
            'total_com_endereco': 0,
            'websites_por_tipo': defaultdict(int)
        }
        
        for estudio in self.estudios_data:
            if estudio.get('phone', ''):
                contact_stats['total_com_telefone'] += 1
            
            if estudio.get('website', ''):
                contact_stats['total_com_website'] += 1
                # Analisa tipo de website
                website = estudio.get('website', '').lower()
                if 'instagram' in website:
                    contact_stats['websites_por_tipo']['Instagram'] += 1
                elif 'facebook' in website:
                    contact_stats['websites_por_tipo']['Facebook'] += 1
                elif 'youtube' in website:
                    contact_stats['websites_por_tipo']['YouTube'] += 1
                elif website.startswith('http'):
                    contact_stats['websites_por_tipo']['Website Próprio'] += 1
            
            if estudio.get('address', ''):
                contact_stats['total_com_endereco'] += 1
        
        return contact_stats
    
    def analyze_by_type(self):
        """Análise detalhada por tipo de estúdio"""
        tipos_analysis = defaultdict(lambda: {
            'count': 0,
            'ratings': [],
            'reviews': [],
            'cidades': set(),
            'com_website': 0,
            'com_telefone': 0
        })
        
        for estudio in self.estudios_data:
            tipo = estudio.get('type', 'N/A')
            tipos_analysis[tipo]['count'] += 1
            tipos_analysis[tipo]['cidades'].add(estudio['cidade'])
            
            # Rating
            rating = estudio.get('rating', '')
            if rating and rating != '':
                try:
                    tipos_analysis[tipo]['ratings'].append(float(rating))
                except:
                    pass
            
            # Reviews
            reviews = estudio.get('reviews', '')
            if reviews and reviews != '':
                try:
                    tipos_analysis[tipo]['reviews'].append(int(reviews))
                except:
                    pass
            
            # Website
            if estudio.get('website', ''):
                tipos_analysis[tipo]['com_website'] += 1
            
            # Telefone
            if estudio.get('phone', ''):
                tipos_analysis[tipo]['com_telefone'] += 1
        
        # Converte sets para contadores
        for tipo in tipos_analysis:
            tipos_analysis[tipo]['cidades'] = len(tipos_analysis[tipo]['cidades'])
            tipos_analysis[tipo]['rating_medio'] = (
                sum(tipos_analysis[tipo]['ratings']) / len(tipos_analysis[tipo]['ratings'])
                if tipos_analysis[tipo]['ratings'] else 0
            )
            tipos_analysis[tipo]['reviews_medio'] = (
                sum(tipos_analysis[tipo]['reviews']) / len(tipos_analysis[tipo]['reviews'])
                if tipos_analysis[tipo]['reviews'] else 0
            )
        
        return dict(tipos_analysis)
    
    def generate_business_insights(self):
        """Gera insights de negócio para ERP"""
        stats = self.get_basic_stats()
        ratings = self.analyze_ratings_and_reviews()
        horarios = self.analyze_operating_hours()
        contatos = self.analyze_contact_info()
        tipos = self.analyze_by_type()
        
        insights = {
            'mercado_total': {
                'tamanho': stats['total_estudios'],
                'cidades_cobertas': stats['total_cidades'],
                'densidade_media': stats['media_estudios_por_cidade']
            },
            'segmentacao': {
                'tipos_principais': list(stats['tipos_estudios'].keys())[:5],
                'oportunidades_por_tipo': tipos
            },
            'qualidade_mercado': {
                'rating_medio': ratings['rating_medio'],
                'penetracao_digital': {
                    'websites': contatos['total_com_website'],
                    'telefones': contatos['total_com_telefone'],
                    'percentual_digital': (contatos['total_com_website'] / stats['total_estudios']) * 100
                }
            },
            'operacional': {
                'horarios_funcionamento': horarios,
                'contato_completo': contatos
            }
        }
        
        return insights
    
    def generate_erp_recommendations(self):
        """Gera recomendações específicas para desenvolvimento do ERP"""
        insights = self.generate_business_insights()
        
        recommendations = {
            'modulos_prioritarios': [
                'Gestão de Agendamentos',
                'Controle Financeiro',
                'Gestão de Clientes',
                'Controle de Estoque (equipamentos)',
                'Relatórios de Performance'
            ],
            'funcionalidades_essenciais': [
                'Sistema de agendamento online',
                'Controle de pagamentos e recebimentos',
                'CRM integrado',
                'Gestão de sessões/fotos',
                'Relatórios de faturamento',
                'Controle de equipamentos e manutenção'
            ],
            'segmentos_alvo': [],
            'precificacao_sugerida': {
                'basico': 'R$ 49-99/mês',
                'profissional': 'R$ 149-299/mês',
                'enterprise': 'R$ 399-599/mês'
            },
            'estrategia_expansao': [
                'Começar com fotografia e estúdios de gravação',
                'Expandir para academias e estúdios de tatuagem',
                'Focar em cidades com maior densidade de estúdios'
            ]
        }
        
        # Identifica segmentos com maior potencial
        tipos_ordenados = sorted(
            insights['segmentacao']['oportunidades_por_tipo'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        recommendations['segmentos_alvo'] = [
            tipo for tipo, data in tipos_ordenados[:5]
            if data['count'] >= 10  # Segmentos com pelo menos 10 estúdios
        ]
        
        return recommendations

def main():
    """Função principal para executar a análise"""
    import os
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'estudios_sc_sanitized.json')
    analyzer = EstudioBusinessAnalyzer(json_file_path)
    
    print("=== ANÁLISE DE MERCADO - ERP PARA ESTÚDIOS ===\n")
    
    # Estatísticas básicas
    stats = analyzer.get_basic_stats()
    print(f"📊 MERCADO TOTAL:")
    print(f"   • Total de estúdios: {stats['total_estudios']}")
    print(f"   • Cidades cobertas: {stats['total_cidades']}")
    print(f"   • Média por cidade: {stats['media_estudios_por_cidade']:.1f}")
    
    print(f"\n🏢 TOP 5 TIPOS DE ESTÚDIOS:")
    for tipo, count in list(stats['tipos_estudios'].items())[:5]:
        print(f"   • {tipo}: {count} estúdios")
    
    print(f"\n🌆 TOP 5 CIDADES COM MAIS ESTÚDIOS:")
    for cidade, count in list(stats['distribuicao_cidades'].items())[:5]:
        print(f"   • {cidade}: {count} estúdios")
    
    # Análise de qualidade
    ratings = analyzer.analyze_ratings_and_reviews()
    contatos = analyzer.analyze_contact_info()
    
    print(f"\n⭐ QUALIDADE DO MERCADO:")
    print(f"   • Rating médio: {ratings['rating_medio']:.1f}/5")
    print(f"   • Estúdios com website: {contatos['total_com_website']} ({contatos['total_com_website']/stats['total_estudios']*100:.1f}%)")
    print(f"   • Estúdios com telefone: {contatos['total_com_telefone']} ({contatos['total_com_telefone']/stats['total_estudios']*100:.1f}%)")
    
    # Recomendações para ERP
    recommendations = analyzer.generate_erp_recommendations()
    
    print(f"\n💡 RECOMENDAÇÕES PARA ERP:")
    print(f"\n📋 MÓDULOS PRIORITÁRIOS:")
    for modulo in recommendations['modulos_prioritarios']:
        print(f"   • {modulo}")
    
    print(f"\n🎯 SEGMENTOS ALVO:")
    for segmento in recommendations['segmentos_alvo']:
        print(f"   • {segmento}")
    
    print(f"\n💰 SUGESTÃO DE PREÇOS:")
    for plano, preco in recommendations['precificacao_sugerida'].items():
        print(f"   • {plano.title()}: {preco}")
    
    print(f"\n🚀 ESTRATÉGIA DE EXPANSÃO:")
    for estrategia in recommendations['estrategia_expansao']:
        print(f"   • {estrategia}")
    
    # Salva insights detalhados
    insights_completos = analyzer.generate_business_insights()
    with open('business_insights.json', 'w', encoding='utf-8') as f:
        json.dump(insights_completos, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Insights detalhados salvos em 'business_insights.json'")

if __name__ == "__main__":
    main()
