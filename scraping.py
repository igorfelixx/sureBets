from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from scrapLinks import extract_game_links

import time

driver = Driver(uc=True, headless=True, incognito=True)

links_dos_jogos = extract_game_links()

print(links_dos_jogos)

driver.get(links_dos_jogos[0])

time.sleep(20)

html_content = driver.page_source

driver.quit()

soup = BeautifulSoup(html_content, 'html.parser')

# Função para extrair as odds de um mercado específico
def extract_odds(market_name):
    # Encontrar o painel de opções pelo nome do mercado
    market_panel = soup.find('span', class_='market-name', string=market_name)
    if not market_panel:
        return None

    # Navegar até o container das odds
    odds_container = market_panel.find_parent('ms-option-panel').find('div', class_='option-group-container')
    if not odds_container:
        return None

    # Extrair as odds
    odds = {}
    for option in odds_container.find_all('ms-option'):
        name = option.find('div', class_='name').text.strip()
        value = option.find('span', class_='custom-odds-value-style').text.strip()
        odds[name] = value

    return odds

# Extrair as odds para cada mercado
resultado_partida = extract_odds("Resultado da Partida")
ambos_marcam = extract_odds("Ambas Marcam")

# Exibir os resultados
print("Resultado da Partida:", resultado_partida)
print("Ambos Marcam:", ambos_marcam)