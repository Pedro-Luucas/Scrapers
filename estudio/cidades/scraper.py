import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from urllib.parse import urljoin

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SCCitiesScraper:
    def __init__(self):
        self.base_url = 'https://pt.db-city.com'
        self.start_url = 'https://pt.db-city.com/Brasil--Santa-Catarina'
        self.cities_data = {}
        self.results_file = 'santa_catarina_cities.json'
        
        # Configuração da sessão
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def get_city_links(self):
        """Extrai os links das cidades da página principal"""
        try:
            logger.info(f"Acessando página principal: {self.start_url}")
            response = self.session.get(self.start_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra a tabela com as cidades
            table = soup.find('table', class_='td25 otd')
            if not table:
                logger.error("Tabela com cidades não encontrada!")
                return []
            
            # Extrai todos os links das cidades
            city_links = []
            for link in table.find_all('a', href=True):
                href = link['href']
                city_name = link.get_text(strip=True)
                full_url = urljoin(self.base_url, href)
                city_links.append((city_name, full_url))
            
            logger.info(f"Encontradas {len(city_links)} cidades para processar")
            return city_links
            
        except requests.RequestException as e:
            logger.error(f"Erro ao acessar página principal: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao extrair links das cidades: {e}")
            return []

    def get_city_coordinates(self, city_name, city_url):
        """Extrai latitude e longitude da página da cidade"""
        try:
            logger.info(f"Processando: {city_name}")
            response = self.session.get(city_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra a célula com coordenadas geográficas
            geo_cell = soup.find('td', class_='geo')
            if not geo_cell:
                logger.warning(f"Elemento geo não encontrado para {city_name}")
                return None
            
            # Extrai latitude
            latitude_elem = geo_cell.find('b', class_='latitude')
            if not latitude_elem:
                logger.warning(f"Latitude não encontrada para {city_name}")
                return None
            
            # Extrai longitude
            longitude_elem = geo_cell.find('b', class_='longitude')
            if not longitude_elem:
                logger.warning(f"Longitude não encontrada para {city_name}")
                return None
            
            latitude = latitude_elem.get_text(strip=True)
            longitude = longitude_elem.get_text(strip=True)
            
            # Converte para float
            lat = float(latitude)
            lng = float(longitude)
            
            # Cria o formato do Google Maps
            google_maps_format = f"@{lat},{lng},12.5z"
            
            logger.info(f"{city_name}: {google_maps_format}")
            print(f"{city_name}: {google_maps_format}")
            
            return google_maps_format
            
        except requests.RequestException as e:
            logger.error(f"Erro de requisição ao processar {city_name}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Erro ao converter coordenadas de {city_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao processar {city_name}: {e}")
            return None

    def save_to_json(self):
        """Salva os dados em arquivo JSON"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.cities_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados salvos em {self.results_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo JSON: {e}")
            return False

    def run(self):
        """Executa o scraper completo"""
        logger.info("Iniciando scraper das cidades de Santa Catarina")
        
        # Obtém links das cidades
        city_links = self.get_city_links()
        if not city_links:
            logger.error("Nenhuma cidade encontrada. Encerrando...")
            return
        
        # Processa cada cidade
        total_cities = len(city_links)
        processed_count = 0
        
        for city_name, city_url in city_links:
            coordinates = self.get_city_coordinates(city_name, city_url)
            
            if coordinates:
                self.cities_data[city_name] = coordinates
                processed_count += 1
            
            # Delay entre requisições
            time.sleep(0.7)
        
        # Salva os resultados
        if self.cities_data:
            if self.save_to_json():
                print(f"\n=== RESUMO ===")
                print(f"Total de cidades encontradas: {total_cities}")
                print(f"Total de cidades processadas com sucesso: {processed_count}")
                print(f"Arquivo salvo: {self.results_file}")
                
                # Mostra algumas cidades como exemplo
                print(f"\nExemplo de dados coletados:")
                for i, (city, coords) in enumerate(list(self.cities_data.items())[:3]):
                    print(f"  {city}: {coords}")
                if len(self.cities_data) > 3:
                    print(f"  ... e mais {len(self.cities_data) - 3} cidades")
            else:
                logger.error("Falha ao salvar arquivo JSON")
        else:
            logger.warning("Nenhum dado foi coletado com sucesso")
        
        logger.info("Scraper finalizado")


def main():
    """Função principal"""
    scraper = SCCitiesScraper()
    scraper.run()


if __name__ == '__main__':
    main()