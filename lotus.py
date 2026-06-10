from playwright.sync_api import sync_playwright
import time
import os

def monitorar_e_comprar_automatico():
    # =========================================================================
    # CONFIGURAÇÃO: Digite aqui o nome do baralho que o robô deve buscar na Home
    # =========================================================================
    BARALHO_ALVO = "Arctic Lotus" 
    # =========================================================================

    with sync_playwright() as p:
        
        # Caminho padrão do perfil do Chrome/Chromium no Linux Ubuntu
        caminho_perfil = os.path.expanduser("~/.config/google-chrome/Default")
        
        print(f"Abrindo o navegador usando seu perfil: {caminho_perfil}")
        print("LEMBRETE: Certifique-se de fechar as janelas do Chrome antes de rodar!")
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=caminho_perfil,
            headless=False,
            slow_mo=100,
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        # 1. Acessa a página inicial da loja automaticamente
        print(f"Acessando a página inicial da Lotus in Hand para buscar o '{BARALHO_ALVO}'...")
        page.goto("https://lotusinhandstore.com/", wait_until="domcontentloaded")
        time.sleep(2.0)

        # 2. Localiza o texto que você configurou acima e clica nele
        print(f"Varrendo a página em busca do texto: '{BARALHO_ALVO}'...")
        try:
            # exact=False ignora se você escreveu com maiúsculas ou minúsculas diferentes do site
            produto_link = page.get_by_text(BARALHO_ALVO, exact=False).first
            produto_link.wait_for(state="visible", timeout=10000)
            
            print(f"Sucesso! Clicando no link para abrir a página do produto...")
            produto_link.click()
        except Exception:
            print(f"\n[ERRO] Não foi possível encontrar o baralho '{BARALHO_ALVO}' de forma automática.")
            print("Verifique se o nome está escrito corretamente no topo do código ou se ele está na Home.")
            context.close()
            return

        # 3. Altera a quantidade para 2 unidades
        print("Ajustando a quantidade para 2 unidades...")
        try:
            input_qtd = page.locator("input[name='quantity']")
            input_qtd.wait_for(state="visible", timeout=5000)
            input_qtd.fill("4")
        except Exception:
            print("[AVISO] Campo de quantidade não localizado. Avançando...")

        # 4. Adiciona ao carrinho / Inicia a compra
        print("Clicando no botão de compra...")
        botao_comprar = page.locator("button[name='add'], button:has-text('Add to cart'), button:has-text('Buy it now')").first
        botao_comprar.click()

        # 5. Redireciona diretamente para o checkout da Shopify
        print("Aguardando o redirecionamento do e-commerce...")
        time.sleep(3.0)

        if "checkout" not in page.url:
            print("Forçando redirecionamento manual para a rota de Checkout...")
            page.goto("https://lotusinhandstore.com/checkout", wait_until="domcontentloaded")

        print(f"\n[PRONTO] {BARALHO_ALVO} adicionado com sucesso! Tela de pagamento liberada.")
        
        # Mantém a janela aberta no seu perfil para você preencher os dados finais
        input("Pressione ENTER aqui no terminal para encerrar o robô após finalizar a compra...")
        context.close()

if __name__ == "__main__":
    monitorar_e_comprar_automatico()