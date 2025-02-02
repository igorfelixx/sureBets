from marketMaking import main

def encontrar_surebets(dados):
    surebets = []

    for jogo in dados:
        mercado = jogo['Mercado']
        comparacoes = jogo['Comparações']

        if mercado == 'Total de Gols':
            for comparacao in comparacoes:
                selecao = comparacao['Seleção']
                sportingbet_odds = comparacao.get('SportingBet', None)
                betano_odds = comparacao.get('Betano', None)

                if "Mais" in selecao and "Menos" in selecao:
                    continue  

                oposta_selecao = "Menos de " + selecao.split(" ")[-1] if "Mais" in selecao else "Mais de " + selecao.split(" ")[-1]
                oposta_comparacao = next((c for c in comparacoes if c['Seleção'] == oposta_selecao), None)

                if oposta_comparacao:
                    oposta_sportingbet_odds = oposta_comparacao.get('SportingBet', None)
                    oposta_betano_odds = oposta_comparacao.get('Betano', None)

                    if sportingbet_odds and oposta_betano_odds:
                        surebet = calcular_surebet(sportingbet_odds, oposta_betano_odds)
                        if surebet:
                            surebets.append({
                                'Jogo': jogo['Jogo'],
                                'Mercado': mercado,
                                'Seleção 1': selecao,
                                'Casa 1': 'SportingBet',
                                'Odd 1': sportingbet_odds,
                                'Seleção 2': oposta_selecao,
                                'Casa 2': 'Betano',
                                'Odd 2': oposta_betano_odds,
                                'Lucro Garantido (%)': surebet
                            })

                    if betano_odds and oposta_sportingbet_odds:
                        surebet = calcular_surebet(betano_odds, oposta_sportingbet_odds)
                        if surebet:
                            surebets.append({
                                'Jogo': jogo['Jogo'],
                                'Mercado': mercado,
                                'Seleção 1': selecao,
                                'Casa 1': 'Betano',
                                'Odd 1': betano_odds,
                                'Seleção 2': oposta_selecao,
                                'Casa 2': 'SportingBet',
                                'Odd 2': oposta_sportingbet_odds,
                                'Lucro Garantido (%)': surebet
                            })

        elif mercado == 'Resultado da Partida - VP (+2)':
            print('Time1: ',comparacoes[0], "|||")
            print('Time2: ',comparacoes[2], "|||")
            if len(comparacoes) == 3: 
                time1 = comparacoes[0]
                empate = comparacoes[1]
                time2 = comparacoes[2]
                if time1['SportingBet'] and time2['Betano']:
                    surebet = calcular_surebet3(time1['SportingBet'], time2['Betano'], empate)
                    if surebet:
                        surebets.append({
                            'Jogo': jogo['Jogo'],
                            'Mercado': mercado,
                            'Seleção 1': time1['Seleção'],
                            'Casa 1': 'SportingBet',
                            'Odd 1': time1['SportingBet'],
                            'Seleção 2': time2['Seleção'],
                            'Casa 2': 'Betano',
                            'Odd 2': time2['Betano'],
                            'Casa 3': 'Betano' if empate['Betano'] > empate['SportingBet'] else 'SportingBet',
                            'Seleção 3': empate['Seleção'],
                            'Odd 3': empate['Betano'] if empate['Betano'] > empate['SportingBet'] else empate['SportingBet'],
                            'Lucro Garantido (%)': surebet
                        })

                elif time1['Betano'] and time2['SportingBet']:
                    surebet = calcular_surebet3(time1['Betano'], time2['SportingBet'], empate)
                    if surebet:
                        surebets.append({
                            'Jogo': jogo['Jogo'],
                            'Mercado': mercado,
                            'Seleção 1': time1['Seleção'],
                            'Casa 1': 'Betano',
                            'Odd 1': time1['Betano'],
                            'Seleção 2': time2['Seleção'],
                            'Casa 2': 'SportingBet',
                            'Odd 2': time2['SportingBet'],
                            'Casa 3': 'Betano' if empate['Betano'] > empate['SportingBet'] else 'SportingBet',
                            'Seleção 3': empate['Seleção'],
                            'Odd 3': empate['Betano'] if empate['Betano'] > empate['SportingBet'] else empate['SportingBet'],
                            'Lucro Garantido (%)': surebet
                        })

    return surebets


def calcular_surebet(odd1, odd2):
    inverso_total = (1 / odd1) + (1 / odd2)
    if inverso_total < 1:
        return round((1 - inverso_total) * 100, 2)
    return None

def calcular_surebet3(odd1, odd2, odd3):
    if odd3['SportingBet'] > odd3 ['Betano']:
        odd3 = odd3['SportingBet']
    else: 
        odd3 = odd3['Betano']
        
    inverso_total = (1 / odd1) + (1 / odd2) + (1 / odd3)
    if inverso_total < 1:
        return round((1 - inverso_total) * 100, 2)
    return None




dados = main()
surebets = encontrar_surebets(dados)

if surebets:
    print("Oportunidades de SureBets encontradas:")
    for surebet in surebets:
        print(f"Jogo: {surebet['Jogo']}")
        print(f"Mercado: {surebet['Mercado']}")
        print(f"Seleção 1: {surebet['Seleção 1']} (Odd: {surebet['Odd 1']}) em {surebet['Casa 1']}")
        print(f"Seleção 2: {surebet['Seleção 2']} (Odd: {surebet['Odd 2']}) em {surebet['Casa 2']}")
        print(f"Seleção 3: {surebet['Seleção 3']} (Odd: {surebet['Odd 3']}) em {surebet['Casa 3']}")
        print(f"Lucro Garantido: {surebet['Lucro Garantido (%)']}%")
        print("-" * 50)
else:
    print("Nenhuma oportunidade de SureBet encontrada.")