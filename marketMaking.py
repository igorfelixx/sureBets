import json
from Betano.scrapingGame import scrapingLinks
from sportingBet.campCarioca import campCarioca
from Betano.campURLS import extract_links
from unidecode import unidecode 

urls = extract_links()

market_mapping = { # Betano é o da esquerda, SportingBet é a da direita
    "resultadofinal": "resultadodapartidavp(+2)", 
    "totaldegolsmais/menos(alternativas)": "totaldegols",
    # "ambasequipesmarcam": "ambasmarcam",  
    # "chancedupla": "chancedupla",
    # "resultadofinal/totaldegols(2.5)": "resultadodojogoetotaldegols2,5"
}

def map_selection(selection, home_team, away_team):
    if selection == home_team:
        return "1"  # Time da casa
    elif selection == away_team:
        return "2"  # Time visitante
    elif selection == "X":
        return "x"  # Empate
    return selection  

def normalize_name(name):
    name = unidecode(name)
    return name.lower().strip().replace(" ", "").replace("-", "").replace(":", "")

def normalize_market(market):
    market = unidecode(market)
    return market.lower().strip().replace(" ", "").replace("-", "").replace(":", "").replace(",", "").replace(".","")

def compare_markets(sportingbet_market, betano_market, home_team, away_team):
    comparisons = []
    for sportingbet_option in sportingbet_market['Seleções']:
        for betano_option in betano_market['Seleções']:
            
            mapped_selection = map_selection(sportingbet_option['Seleção'], home_team, away_team)
            sportingbet_selection = normalize_name(sportingbet_option['Seleção'])
            betano_selection = normalize_name(betano_option['Seleção'])
            
            if "totaldegols" in normalize_name(sportingbet_market['Mercado']):
                if "maisde" in sportingbet_selection and "maisde" in betano_selection:
                    if normalize_market(sportingbet_selection) == normalize_market(betano_selection):
                        sportingbet_odds = sportingbet_option['Preço']
                        betano_odds = betano_option['Preço']
                        difference = abs(sportingbet_odds - betano_odds)
                        comparisons.append({
                            "Seleção": sportingbet_option['Seleção'],
                            "SportingBet": sportingbet_odds,
                            "Betano": betano_odds,
                            "Diferença": difference
                        })
                elif "menosde" in sportingbet_selection and "menosde" in betano_selection:
                    if normalize_market(sportingbet_selection) == normalize_market(betano_selection):
                        sportingbet_odds = sportingbet_option['Preço']
                        betano_odds = betano_option['Preço']
                        difference = abs(sportingbet_odds - betano_odds)
                        comparisons.append({
                            "Seleção": sportingbet_option['Seleção'],
                            "SportingBet": sportingbet_odds,
                            "Betano": betano_odds,
                            "Diferença": difference
                        })
            
            if mapped_selection == normalize_name(betano_option['Seleção']):
                sportingbet_odds = sportingbet_option['Preço']
                betano_odds = betano_option['Preço']
                difference = abs(sportingbet_odds - betano_odds)
                comparisons.append({
                    "Seleção": sportingbet_option['Seleção'],
                    "SportingBet": sportingbet_odds,
                    "Betano": betano_odds,
                    "Diferença": difference
                })
    return comparisons

def compare_games(sportingbet_data, betano_data):
    results = []
    for sportingbet_game in sportingbet_data:
        for betano_game in betano_data:
            if (normalize_name(sportingbet_game['HomeTeam']) in normalize_name(betano_game['Jogo']) and 
                normalize_name(sportingbet_game['AwayTeam']) in normalize_name(betano_game['Jogo'])):
                
                home_team = sportingbet_game['HomeTeam']  
                away_team = sportingbet_game['AwayTeam']  
                
                for sportingbet_market in sportingbet_game['Mercados']:
                    for betano_market in betano_game['Mercados']:
                        sportingbet_market_name = normalize_name(sportingbet_market['Mercado'])
                        betano_market_name = normalize_name(betano_market['Mercado'])
                        
                        if (market_mapping.get(betano_market_name) == sportingbet_market_name):
                            comparisons = compare_markets(sportingbet_market, betano_market, home_team, away_team)
                            
                            results.append({
                                "Jogo": sportingbet_game['Jogo'],
                                "Mercado": sportingbet_market['Mercado'],
                                "Comparações": comparisons
                            })
    return results

def main():
    sportingbet_data = campCarioca()  
    betano_data = scrapingLinks(urls) 

    comparison_results = compare_games(sportingbet_data, betano_data)
    return comparison_results

if __name__ == "__main__":
    main()