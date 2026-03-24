import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import argparse
import os
from urllib.parse import urljoin

ESTADOS_BR = {
    "AC": ("Acre",              "Acre"),
    "AL": ("Alagoas",           "Alagoas"),
    "AP": ("Amapá",             "Amapá"),
    "AM": ("Amazonas",          "Amazonas"),
    "BA": ("Bahia",             "Bahia"),
    "CE": ("Ceará",             "Ceará"),
    "DF": ("Distrito Federal",  "Distrito-Federal"),
    "ES": ("Espírito Santo",    "Espírito-Santo"),
    "GO": ("Goiás",             "Goiás"),
    "MA": ("Maranhão",          "Maranhão"),
    "MT": ("Mato Grosso",       "Mato-Grosso"),
    "MS": ("Mato Grosso do Sul","Mato-Grosso-do-Sul"),
    "MG": ("Minas Gerais",      "Minas-Gerais"),
    "PA": ("Pará",              "Pará"),
    "PB": ("Paraíba",           "Paraíba"),
    "PR": ("Paraná",            "Paraná"),
    "PE": ("Pernambuco",        "Pernambuco"),
    "PI": ("Piauí",             "Piauí"),
    "RJ": ("Rio de Janeiro",    "Rio-de-Janeiro"),
    "RN": ("Rio Grande do Norte","Rio-Grande-do-Norte"),
    "RS": ("Rio Grande do Sul", "Rio-Grande-do-Sul"),
    "RO": ("Rondônia",          "Rondônia"),
    "RR": ("Roraima",           "Roraima"),
    "SC": ("Santa Catarina",    "Santa-Catarina"),
    "SP": ("São Paulo",         "São-Paulo"),
    "SE": ("Sergipe",           "Sergipe"),
    "TO": ("Tocantins",         "Tocantins"),
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BrazilCitiesScraper:
    BASE_URL = 'https://pt.db-city.com'

    def __init__(self, sigla: str, output_dir: str = 'resultados'):
        sigla = sigla.upper()
        if sigla not in ESTADOS_BR:
            raise ValueError(
                f"Sigla '{sigla}' inválida. Use uma das: {', '.join(sorted(ESTADOS_BR))}"
            )

        self.sigla = sigla
        self.state_name, self.state_slug = ESTADOS_BR[sigla]
        self.start_url = f"{self.BASE_URL}/Brasil--{self.state_slug}"
        self.cities_data = {}
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.results_file = os.path.join(
            self.output_dir,
            f"{self.state_slug.lower().replace('-', '_')}_cities.json"
        )

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def get_city_links(self):
        try:
            logger.info(f"[{self.sigla}] Acessando: {self.start_url}")
            response = self.session.get(self.start_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            city_links = []

            # Fonte 1: tabela completa de cidades
            table = soup.find('table', class_='td25 otd')
            if table:
                for link in table.find_all('a', href=True):
                    city_name = link.get_text(strip=True)
                    full_url = urljoin(self.BASE_URL, link['href'])
                    city_links.append((city_name, full_url))
                logger.info(f"[{self.sigla}] Tabela: {len(city_links)} cidades encontradas")
            else:
                # Fonte 2: parágrafo "Cidades importantes" como fallback
                logger.warning(f"[{self.sigla}] Tabela não encontrada, tentando 'Cidades importantes'...")
                intro = soup.find('p', id='intro_max')
                if intro:
                    for link in intro.find_all('a', href=True):
                        href = link['href']
                        # Ignora links de país/estado (só 2 segmentos depois de /)
                        if href.count('--') >= 2:
                            city_name = link.get('title') or link.get_text(strip=True)
                            full_url = urljoin(self.BASE_URL, href)
                            city_links.append((city_name, full_url))
                    logger.info(f"[{self.sigla}] Fallback: {len(city_links)} cidades importantes encontradas")
                else:
                    logger.error(f"[{self.sigla}] Nenhuma fonte de cidades encontrada na página!")

            return city_links

        except requests.RequestException as e:
            logger.error(f"[{self.sigla}] Erro ao acessar página: {e}")
            return []

    def get_city_coordinates(self, city_name, city_url):
        try:
            response = self.session.get(city_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            geo_cell = soup.find('td', class_='geo')
            if not geo_cell:
                logger.warning(f"[{self.sigla}] Geo não encontrado: {city_name}")
                return None

            latitude_elem = geo_cell.find('b', class_='latitude')
            longitude_elem = geo_cell.find('b', class_='longitude')
            if not latitude_elem or not longitude_elem:
                logger.warning(f"[{self.sigla}] Coordenadas incompletas: {city_name}")
                return None

            lat = float(latitude_elem.get_text(strip=True))
            lng = float(longitude_elem.get_text(strip=True))
            google_maps_format = f"@{lat},{lng},12.5z"

            logger.info(f"[{self.sigla}] {city_name}: {google_maps_format}")
            return google_maps_format

        except (requests.RequestException, ValueError) as e:
            logger.error(f"[{self.sigla}] Erro ao processar {city_name}: {e}")
            return None

    def save_to_json(self):
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.cities_data, f, ensure_ascii=False, indent=2)
            logger.info(f"[{self.sigla}] Salvo em {self.results_file}")
            return True
        except Exception as e:
            logger.error(f"[{self.sigla}] Erro ao salvar JSON: {e}")
            return False

    def run(self):
        logger.info(f"Iniciando scraper: {self.state_name} ({self.sigla})")

        city_links = self.get_city_links()
        if not city_links:
            logger.error(f"[{self.sigla}] Nenhuma cidade encontrada. Pulando...")
            return {}

        processed_count = 0
        total = len(city_links)

        for i, (city_name, city_url) in enumerate(city_links, 1):
            coordinates = self.get_city_coordinates(city_name, city_url)
            if coordinates:
                self.cities_data[city_name] = coordinates
                processed_count += 1

            if i % 50 == 0:
                logger.info(f"[{self.sigla}] Progresso: {i}/{total}")

            time.sleep(0.7)

        if self.cities_data:
            self.save_to_json()
            print(f"\n=== {self.state_name} ({self.sigla}) ===")
            print(f"  Cidades encontradas: {total}")
            print(f"  Processadas com sucesso: {processed_count}")
            print(f"  Arquivo: {self.results_file}")
        else:
            logger.warning(f"[{self.sigla}] Nenhum dado coletado")

        return self.cities_data


def consolidate_results(output_dir: str):
    """Junta todos os JSONs individuais em um único arquivo consolidado."""
    consolidated = {}
    for filename in sorted(os.listdir(output_dir)):
        if not filename.endswith('_cities.json') or filename == 'brasil_all_cities.json':
            continue
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        state_key = filename.replace('_cities.json', '').replace('_', ' ').title()
        consolidated[state_key] = data

    output_path = os.path.join(output_dir, 'brasil_all_cities.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in consolidated.values())
    print(f"\nConsolidado: {len(consolidated)} estados, {total} cidades → {output_path}")


def list_states():
    print("\nEstados disponíveis:")
    print("-" * 45)
    for sigla in sorted(ESTADOS_BR):
        nome, _ = ESTADOS_BR[sigla]
        print(f"  {sigla}  -  {nome}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Scraper de coordenadas de cidades brasileiras (db-city.com)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python scraper.py SC              # apenas Santa Catarina\n"
            "  python scraper.py SC PR RS        # vários estados\n"
            "  python scraper.py --todos         # todos os 27 estados\n"
            "  python scraper.py --todos --forcar# refaz todos mesmo que já existam\n"
            "  python scraper.py --listar        # mostra siglas disponíveis\n"
            "  python scraper.py SC -o dados     # salva na pasta 'dados'\n"
        )
    )
    parser.add_argument(
        'estados', nargs='*', metavar='SIGLA',
        help='Sigla(s) do(s) estado(s) (ex: SC, PR, SP)'
    )
    parser.add_argument(
        '--todos', action='store_true',
        help='Scrape todos os 27 estados do Brasil'
    )
    parser.add_argument(
        '--listar', action='store_true',
        help='Lista todas as siglas disponíveis'
    )
    parser.add_argument(
        '-o', '--output', default='resultados',
        help='Diretório de saída (padrão: resultados)'
    )
    parser.add_argument(
        '--consolidar', action='store_true',
        help='Consolida resultados existentes em um único JSON'
    )
    parser.add_argument(
        '--forcar', action='store_true',
        help='Refaz o scraping mesmo que o arquivo do estado já exista'
    )

    args = parser.parse_args()

    if args.listar:
        list_states()
        return

    if args.consolidar:
        consolidate_results(args.output)
        return

    if args.todos:
        siglas = sorted(ESTADOS_BR.keys())
    elif args.estados:
        siglas = [s.upper() for s in args.estados]
        invalid = [s for s in siglas if s not in ESTADOS_BR]
        if invalid:
            print(f"Siglas inválidas: {', '.join(invalid)}")
            list_states()
            return
    else:
        parser.print_help()
        return

    print(f"Estados a processar: {', '.join(siglas)}")
    print(f"Saída: {args.output}/\n")

    grand_total = 0
    skipped = []
    for i, sigla in enumerate(siglas, 1):
        scraper = BrazilCitiesScraper(sigla, output_dir=args.output)

        if not args.forcar and os.path.exists(scraper.results_file):
            with open(scraper.results_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            print(f"\n[{i}/{len(siglas)}] {ESTADOS_BR[sigla][0]} ({sigla}) — já existe ({len(cached)} cidades), pulando. Use --forcar para refazer.")
            grand_total += len(cached)
            skipped.append(sigla)
            continue

        print(f"\n[{i}/{len(siglas)}] Processando {ESTADOS_BR[sigla][0]} ({sigla})...")
        data = scraper.run()
        grand_total += len(data)

    if skipped:
        print(f"\nEstados pulados (já existiam): {', '.join(skipped)}")

    if len(siglas) > 1:
        consolidate_results(args.output)

    print(f"\nFinalizado! {grand_total} cidades processadas no total.")


if __name__ == '__main__':
    main()