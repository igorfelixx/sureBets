import requests

# Lista de URLs
urls = [
    "https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Medium&page=CompetitionLobby&sportId=4&regionId=33&competitionId=102137&compoundCompetitionId=2:102137&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true",  # Carioca
    "https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Medium&page=CompetitionLobby&sportId=4&regionId=33&competitionId=102148&compoundCompetitionId=2:102148&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true",  # Paulista
    "https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=14&competitionId=102841&compoundCompetitionId=2:102841&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true",  # Premier League
	"https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=28&competitionId=102829&compoundCompetitionId=2:102829&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true", # La Liga
	"https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=20&competitionId=102846&compoundCompetitionId=2:102846&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true", # Seria A (Intaliana)
	"https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=17&competitionId=102842&compoundCompetitionId=2:102842&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true", # BundesLiga
	"https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=16&competitionId=102843&compoundCompetitionId=2:102843&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true", # Ligue 1
	"https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Small&page=CompetitionLobby&sportId=4&regionId=38&competitionId=102540&compoundCompetitionId=2:102540&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true", # Campeonato Argentino
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://sports.sportingbet.bet.br/",
}

def campCarioca():
    all_jogos_data = []
    
    for url in urls:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            jogos_data = []
            data = response.json()
            fixtures = data['widgets'][0]['payload']['items'][0]['activeChildren'][0]['payload']['fixtures']

            for fixture in fixtures:
                team1 = fixture['participants'][0]['name']['value']
                team2 = fixture['participants'][1]['name']['value']
                start_date = fixture['startDate']

                mercados = []

                for market in fixture['optionMarkets']:
                    market_name = market['name']['value']

                    selecoes = []

                    for option in market['options']:
                        option_name = option['name']['value']
                        odds = option['price']['odds']

                        selecoes.append({
                            "Seleção": option_name,
                            "Preço": odds
                        })

                    mercados.append({
                        "Mercado": market_name,
                        "Seleções": selecoes
                    })

                jogos_data.append({
                    "Jogo": f"{team1} vs {team2}",
                    "Data": start_date,
                    "HomeTeam": team1,
                    "AwayTeam": team2,
                    "Mercados": mercados
                })

            all_jogos_data.extend(jogos_data)
        else:
            print(f"Erro na requisição para {url}: {response.status_code}")
            print(f"Resposta do servidor: {response.text}")
    
    return all_jogos_data
