import cloudscraper
from bs4 import BeautifulSoup
import json

scraper = cloudscraper.create_scraper()

def scrapingGames(url):
    response = scraper.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', text=lambda x: x and 'window["initial_state"]' in x)
        
        if script_tag:
            script_content = script_tag.string
            json_start = script_content.find('{')
            json_end = script_content.rfind('}') + 1
            json_data = script_content[json_start:json_end]
            
            initial_state = json.loads(json_data)
            
            market_id = None
            for market in initial_state['data']['markets']:
                if 'Todos' in market['name']:
                    market_id = market['id']
                    break
            
            if market_id:
                response = scraper.get(url + f'?bt={market_id}')
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
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
                            
                            mercados = []
                            home_team = "Não encontrado"
                            away_team = "Não encontrado"
                            
                            if 'markets' in evento:
                                for market in evento['markets']:
                                    market_name = market.get('name', 'N/A')
                                    market_id = market.get('id', 'N/A')
                                    
                                    if market_name == 'Resultado Final':                    
                                        home_team = market['selections'][0]['fullName']
                                        away_team = market['selections'][2]['fullName']
                                    
                                    selecoes = []
                                    if 'selections' in market:
                                        for selection in market['selections']:
                                            selection_name = selection.get('name', 'N/A')
                                            selection_price = selection.get('price', 'N/A')
                                            
                                            selecoes.append({
                                                "Seleção": selection_name,
                                                "Preço": selection_price
                                            })
                                    
                                    if 'tableLayout' in market and 'rows' in market['tableLayout']:
                                        for row in market['tableLayout']['rows']:
                                            if 'groupSelections' in row:
                                                for group in row['groupSelections']:
                                                    if 'selections' in group:
                                                        for selection in group['selections']:
                                                            selection_name = selection.get('name', 'N/A')
                                                            selection_price = selection.get('price', 'N/A')
                                                            selection_handicap = selection.get('handicap', 'N/A')
                                                            
                                                            selecoes.append({
                                                                "Seleção": f"{selection_name} (Handicap: {selection_handicap})",
                                                                "Preço": selection_price
                                                            })
                                    
                                    mercados.append({
                                        "Mercado": market_name,
                                        "ID": market_id,
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
                    print(f"Erro ao acessar a página com o ID do mercado: {response.status_code}")
                    print(response.text)
            else:
                print("ID do mercado 'Todos' não encontrado.")
        else:
            print("Script com JSON não encontrado.")
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

urls = ["https://www.betano.bet.br/odds/sampaio-correa-rj-vasco-da-gama/62837596/"]
resultados = scrapingLinks(urls)

for resultado in resultados:
    print(f"Jogo: {resultado['Jogo']}")
    print(f"Data: {resultado['Data']}")
    print(f"Home Team: {resultado['HomeTeam']}")
    print(f"Away Team: {resultado['AwayTeam']}")
    print("Mercados:")
    for mercado in resultado['Mercados']:
        print(f"  Mercado: {mercado['Mercado']} (ID: {mercado['ID']})")
        for selecao in mercado['Seleções']:
            print(f"    Seleção: {selecao['Seleção']}, Preço: {selecao['Preço']}")