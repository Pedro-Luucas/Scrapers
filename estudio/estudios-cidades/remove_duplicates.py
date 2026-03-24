import json
import os
from collections import defaultdict

def remove_duplicate_place_ids(input_file, output_file):
    """
    Remove objetos com place_id duplicados do arquivo sanitizado.
    Verifica duplicatas globalmente (entre todas as cidades) e mantém apenas a primeira ocorrência.
    """
    
    print(f"Lendo arquivo: {input_file}")
    
    # Ler o arquivo JSON sanitizado
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processando {len(data)} cidades...")
    
    # Estrutura para dados sem duplicatas
    deduplicated_data = {}
    total_removed = 0
    total_original = 0
    
    # Set global para rastrear place_ids já vistos em todas as cidades
    global_seen_place_ids = set()
    
    for cidade, cidade_data in data.items():
        print(f"Processando cidade: {cidade}")
        
        # Criar estrutura para a cidade
        deduplicated_data[cidade] = {
            "results": []
        }
        
        # Contar resultados originais
        original_count = len(cidade_data.get("results", []))
        total_original += original_count
        
        duplicates_found = 0
        
        # Processar resultados
        if 'results' in cidade_data and cidade_data['results']:
            for result in cidade_data['results']:
                place_id = result.get('place_id', '').strip()
                
                # Se o place_id já foi visto em qualquer cidade, pular este resultado
                if place_id in global_seen_place_ids:
                    duplicates_found += 1
                    title = result.get('title', 'Sem título')
                    print(f"  - Duplicata global encontrada: '{title}' (place_id: {place_id})")
                    continue
                
                # Adicionar place_id ao set global de place_ids vistos
                global_seen_place_ids.add(place_id)
                
                # Adicionar resultado à lista deduplicada
                deduplicated_data[cidade]["results"].append(result)
        
        # Contar resultados após remoção de duplicatas
        final_count = len(deduplicated_data[cidade]["results"])
        total_removed += duplicates_found
        
        print(f"  - Resultados originais: {original_count}")
        print(f"  - Duplicatas removidas: {duplicates_found}")
        print(f"  - Resultados finais: {final_count}")
    
    # Salvar arquivo sem duplicatas
    print(f"Salvando arquivo sem duplicatas: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(deduplicated_data, f, ensure_ascii=False, indent=2)
    
    print("\nRemoção de duplicatas concluída!")
    return deduplicated_data, total_original, total_removed

def analyze_duplicates(input_file):
    """
    Analisa o arquivo para mostrar estatísticas de duplicatas globais baseado em place_id.
    """
    
    print(f"Analisando duplicatas em: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Coletar todos os place_ids de todas as cidades
    all_place_ids = []
    place_id_to_info = {}  # place_id -> {'title': title, 'cidade': cidade}
    
    for cidade, cidade_data in data.items():
        if 'results' not in cidade_data or not cidade_data['results']:
            continue
            
        for result in cidade_data['results']:
            place_id = result.get('place_id', '').strip()
            if place_id:
                all_place_ids.append(place_id)
                place_id_to_info[place_id] = {
                    'title': result.get('title', 'Sem título'),
                    'cidade': cidade
                }
    
    # Contar ocorrências de cada place_id
    place_id_counts = defaultdict(int)
    for place_id in all_place_ids:
        place_id_counts[place_id] += 1
    
    # Encontrar duplicatas
    duplicates = {place_id: count for place_id, count in place_id_counts.items() if count > 1}
    
    print("\nAnálise de duplicatas globais:")
    print("-" * 60)
    
    if duplicates:
        print(f"Encontradas {len(duplicates)} duplicatas globais:")
        print()
        
        for place_id, count in duplicates.items():
            info = place_id_to_info[place_id]
            print(f"'{info['title']}' (place_id: {place_id})")
            print(f"  - Aparece {count} vezes")
            
            # Mostrar em quais cidades aparece
            cities_with_this_place_id = []
            for cidade, cidade_data in data.items():
                if 'results' in cidade_data and cidade_data['results']:
                    for result in cidade_data['results']:
                        if result.get('place_id', '').strip() == place_id:
                            cities_with_this_place_id.append(cidade)
                            break
            
            print(f"  - Cidades: {', '.join(cities_with_this_place_id)}")
            print()
    else:
        print("Nenhuma duplicata global encontrada!")
    
    total_duplicates = sum(count - 1 for count in duplicates.values())  # -1 porque mantemos uma ocorrência
    
    print("-" * 60)
    print(f"Resumo geral:")
    print(f"- Total de resultados: {len(all_place_ids)}")
    print(f"- Place IDs únicos: {len(place_id_counts)}")
    print(f"- Duplicatas globais: {len(duplicates)}")
    print(f"- Total de registros duplicados a remover: {total_duplicates}")
    
    return total_duplicates

if __name__ == "__main__":
    input_file = "estudio/estudios-cidades/estudios_sc_sanitized.json"
    output_file = "estudio/estudios-cidades/estudios_sc_sanitized.json"
    
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo {input_file} não encontrado!")
        exit(1)
    
    # Primeiro, analisar duplicatas
    print("=== ANÁLISE DE DUPLICATAS ===")
    total_duplicates = analyze_duplicates(input_file)
    
    if total_duplicates == 0:
        print("\nNenhuma duplicata encontrada! O arquivo já está limpo.")
    else:
        print(f"\n=== REMOVENDO {total_duplicates} DUPLICATAS ===")
        
        # Executar remoção de duplicatas
        deduplicated_data, total_original, total_removed = remove_duplicate_place_ids(input_file, output_file)
        
        # Mostrar estatísticas finais
        total_cities = len(deduplicated_data)
        total_final = sum(len(city_data["results"]) for city_data in deduplicated_data.values())
        
        print(f"\nEstatísticas finais:")
        print(f"- Total de cidades: {total_cities}")
        print(f"- Total de resultados originais: {total_original}")
        print(f"- Duplicatas removidas: {total_removed}")
        print(f"- Total de resultados finais: {total_final}")
        print(f"- Arquivo de saída: {output_file}")
        print(f"- ")