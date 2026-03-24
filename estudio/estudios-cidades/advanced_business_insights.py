import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime

def analyze_business_insights():
    """
    Análise avançada de insights de negócio dos estúdios de Santa Catarina
    """
    
    # Carregar dados
    with open("estudio/estudios-cidades/estudios_sc_sanitized.json", "r", encoding="utf-8") as f:
        estudios_data = json.load(f)
    
    with open("estudio/estudios-cidades/top50_summary.json", "r", encoding="utf-8") as f:
        top50_data = json.load(f)
    
    with open("estudio/estudios-cidades/top50_detailed.json", "r", encoding="utf-8") as f:
        top50_detailed = json.load(f)
    
    insights = {
        "timestamp": datetime.now().isoformat(),
        "analise_mercado": {},
        "segmentacao_geografica": {},
        "performance_competitiva": {},
        "oportunidades_negocio": {},
        "tendencias_mercado": {},
        "recomendacoes_estrategicas": {}
    }
    
    # 1. ANÁLISE DE MERCADO GERAL
    total_estudios = 0
    total_reviews = 0
    ratings_list = []
    tipos_counter = Counter()
    cidades_counter = Counter()
    
    for cidade, data in estudios_data.items():
        estudios = data.get("results", [])
        total_estudios += len(estudios)
        cidades_counter[cidade] = len(estudios)
        
        for estudio in estudios:
            reviews = estudio.get("reviews", 0)
            if isinstance(reviews, str):
                try:
                    reviews = int(reviews.replace(",", "").replace(".", ""))
                except:
                    reviews = 0
            
            total_reviews += reviews
            rating = estudio.get("rating")
            if rating:
                ratings_list.append(rating)
            
            tipo = estudio.get("type", "Unknown")
            tipos_counter[tipo] += 1
    
    insights["analise_mercado"] = {
        "tamanho_total_mercado": total_estudios,
        "total_reviews_mercado": total_reviews,
        "rating_medio_geral": round(statistics.mean(ratings_list), 2) if ratings_list else 0,
        "densidade_media_por_cidade": round(total_estudios / len(cidades_counter), 2),
        "tipos_mais_comuns": dict(tipos_counter.most_common(10)),
        "cidades_mais_ativas": dict(cidades_counter.most_common(10))
    }
    
    # 2. SEGMENTAÇÃO GEOGRÁFICA
    regioes = {
        "Norte": ["Joinville", "Araquari", "São Francisco do Sul", "Garuva"],
        "Vale do Itajaí": ["Blumenau", "Itajaí", "Balneário Camboriú", "Camboriú", "Gaspar", "Indaial", "Timbó", "Navegantes", "Itapema"],
        "Grande Florianópolis": ["Florianópolis", "São José", "Palhoça", "Biguaçu"],
        "Sul": ["Criciúma", "Içara", "Araranguá", "Tubarão"],
        "Oeste": ["Chapecó", "Joaçaba", "Concórdia", "Caçador", "Curitibanos", "Videira"],
        "Serra": ["São Bento do Sul", "Rio Negrinho", "Jaraguá do Sul", "Rio do Sul"]
    }
    
    regioes_stats = {}
    for regiao, cidades in regioes.items():
        estudios_regiao = 0
        reviews_regiao = 0
        ratings_regiao = []
        
        for cidade in cidades:
            if cidade in estudios_data:
                data = estudios_data[cidade]
                estudios = data.get("results", [])
                estudios_regiao += len(estudios)
                
                for estudio in estudios:
                    reviews = estudio.get("reviews", 0)
                    if isinstance(reviews, str):
                        try:
                            reviews = int(reviews.replace(",", "").replace(".", ""))
                        except:
                            reviews = 0
                    reviews_regiao += reviews
                    
                    rating = estudio.get("rating")
                    if rating:
                        ratings_regiao.append(rating)
        
        regioes_stats[regiao] = {
            "total_estudios": estudios_regiao,
            "total_reviews": reviews_regiao,
            "rating_medio": round(statistics.mean(ratings_regiao), 2) if ratings_regiao else 0,
            "densidade": estudios_regiao / len(cidades) if cidades else 0
        }
    
    insights["segmentacao_geografica"] = regioes_stats
    
    # 3. PERFORMANCE COMPETITIVA (Top 50)
    top50_analysis = {
        "rating_medio_top50": round(statistics.mean([e["rating"] for e in top50_data if e["rating"]]), 2),
        "reviews_medio_top50": round(statistics.mean([e["reviews"] for e in top50_data]), 0),
        "tipos_top50": dict(Counter([e["type"] for e in top50_detailed if e.get("type")]).most_common()),
        "cidades_top50": dict(Counter([e["cidade"] for e in top50_data]).most_common()),
        "websites_top50": len([e for e in top50_data if e.get("website") and e["website"] != ""]),
        "percentual_com_website": round(len([e for e in top50_data if e.get("website") and e["website"] != ""]) / len(top50_data) * 100, 1)
    }
    
    insights["performance_competitiva"] = top50_analysis
    
    # 4. OPORTUNIDADES DE NEGÓCIO
    oportunidades = {
        "cidades_subatendidas": [],
        "tipos_em_alta": [],
        "gap_tecnologico": {},
        "oportunidades_expansao": []
    }
    
    # Cidades com poucos estúdios mas potencial
    cidades_pequenas = [(cidade, count) for cidade, count in cidades_counter.items() if count < 5]
    oportunidades["cidades_subatendidas"] = sorted(cidades_pequenas, key=lambda x: x[1])[:10]
    
    # Tipos com alta demanda mas baixa oferta
    tipos_demanda = {}
    for tipo, count in tipos_counter.items():
        if count > 10:  # Tipos com pelo menos 10 estúdios
            ratings_tipo = [e["rating"] for e in top50_detailed if e.get("type") == tipo and e.get("rating")]
            if ratings_tipo:  # Verificar se há ratings disponíveis
                avg_rating = statistics.mean(ratings_tipo)
                tipos_demanda[tipo] = {
                    "quantidade": count,
                    "rating_medio": round(avg_rating, 2),
                    "score_oportunidade": count * avg_rating
                }
            else:
                # Se não há ratings no top 50, usar rating médio geral
                tipos_demanda[tipo] = {
                    "quantidade": count,
                    "rating_medio": insights["analise_mercado"]["rating_medio_geral"],
                    "score_oportunidade": count * insights["analise_mercado"]["rating_medio_geral"]
                }
    
    oportunidades["tipos_em_alta"] = sorted(tipos_demanda.items(), key=lambda x: x[1]["score_oportunidade"], reverse=True)[:5]
    
    # Gap tecnológico (estúdios sem site próprio - excluindo redes sociais)
    redes_sociais = ["instagram.com", "facebook.com", "youtube.com", "soundcloud.com", "tiktok.com", "twitter.com", "linkedin.com", "pinterest.com"]
    
    def tem_site_proprio(website):
        if not website or website == "":
            return False
        
        website_lower = website.lower()
        # Verificar se é uma rede social
        for rede in redes_sociais:
            if rede in website_lower:
                return False
        
        # Se não é rede social e tem website, considera como site próprio
        return True
    
    sem_site_proprio = len([e for e in top50_data if not tem_site_proprio(e.get("website"))])
    com_site_proprio = len([e for e in top50_data if tem_site_proprio(e.get("website"))])
    apenas_redes_sociais = len([e for e in top50_data if e.get("website") and e["website"] != "" and not tem_site_proprio(e.get("website"))])
    
    oportunidades["gap_tecnologico"] = {
        "estudios_sem_site_proprio_top50": sem_site_proprio,
        "estudios_com_site_proprio_top50": com_site_proprio,
        "estudios_apenas_redes_sociais_top50": apenas_redes_sociais,
        "percentual_sem_site_proprio": round(sem_site_proprio / len(top50_data) * 100, 1),
        "percentual_com_site_proprio": round(com_site_proprio / len(top50_data) * 100, 1),
        "oportunidade_digital": "Alta" if sem_site_proprio > 25 else "Média" if sem_site_proprio > 15 else "Baixa"
    }
    
    insights["oportunidades_negocio"] = oportunidades
    
    # 5. TENDÊNCIAS DE MERCADO
    tendencias = {
        "horarios_funcionamento": {},
        "concentracao_geografica": {},
        "padroes_rating": {}
    }
    
    # Análise de horários de funcionamento
    horarios_counter = Counter()
    for estudio in top50_detailed:
        operating_hours = estudio.get("operating_hours", {})
        if isinstance(operating_hours, dict):
            for dia, horario in operating_hours.items():
                if "24 hours" in str(horario):
                    horarios_counter["24h"] += 1
                elif "AM" in str(horario) and "PM" in str(horario):
                    horarios_counter["Comercial"] += 1
                elif "Closed" in str(horario):
                    horarios_counter["Fechado"] += 1
    
    tendencias["horarios_funcionamento"] = dict(horarios_counter)
    
    # Concentração geográfica
    concentracao = {}
    for regiao, cidades in regioes.items():
        total_regiao = sum([cidades_counter.get(cidade, 0) for cidade in cidades])
        concentracao[regiao] = {
            "total_estudios": total_regiao,
            "percentual_mercado": round(total_regiao / total_estudios * 100, 1)
        }
    
    tendencias["concentracao_geografica"] = concentracao
    
    # Padrões de rating
    rating_ranges = {"5.0": 0, "4.5-4.9": 0, "4.0-4.4": 0, "3.5-3.9": 0, "<3.5": 0}
    for estudio in top50_data:
        rating = estudio.get("rating", 0)
        if rating == 5.0:
            rating_ranges["5.0"] += 1
        elif 4.5 <= rating < 5.0:
            rating_ranges["4.5-4.9"] += 1
        elif 4.0 <= rating < 4.5:
            rating_ranges["4.0-4.4"] += 1
        elif 3.5 <= rating < 4.0:
            rating_ranges["3.5-3.9"] += 1
        else:
            rating_ranges["<3.5"] += 1
    
    tendencias["padroes_rating"] = rating_ranges
    
    insights["tendencias_mercado"] = tendencias
    
    # 6. RECOMENDAÇÕES ESTRATÉGICAS
    recomendacoes = {
        "mercados_prioritarios": [],
        "estrategias_diferencial": [],
        "investimentos_sugeridos": [],
        "riscos_mercado": []
    }
    
    # Mercados prioritários (baseado em densidade e rating)
    mercados_prioritarios = []
    for regiao, stats in regioes_stats.items():
        if stats["densidade"] < 10 and stats["rating_medio"] > 4.0:  # Baixa densidade, alta qualidade
            mercados_prioritarios.append({
                "regiao": regiao,
                "densidade": stats["densidade"],
                "rating_medio": stats["rating_medio"],
                "potencial": "Alto"
            })
            
    
    recomendacoes["mercados_prioritarios"] = sorted(mercados_prioritarios, key=lambda x: x["rating_medio"], reverse=True)
    
    # Estratégias de diferencial
    estrategias = [
        "Foco em serviços 24h para capturar mercado noturno",
        "Desenvolvimento de presença digital (websites profissionais)",
        "Especialização em nichos específicos (newborn, casamentos)",
        "Expansão para cidades com baixa densidade de estúdios",
        "Implementação de sistema de agendamento online"
    ]
    recomendacoes["estrategias_diferencial"] = estrategias
    
    # Investimentos sugeridos
    investimentos = [
        "Marketing digital e SEO para aumentar visibilidade online",
        "Equipamentos de última geração para diferenciação técnica",
        "Treinamento de equipe em atendimento ao cliente",
        "Sistema de gestão integrado (agendamento, pagamentos)",
        "Expansão física em mercados prioritários"
    ]
    recomendacoes["investimentos_sugeridos"] = investimentos
    
    # Riscos de mercado
    riscos = [
        "Alta concentração em algumas regiões pode indicar saturação",
        "Dependência de avaliações online para reputação",
        "Concorrência crescente em cidades principais",
        "Necessidade de constante atualização tecnológica"
    ]
    recomendacoes["riscos_mercado"] = riscos
    
    insights["recomendacoes_estrategicas"] = recomendacoes
    
    return insights

