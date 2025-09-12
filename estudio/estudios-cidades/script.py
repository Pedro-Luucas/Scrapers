import json
import time
from serpapi import GoogleSearch

def buscar_estudios_por_cidade():
    # Carrega as cidades do JSON
    with open('../santa_catarina_cities.json', 'r', encoding='utf-8') as f:
        cidades = json.load(f)
    
    resultados = {}
    
    print(f"Iniciando busca de estúdios em {len(cidades)} cidades...")
    
    for i, (cidade, coordenadas) in enumerate(cidades.items(), 1):
        print(f"[{i}/{len(cidades)}] Buscando estúdios em {cidade}...")
        
        try:
            params = {
                "engine": "google_maps",
                "q": "Estudio",
                "ll": coordenadas,
                "api_key": "9cb3b3c42098e3d00f1cf99e65637997002837e01e1c672491e330caa52eb679"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            resultados[cidade] = results
            print(f"✓ {cidade}: {len(results.get('local_results', []))} resultados encontrados")
            
            # Delay de 2 segundos entre requisições
            if i < len(cidades):  # Não faz delay na última iteração
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Erro ao buscar estúdios em {cidade}: {str(e)}")
            print("Parando o script devido ao erro.")
            break
    
    # Salva os resultados
    with open('estudios_sc.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Busca concluída! Resultados salvos em 'estudios_sc.json'")
    print(f"Total de cidades processadas: {len(resultados)}")

if __name__ == "__main__":
    buscar_estudios_por_cidade()
