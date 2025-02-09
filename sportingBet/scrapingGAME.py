import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://sports.sportingbet.bet.br/",
}

def campCarioca(sourceID):
    
    all_jogos_data = []
    for id in sourceID:
        url = f'https://sports.sportingbet.bet.br/cds-api/bettingoffer/fixture-view?x-bwin-accessid=YTRhMjczYjctNTBlNy00MWZlLTliMGMtMWNkOWQxMThmZTI2&lang=pt-br&country=BR&userCountry=BR&offerMapping=All&scoreboardMode=Full&fixtureIds=2:{id['SourceID']}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=true&isBettingInsightsEnabled=false&useRegionalisedConfiguration=true&includeRelatedFixtures=false&statisticsModes=None' 
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Acessa os dados do fixture
            fixture = data.get('fixture', {})
            
            # Extrai informações básicas do jogo
            jogo = f"{fixture.get('participants', [{}])[0].get('name', {}).get('value', 'N/A')} vs {fixture.get('participants', [{}])[1].get('name', {}).get('value', 'N/A')}"
            data_jogo = fixture.get('startDate', 'N/A')
            home_team = fixture.get('participants', [{}])[0].get('name', {}).get('value', 'N/A')
            away_team = fixture.get('participants', [{}])[1].get('name', {}).get('value', 'N/A')
            
            # Extrai os mercados de apostas
            mercados = []
            for market in fixture.get('optionMarkets', []):
                market_name = market.get('name', {}).get('value', 'N/A')
                
                selecoes = []
                for option in market.get('options', []):
                    selection_name = option.get('name', {}).get('value', 'N/A')
                    selection_price = option.get('price', {}).get('odds', 'N/A')
                    
                    selecoes.append({
                        "Seleção": selection_name,
                        "Preço": selection_price
                    })
                
                mercados.append({
                    "Mercado": market_name,
                    "Seleções": selecoes
                })
            
            # Adiciona os dados do jogo à lista
            all_jogos_data.append({
                "Jogo": jogo,
                "Data": data_jogo,
                "HomeTeam": home_team,
                "AwayTeam": away_team,
                "Mercados": mercados
            })
        else:
            print(f"Erro na requisição para {url}: {response.status_code}")
            print(f"Resposta do servidor: {response.text}")
    return all_jogos_data
