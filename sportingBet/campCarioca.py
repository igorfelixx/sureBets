import requests

url = "https://sports.sportingbet.bet.br/pt-br/sports/api/widget/widgetdata?layoutSize=Medium&page=CompetitionLobby&sportId=4&regionId=33&competitionId=102137&compoundCompetitionId=2:102137&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer&shouldIncludePayload=true"

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
	"Accept": "application/json",
	"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
	"Referer": "https://sports.sportingbet.bet.br/",
}

response = requests.get(url, headers=headers)

def campCarioca() :
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

			print("\n") 
	else:
		print(f"Erro na requisição: {response.status_code}")
		print(f"Resposta do servidor: {response.text}")
    

	return jogos_data
