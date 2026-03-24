#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filtro de Tipos de Estúdios com Mais de 7 Estabelecimentos
"""

import json

def filter_business_types_by_count(min_count=7):
    """Filtra tipos de estúdios com mais de 7 estabelecimentos"""
    
    # Carrega os insights de negócio
    with open('business_insights.json', 'r', encoding='utf-8') as f:
        insights = json.load(f)
    
    # Obtém os dados de oportunidades por tipo
    oportunidades_por_tipo = insights['segmentacao']['oportunidades_por_tipo']
    
    # Filtra apenas os que têm mais de 7 estabelecimentos
    filtered_types = {}
    for tipo, data in oportunidades_por_tipo.items():
        if data['count'] > min_count:
            filtered_types[tipo] = data
    
    # Ordena por quantidade de estabelecimentos (decrescente)
    sorted_types = dict(sorted(filtered_types.items(), key=lambda x: x[1]['count'], reverse=True))
    
    return sorted_types

def main():
    """Função principal para executar o filtro"""
    print("=== TIPOS DE ESTÚDIOS COM MAIS DE 7 ESTABELECIMENTOS ===\n")
    
    filtered_types = filter_business_types_by_count(7)
    
    print(f"📊 Total de tipos filtrados: {len(filtered_types)}\n")
    
    for tipo, data in filtered_types.items():
        print(f"🏢 {tipo}")
        print(f"   • Quantidade: {data['count']} estabelecimentos")
        print(f"   • Cidades: {data['cidades']}")
        print(f"   • Rating médio: {data['rating_medio']:.1f}/5")
        print(f"   • Reviews médio: {data['reviews_medio']:.1f}")
        print(f"   • Com website: {data['com_website']} ({data['com_website']/data['count']*100:.1f}%)")
        print(f"   • Com telefone: {data['com_telefone']} ({data['com_telefone']/data['count']*100:.1f}%)")
        print()
    
    # Salva os dados filtrados
    with open('business_types_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_types, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Dados filtrados salvos em 'business_types_filtered.json'")

if __name__ == "__main__":
    main()
