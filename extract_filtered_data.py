import json

# Load the business insights
with open('business_insights.json', 'r', encoding='utf-8') as f:
    insights = json.load(f)

# Get business types with count > 7
oportunidades = insights['segmentacao']['oportunidades_por_tipo']
filtered = {k: v for k, v in oportunidades.items() if v['count'] > 7}

# Sort by count (descending)
sorted_filtered = dict(sorted(filtered.items(), key=lambda x: x[1]['count'], reverse=True))

print("=== TIPOS DE ESTÚDIOS COM MAIS DE 7 ESTABELECIMENTOS ===\n")

for tipo, data in sorted_filtered.items():
    print(f"🏢 {tipo}")
    print(f"   • Quantidade: {data['count']} estabelecimentos")
    print(f"   • Cidades: {data['cidades']}")
    print(f"   • Rating médio: {data['rating_medio']:.1f}/5")
    print(f"   • Reviews médio: {data['reviews_medio']:.1f}")
    print(f"   • Com website: {data['com_website']} ({data['com_website']/data['count']*100:.1f}%)")
    print(f"   • Com telefone: {data['com_telefone']} ({data['com_telefone']/data['count']*100:.1f}%)")
    print()

print(f"📊 Total de tipos filtrados: {len(sorted_filtered)}")

# Save filtered data
with open('business_types_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_filtered, f, ensure_ascii=False, indent=2)

print(f"📄 Dados filtrados salvos em 'business_types_filtered.json'")