def save_insights(insights, filename="estudio/estudios-cidades/advanced_business_insights.json"):
    """Salva os insights em arquivo JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Insights avançados salvos em {filename}")
    return insights

def print_summary(insights):
    """Imprime um resumo dos insights principais"""
    print("\n" + "="*60)
    print("📊 INSIGHTS AVANÇADOS DE NEGÓCIO - ESTÚDIOS SC")
    print("="*60)
    
    mercado = insights["analise_mercado"]
    print(f"\n🏢 MERCADO GERAL:")
    print(f"   • Total de estúdios: {mercado['tamanho_total_mercado']}")
    print(f"   • Total de reviews: {mercado['total_reviews_mercado']:,}")
    print(f"   • Rating médio: {mercado['rating_medio_geral']}")
    print(f"   • Densidade média por cidade: {mercado['densidade_media_por_cidade']}")
    
    print(f"\n🎯 TOP 5 TIPOS MAIS COMUNS:")
    for tipo, count in list(mercado['tipos_mais_comuns'].items())[:5]:
        print(f"   • {tipo}: {count} estúdios")
    
    print(f"\n🌍 TOP 5 CIDADES MAIS ATIVAS:")
    for cidade, count in list(mercado['cidades_mais_ativas'].items())[:5]:
        print(f"   • {cidade}: {count} estúdios")
    
    performance = insights["performance_competitiva"]
    print(f"\n🏆 PERFORMANCE TOP 50:")
    print(f"   • Rating médio: {performance['rating_medio_top50']}")
    print(f"   • Reviews médio: {performance['reviews_medio_top50']}")
    print(f"   • % com website: {performance['percentual_com_website']}%")
    
    oportunidades = insights["oportunidades_negocio"]
    gap = oportunidades['gap_tecnologico']
    print(f"\n💡 OPORTUNIDADES:")
    print(f"   • Gap tecnológico: {gap['oportunidade_digital']}")
    print(f"   • Estúdios sem site próprio no top 50: {gap['estudios_sem_site_proprio_top50']} ({gap['percentual_sem_site_proprio']}%)")
    print(f"   • Estúdios com site próprio no top 50: {gap['estudios_com_site_proprio_top50']} ({gap['percentual_com_site_proprio']}%)")
    print(f"   • Estúdios apenas com redes sociais: {gap['estudios_apenas_redes_sociais_top50']}")
    
    recomendacoes = insights["recomendacoes_estrategicas"]
    print(f"\n🎯 MERCADOS PRIORITÁRIOS:")
    for mercado in recomendacoes["mercados_prioritarios"][:3]:
        print(f"   • {mercado['regiao']}: Rating {mercado['rating_medio']}, Densidade {mercado['densidade']}")
    
    print(f"\n📈 ESTRATÉGIAS RECOMENDADAS:")
    for estrategia in recomendacoes["estrategias_diferencial"][:3]:
        print(f"   • {estrategia}")

if __name__ == "__main__":
    print("🔍 Analisando dados para insights avançados...")
    insights = analyze_business_insights()
    save_insights(insights)
    print_summary(insights)
    
    print(f"\n📄 Análise completa salva em: advanced_business_insights.json")
    print(f"📊 Total de insights gerados: {len(insights)} categorias principais")
