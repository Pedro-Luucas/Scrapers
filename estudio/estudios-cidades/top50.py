import json

def top_50_estudios(file_path: str, output_path: str = "estudio/estudios-cidades/top_50_estudios.json"):
    # carregar o JSON local
    with open(file_path, "r", encoding="utf-8") as f:
        estudios_sc_sanitized = json.load(f)

    # juntar todos os estúdios de todas as cidades
    all_estudios = []
    for cidade, data in estudios_sc_sanitized.items():
        for est in data.get("results", []):
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
    
    # ordenar do maior para o menor por número de reviews
    all_estudios.sort(key=lambda x: x["reviews"], reverse=True)

    # pegar só top 50
    top_50 = all_estudios[:50]

    # salvar em arquivo JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(top_50, f, ensure_ascii=False, indent=2)

    print(f"✅ Top 50 salvo em {output_path}")
    return top_50


if __name__ == "__main__":
    top_50 = top_50_estudios("estudio/estudios-cidades/estudios_sc_sanitized.json")
