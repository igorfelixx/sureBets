from concurrent.futures import ThreadPoolExecutor, as_completed
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações
BASE_URL = "https://sports.sportingbet.bet.br"
MAX_WORKERS = 5  # Número máximo de threads para requisições paralelas
REQUEST_DELAY = 2  # Delay entre requisições (em segundos)

def fetch_page(url):
    """Função para buscar o conteúdo de uma página."""
    driver = Driver(uc=True, headless=True, incognito=True, block_images=True)
    try:
        driver.get(url)
        # Espera até que um elemento específico esteja presente na página
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/pt-br/sports/eventos"]'))
        )
        return driver.page_source
    except Exception as e:
        print(f"Erro ao carregar a página {url}: {e}")
        return None
    finally:
        driver.quit()

def extract_game_links(html_content):
    """Função para extrair links de jogos de uma página."""
    try:
        if not html_content:
            return []

        # Extrai links diretamente com Selenium (simulado aqui com BeautifulSoup)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        game_links = {
            BASE_URL + link['href']
            for link in soup.find_all('a', href=True)
            if "/pt-br/sports/eventos" in link['href']
        }
        return list(game_links)
    except Exception as e:
        print(f"Erro ao extrair links dos jogos: {e}")
        return []

def main():
    # Busca o conteúdo da página principal
    html_content = fetch_page(BASE_URL)
    if not html_content:
        return []

    # Extrai os links dos jogos da página principal
    game_links = extract_game_links(html_content)
    print("Links dos jogos encontrados:", game_links)

    # Paraleliza a extração de dados das páginas dos jogos
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_page, link): link
            for link in game_links
        }

        results = []
        for future in as_completed(futures):
            link = futures[future]
            try:
                page_content = future.result()
                if page_content:
                    # Aqui você pode processar o conteúdo de cada página de jogo
                    results.append((link, page_content))
            except Exception as e:
                print(f"Erro ao processar a página {link}: {e}")

    print("Processamento concluído. Resultados:", results)

if __name__ == "__main__":
    main()