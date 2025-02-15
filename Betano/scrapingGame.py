import cloudscraper
from bs4 import BeautifulSoup
import json

scraper = cloudscraper.create_scraper()

def scrapingGames(url):
    response = scraper.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', type='application/ld+json')
        
        if script_tag:
            script_tag = soup.find('script', text=lambda x: x and 'window["initial_state"]' in x)
            if script_tag:
                script_content = script_tag.string
                json_start = script_content.find('{')
                json_end = script_content.rfind('}') + 1
                json_data = script_content[json_start:json_end]
                
                initial_state = json.loads(json_data)
                
                if 'data' in initial_state and 'event' in initial_state['data']:
                    evento = initial_state['data']['event']
                    
                    jogo = evento.get('name', 'N/A')
                    data = evento.get('startTime', 'N/A')
                    
                    if 'homeTeam' in evento and 'awayTeam' in evento:                        
                        home_team = evento.get('homeTeam', {}).get('name', 'N/A')
                        away_team = evento.get('awayTeam', {}).get('name', 'N/A')
                    else:
                        home_team = "Não Encontrado"
                        away_team = "Não Encontrado"
                    
                    mercados = []
                    if 'markets' in evento:
                        for market in evento['markets']:
                            
                            market_name = market.get('name', 'N/A')

                            selecoes = []
                            
                            for selection in market['selections']:
                                selection_name = selection.get('name', 'N/A')
                                selection_price = selection.get('price', 'N/A')
                                
                                selecoes.append({
                                    "Seleção": selection_name,
                                    "Preço": selection_price
                                })
                            
                            mercados.append({
                                "Mercado": market_name,
                                "Seleções": selecoes
                            })
                    else:
                        print("Nenhum mercado encontrado.")
                    return {
                        "Jogo": jogo,
                        "Data": data,
                        "HomeTeam": home_team,
                        "AwayTeam": away_team,
                        "Mercados": mercados 
                    }
                else:
                    print("Dados do evento não encontrados.")
            else:
                print("Script com JSON não encontrado.")
        else:
            print("Não encontrou o Script... Tentando novamente...")
    else:
        print(f"Erro ao acessar a página: {response.status_code}")
        print(response.text)
        
def scrapingLinks(urls):
    all_games_data = []
    for url in urls:
        gamesData = scrapingGames(url)
        if gamesData:
            all_games_data.append(gamesData)
    return all_games_data
        