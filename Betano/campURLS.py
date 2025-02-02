import cloudscraper
from bs4 import BeautifulSoup
import json

# Lista de URLs
urls = [
    "https://www.betano.bet.br/sport/futebol/brasil/campeonato-carioca-serie-a/16880/",  # Campeonato Carioca Série A
    "https://www.betano.bet.br/sport/futebol/brasil/campeonato-paulista-serie-a1/16901/",  # Campeonato Paulista Série A1
    "https://www.betano.bet.br/sport/futebol/inglaterra/premier-league/1/",  # Premier League
]

scraper = cloudscraper.create_scraper()

def extract_links():
    all_game_links = []
    
    for url in urls:
        response = scraper.get(url)
        game_links = []
        
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            script_tag = soup.find('script', type='application/ld+json')
            
            if script_tag:
                json_data = script_tag.string
                
                eventos = json.loads(json_data)
                
                for evento in eventos:
                    nome = evento.get('name')
                    data = evento.get('startDate')
                    time_casa = evento.get('homeTeam', {}).get('name')
                    time_visitante = evento.get('awayTeam', {}).get('name')
                    url_evento = evento.get('url')
                    
                    if url_evento not in game_links:
                        game_links.append(url_evento)
                
                all_game_links.extend(game_links)
            else:
                print(f"Script com JSON não encontrado para {url}.")
        else:
            print(f"Erro ao acessar a página {url}: {response.status_code}")
            print(response.text)
    
    return all_game_links