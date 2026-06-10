from playwright.sync_api import sync_playwright
import requests
import time
import random

def checar_link(url):
    """Verifica se o link está quebrado sem precisar abrir o navegador"""
    try:
        resposta = requests.head(url, timeout=5, allow_redirects=True)
        return resposta.status_code ==200
    except Exception:
        return False

def executar_poc_tce():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        print("Acessando o Portal do TCE-Ap...")
        page.goto("https://www.tce.ap.gov.br/transparencia", wait_until="domcontentloaded")

        #simulação de user
        #1 interação com filtro de Ano (Exemplificar)
        #page.select_option("select#ano", value="2025")
        time.sleep(random.uniform(1.0,2.5))

        #2 clicar no botão de busca/filtro
        #page.click("button#buscar")
        #page.wait_for_load_state("networkidle")

        links_elementos = page.locator("a").all()
        urls_para_testar = []

        for el in links_elementos:
            href = el.get_attribute ("href")
            if href and ("transparencia" in href or href.endswith(".pdf")):
                urls_para_testar.append(href)

        print(f"encontrados {len(urls_para_testar)} links. Iniciando validação de integridade...")

        for url in urls_para_testar[:10]:
            valido = checar_link(url)
            status = "OK" if valido else "QUEBRADO/ERRO"
            print(f"link: {url} -> {status}")
            time.sleep(random.uniform(0.5,1.5))

        browser.close()

if __name__ == "__main__":
    executar_poc_tce()