from playwright.sync_api import sync_playwright
import time
import random

def executar_poc_tce():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True  # Diz ao Playwright para aceitar os certificados do TCE-AP
        )
        page = context.new_page()

        print("Acessando o Portal do TCE-AP...")
        page.goto("https://www.tce.ap.gov.br/transparencia", wait_until="domcontentloaded")

        time.sleep(random.uniform(1.0, 2.5)) 

        # --- CAPTURA E FILTRAGEM DE LINKS ---
        links_elementos = page.locator("a").all()
        urls_para_testar = []

        for el in links_elementos:
            href = el.get_attribute("href")
            if href:
                # 1. Remove espaços em branco nas pontas que possam quebrar a URL
                href = href.strip()
                
                # 3. Corrige links relativos (ex: /transparencia ou /arquivos/documento.pdf)
                if href.startswith("/"):
                    href = f"https://www.tce.ap.gov.br{href}"
                
                # 4. NOVA REGRA: Aceita o link se ele for da Transparência OU se terminar com .pdf
                if "tce.ap.gov.br/transparencia" in href or href.lower().endswith(".pdf"):
                    # Evita duplicar URLs na lista de testes
                    if href not in urls_para_testar:
                        urls_para_testar.append(href)

        print(f"Encontrados {len(urls_para_testar)} links válidos (Páginas e PDFs da Transparência).")
        print("Iniciando validação de integridade nativa...")

        # --- VALIDAÇÃO DOS LINKS COLETADOS ---
        # Remova o '[:10]' quando quiser testar a lista inteira de uma vez
        for url in urls_para_testar[:10]: 
            motivo_erro = ""
            try:
                resposta = page.request.get(url, timeout=10000)
                
                if resposta.status == 200:
                    status = "✓ OK"
                else:
                    status = "✗ QUEBRADO/ERRO"
                    motivo_erro = f"[Status HTTP: {resposta.status}]"
                    
            except Exception as e:
                status = "✗ QUEBRADO/ERRO"
                motivo_erro = f"[Exceção de Rede: {str(e).splitlines()[0]}]"
                
            if motivo_erro:
                print(f"Link: {url} -> {status} {motivo_erro}")
            else:
                print(f"Link: {url} -> {status}")
            
            time.sleep(random.uniform(0.5, 1.5))

        browser.close()

if __name__ == "__main__":
    executar_poc_tce()