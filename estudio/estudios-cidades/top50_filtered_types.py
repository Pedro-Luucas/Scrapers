import json

def top_50_filtered_estudios(file_path: str, output_path: str = "estudio/estudios-cidades/top_50_filtered_estudios.json"):
    """
    Cria top 50 estúdios apenas com os tipos permitidos
    """
    # Tipos permitidos conforme especificado
    allowed_types = [
        "Recording studio",
        "Photography studio", 
        "Portrait studio",
        "Beauty salon",
        "Tattoo shop",
        "Photographer",
        "Rehearsal studio"
    ]
    
    # Carregar o JSON local
    with open(file_path, "r", encoding="utf-8") as f:
        estudios_sc_sanitized = json.load(f)

    # Juntar todos os estúdios de todas as cidades, filtrando apenas os tipos permitidos
    all_estudios = []
    for cidade, data in estudios_sc_sanitized.items():
        for est in data.get("results", []):
            # Verificar se o tipo está na lista de tipos permitidos
            if est.get("type") in allowed_types:
                # Converter reviews para int, tratando casos onde pode ser string
                reviews = est.get("reviews", 0)
                if isinstance(reviews, str):
                    try:
                        reviews = int(reviews.replace(",", "").replace(".", ""))
                    except (ValueError, AttributeError):
                        reviews = 0
                
                # Criar um novo objeto com todos os dados do estúdio + cidade
                estudio_completo = est.copy()
                estudio_completo["cidade"] = cidade
                estudio_completo["reviews"] = reviews  # Usar o valor convertido para int
                all_estudios.append(estudio_completo)
    
    # Ordenar do maior para o menor por número de reviews
    all_estudios.sort(key=lambda x: x["reviews"], reverse=True)

    # Pegar só top 50
    top_50 = all_estudios[:50]

    # Salvar em arquivo JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(top_50, f, ensure_ascii=False, indent=2)

    print(f"✅ Top 50 filtrado salvo em {output_path}")
    print(f"📊 Total de estúdios encontrados com tipos permitidos: {len(all_estudios)}")
    print(f"📊 Top 50 selecionados")
    
    # Mostrar estatísticas por tipo
    type_counts = {}
    for estudio in top_50:
        tipo = estudio.get("type", "Unknown")
        type_counts[tipo] = type_counts.get(tipo, 0) + 1
    
    print(f"\n📈 Distribuição por tipo no top 50:")
    for tipo, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {tipo}: {count}")
    
    return top_50

def create_detailed_filtered_top50(input_file="estudio/estudios-cidades/top_50_filtered_estudios.json", 
                                 output_file="estudio/estudios-cidades/top50_filtered_detailed.json"):
    """
    Cria um JSON com dados detalhados dos top 50 estúdios filtrados
    Campos: title, gps_coordinates, rating, reviews, type, type_id, address, operating_hours, phone, website, cidade
    """
    with open(input_file, "r", encoding="utf-8") as f:
        top50_data = json.load(f)
    
    detailed_data = []
    for estudio in top50_data:
        detailed_estudio = {
            "title": estudio.get("title"),
            "gps_coordinates": estudio.get("gps_coordinates"),
            "rating": estudio.get("rating"),
            "reviews": estudio.get("reviews"),
            "type": estudio.get("type"),
            "type_id": estudio.get("type_id"),
            "address": estudio.get("address"),
            "operating_hours": estudio.get("operating_hours"),
            "phone": estudio.get("phone"),
            "website": estudio.get("website"),
            "cidade": estudio.get("cidade")
        }
        detailed_data.append(detailed_estudio)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(detailed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Top 50 filtrado detalhado salvo em {output_file}")
    return detailed_data

def create_summary_filtered_top50(input_file="estudio/estudios-cidades/top_50_filtered_estudios.json", 
                                output_file="estudio/estudios-cidades/top50_filtered_summary.json"):
    """
    Cria um JSON resumido dos top 50 estúdios filtrados
    Campos: title, rating, reviews, type, phone, website, cidade
    """
    with open(input_file, "r", encoding="utf-8") as f:
        top50_data = json.load(f)
    
    summary_data = []
    for estudio in top50_data:
        summary_estudio = {
            "title": estudio.get("title"),
            "rating": estudio.get("rating"),
            "reviews": estudio.get("reviews"),
            "type": estudio.get("type"),
            "phone": estudio.get("phone"),
            "website": estudio.get("website"),
            "cidade": estudio.get("cidade")
        }
        summary_data.append(summary_estudio)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Top 50 filtrado resumido salvo em {output_file}")
    return summary_data

if __name__ == "__main__":
    # Criar o top 50 filtrado
    top_50 = top_50_filtered_estudios("estudio/estudios-cidades/estudios_sc_sanitized.json")
    
    # Criar ambos os arquivos detalhado e resumido
    detailed = create_detailed_filtered_top50()
    summary = create_summary_filtered_top50()
    
    print(f"\n📊 Resumo final:")
    print(f"- Total de estúdios processados: {len(detailed)}")
    print(f"- Arquivo principal: top_50_filtered_estudios.json")
    print(f"- Arquivo detalhado: top50_filtered_detailed.json")
    print(f"- Arquivo resumido: top50_filtered_summary.json")
