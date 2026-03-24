#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai todos os estúdios dos tipos de negócio filtrados
"""

import json
import os

def extract_filtered_estudios():
    """Extrai todos os estúdios dos tipos de negócio com mais de 7 estabelecimentos"""
    
    # Carrega os tipos de negócio filtrados
    with open('business_types_filtered.json', 'r', encoding='utf-8') as f:
        filtered_types = json.load(f)
    
    # Carrega os dados sanitizados dos estúdios
    script_dir = os.path.dirname(os.path.abspath(__file__))
    estudios_file = os.path.join(script_dir, 'estudio', 'estudios-cidades', 'estudios_sc_sanitized.json')
    
    with open(estudios_file, 'r', encoding='utf-8') as f:
        estudios_data = json.load(f)
    
    # Lista dos tipos de negócio que queremos extrair
    target_types = list(filtered_types.keys())
    
    print(f"Tipos de negócio alvo: {target_types}")
    print(f"Total de tipos: {len(target_types)}")
    
    # Estrutura para armazenar os estúdios filtrados
    filtered_estudios = {}
    
    # Contador para estatísticas
    total_extracted = 0
    
    # Itera por todas as cidades
    for cidade, info in estudios_data.items():
        cidade_estudios = []
        
        # Itera pelos resultados de cada cidade
        for estudio in info.get('results', []):
            estudio_type = estudio.get('type', '')
            
            # Verifica se o tipo está na lista de tipos filtrados
            if estudio_type in target_types:
                # Adiciona a cidade ao objeto do estúdio
                estudio['cidade'] = cidade
                cidade_estudios.append(estudio)
                total_extracted += 1
        
        # Adiciona a cidade apenas se tiver estúdios dos tipos filtrados
        if cidade_estudios:
            filtered_estudios[cidade] = {
                'results': cidade_estudios,
                'total_estudios': len(cidade_estudios)
            }
    
    # Estatísticas por tipo
    type_stats = {}
    for cidade, info in filtered_estudios.items():
        for estudio in info['results']:
            tipo = estudio.get('type', 'N/A')
            if tipo not in type_stats:
                type_stats[tipo] = 0
            type_stats[tipo] += 1
    
    # Adiciona estatísticas ao resultado final
    result = {
        'metadata': {
            'total_cidades': len(filtered_estudios),
            'total_estudios': total_extracted,
            'tipos_incluidos': target_types,
            'estatisticas_por_tipo': type_stats
        },
        'estudios_por_cidade': filtered_estudios
    }
    
    return result

def main():
    """Função principal"""
    print("=== EXTRAINDO ESTÚDIOS DOS TIPOS FILTRADOS ===\n")
    
    # Extrai os dados
    filtered_data = extract_filtered_estudios()
    
    # Exibe estatísticas
    metadata = filtered_data['metadata']
    print(f"📊 ESTATÍSTICAS:")
    print(f"   • Total de cidades com estúdios filtrados: {metadata['total_cidades']}")
    print(f"   • Total de estúdios extraídos: {metadata['total_estudios']}")
    print(f"   • Tipos incluídos: {len(metadata['tipos_incluidos'])}")
    
    print(f"\n🏢 ESTATÍSTICAS POR TIPO:")
    for tipo, count in metadata['estatisticas_por_tipo'].items():
        print(f"   • {tipo}: {count} estúdios")
    
    # Salva o resultado
    output_file = 'estudios_filtered_by_type.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Dados salvos em '{output_file}'")
    print(f"📄 Arquivo contém {metadata['total_estudios']} estúdios de {metadata['total_cidades']} cidades")

if __name__ == "__main__":
    main()
