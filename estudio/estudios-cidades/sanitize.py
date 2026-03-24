import json
import os

def sanitize_estudios_data(input_file, output_file):
    """
    Sanitiza os dados do arquivo estudios_sc.json removendo campos desnecessários
    e mantendo apenas os campos especificados nos local_results.
    """
    
    # Campos que devem ser mantidos nos local_results
    required_fields = [
        'position', 'title', 'place_id', 'data_id', 'data_cid', 
        'gps_coordinates', 'rating', 'reviews', 'type', 'type_id', 
        'address', 'operating_hours', 'phone', 'website'
    ]
    
    print(f"Lendo arquivo: {input_file}")
    
    # Ler o arquivo JSON original
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processando {len(data)} cidades...")
    
    # Estrutura sanitizada
    sanitized_data = {}
    
    for cidade, cidade_data in data.items():
        print(f"Processando cidade: {cidade}")
        
        # Criar estrutura para a cidade
        sanitized_data[cidade] = {
            "results": []
        }
        
        # Processar local_results se existir
        if 'local_results' in cidade_data and cidade_data['local_results']:
            for result in cidade_data['local_results']:
                sanitized_result = {}
                
                # Extrair apenas os campos necessários
                for field in required_fields:
                    if field in result:
                        sanitized_result[field] = result[field]
                    else:
                        sanitized_result[field] = ""
                
                sanitized_data[cidade]["results"].append(sanitized_result)
        
        print(f"  - {len(sanitized_data[cidade]['results'])} resultados encontrados")
    
    # Salvar arquivo sanitizado
    print(f"Salvando arquivo sanitizado: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sanitized_data, f, ensure_ascii=False, indent=2)
    
    print("Sanitização concluída!")
    return sanitized_data

if __name__ == "__main__":
    input_file = "estudio/estudios-cidades/estudios_sc.json"
    output_file = "estudio/estudios-cidades/estudios_sc_sanitized.json"
    
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo {input_file} não encontrado!")
        exit(1)
    
    # Executar sanitização
    sanitized_data = sanitize_estudios_data(input_file, output_file)
    
    # Mostrar estatísticas
    total_cities = len(sanitized_data)
    total_results = sum(len(city_data["results"]) for city_data in sanitized_data.values())
    
    print(f"\nEstatísticas:")
    print(f"- Total de cidades: {total_cities}")
    print(f"- Total de resultados: {total_results}")
    print(f"- Arquivo de saída: {output_file}")
