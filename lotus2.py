from playwright.sync_api import sync_playwright
import time
import os

def monitorar_e_comprar_automatico():
    # =========================================================================
    # CONFIGURAÇÃO DO DROPSNIPER
    # =========================================================================
    BARALHO_ALVO = "Arctic Lotus" 
    INTERVALO_CHEK_SEGUNDOS = 1.0  # Tempo de espera entre os recarregamentos (Seguro e rápido)
    # =========================================================================

    with sync_playwright() as p:
        caminho_perfil = os.path.expanduser("~/.config/google-chrome/Default")
        
        print(f"Abrindo navegador persistente...")
        print("LEMBRETE: Feche todas as janelas do Chrome antes de rodar!")
        
        # Reduzimos o slow_mo para 20ms para o robô agir na velocidade da luz após o drop
        context = p.chromium.launch_persistent_context(
            user_data_dir=caminho_perfil,
            headless=False,
            slow_mo=20, 
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        print(f"Iniciando monitoramento do produto: '{BARALHO_ALVO}'...")
        page.goto("https://lotusinhandstore.com/", wait_until="domcontentloaded")

        tentativas = 0
        while True:
            tentativas += 1
            print(f"\n[Tentativa {tentativas}] Verificando disponibilidade na Home...")
            
            try:
                # 1. Procura o link do produto na página inicial
                produto_link = page.get_by_text(BARALHO_ALVO, exact=False).first
                
                # Se o link não estiver visível (não lançou), força o erro para ir pro except
                if not produto_link.is_visible():
                    raise Exception("Produto ainda não apareceu na listagem.")
                
                print("-> Produto localizado na Home! Entrando na página...")
                produto_link.click()
                
                # 2. Aguarda a página do produto carregar e confere se o botão de compra está ativo
                # Procuramos o botão de adicionar que NÃO contenha textos de esgotado/indisponível
                print("-> Verificando se o estoque foi liberado...")
                
                # Espera o input de quantidade aparecer para garantir que a página carregou
                input_qtd = page.locator("input[name='quantity']")
                input_qtd.wait_for(state="visible", timeout=3000)
                
                # Se o botão disser "Sold Out" ou estiver desativado, o drop ainda não valeu
                botao_esgotado = page.locator("button:has-text('Sold Out'), button[disabled]").first
                if botao_esgotado.is_visible():
                    print("-> Botão 'Sold Out' detectado. Estoque ainda travado.")
                    raise Exception("Sold Out")

                # Se passou por todas as travas acima, significa que o PRODUTO ESTÁ DISPONÍVEL!
                print("-> ESTOQUE LIBERADO! Iniciando procedimentos de compra rápida...")
                break

            except Exception as e:
                # Se deu erro (não achou o produto ou está esgotado), recarrega a Home e tenta de novo
                print(f"-> Fora de estoque ou indisponível. Motivo: {e}")
                print(f"-> Aguardando {INTERVALO_CHEK_SEGUNDOS}s para evitar block antes de recarregar...")
                time.sleep(INTERVALO_CHEK_SEGUNDOS)
                
                # Volta para a home atualizando a página
                page.goto("https://lotusinhandstore.com/", wait_until="domcontentloaded")

        # =========================================================================
        # FASE DE EXECUÇÃO ULTRA-RÁPIDA (SAIU DO LOOP)
        # =========================================================================
        
        # 3. Altera quantidade
        try:
            input_qtd.fill("2")
        except:
            pass

        # 4. Clique agressivo no botão de compra
        print("-> Clicando no botão de compra...")
        botao_comprar = page.locator("button[name='add'], button:has-text('Add to cart'), button:has-text('Buy it now')").first
        botao_comprar.click()

        # 5. Redirecionamento instantâneo para o checkout da Shopify
        print("-> Direcionando para o Checkout...")
        time.sleep(2.0)

        if "checkout" not in page.url:
            page.goto("https://lotusinhandstore.com/checkout", wait_until="domcontentloaded")

        print(f"\n[ALVO ADQUIRIDO] Robô finalizou a missão. Assuma o controle para pagar!")
        
        # Mantém a janela aberta no seu perfil
        input("Pressione ENTER aqui no terminal para fechar o navegador quando terminar...")
        context.close()

if __name__ == "__main__":
    monitorar_e_comprar_automatico()