import json

def create_detailed_top50(input_file="estudio/estudios-cidades/top_50_estudios.json", 
                         output_file="estudio/estudios-cidades/top50_detailed.json"):
    """
    Cria um JSON com dados detalhados dos top 50 estúdios
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
    
    print(f"✅ Top 50 detalhado salvo em {output_file}")
    return detailed_data

def create_summary_top50(input_file="estudio/estudios-cidades/top_50_estudios.json", 
                        output_file="estudio/estudios-cidades/top50_summary.json"):
    """
    Cria um JSON resumido dos top 50 estúdios
    Campos: title, rating, reviews, phone, website, cidade
    """
    with open(input_file, "r", encoding="utf-8") as f:
        top50_data = json.load(f)
    
    summary_data = []
    for estudio in top50_data:
        summary_estudio = {
            "title": estudio.get("title"),
            "rating": estudio.get("rating"),
            "reviews": estudio.get("reviews"),
            "phone": estudio.get("phone"),
            "website": estudio.get("website"),
            "cidade": estudio.get("cidade")
        }
        summary_data.append(summary_estudio)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Top 50 resumido salvo em {output_file}")
    return summary_data

if __name__ == "__main__":
    # Criar ambos os arquivos
    detailed = create_detailed_top50()
    summary = create_summary_top50()
    
    print(f"\n📊 Resumo:")
    print(f"- Total de estúdios processados: {len(detailed)}")
    print(f"- Arquivo detalhado: top50_detailed.json")
    print(f"- Arquivo resumido: top50_summary.json")
