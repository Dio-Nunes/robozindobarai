from playwright.sync_api import sync_playwright
import time
import os

def monitorar_e_comprar_automatico():
    # =========================================================================
    # CONFIGURAÇÃO DO DROPSNIPER
    # =========================================================================
    BARALHO_ALVO = "Lotus #05" 
    INTERVALO_CHEK_SEGUNDOS = 1.0  # Tempo de espera entre os recarregamentos
    # =========================================================================

    with sync_playwright() as p:
        # Pega o caminho 'C:\Users\SEU_USUARIO\AppData\Local' dinamicamente no Windows
        # SUBSTITUA A PARTE DO APPDATA POR ISSO:
        # Coloque o nome do seu usuário do Windows exatamente como está na pasta C:\Users
        NOME_USUARIO_WINDOWS = "dionisio.nunes"  # <-- Mude aqui!
        
        caminho_perfil = f"C:\\Users\\{NOME_USUARIO_WINDOWS}\\AppData\\Local\\Google\\Chrome\\User Data"
        
        print(f"Abrindo navegador persistente no Windows...")
        print("=" * 70)
        print(f"Caminho do perfil configurado: {caminho_perfil}")
        print("AVISO CRÍTICO PARA WINDOWS:")
        print("Feche COMPLETAMENTE todas as janelas do seu Google Chrome antes de rodar!")
        print("=" * 70)
        
        try:
            # Iniciando o contexto persistente adaptado para Windows
            context = p.chromium.launch_persistent_context(
                user_data_dir=caminho_perfil,
                channel="chrome",  # Força a usar o Google Chrome instalado no seu Windows
                headless=False,
                slow_mo=20,        # Velocidade da luz pós-drop
                viewport={'width': 1280, 'height': 800},
                ignore_https_errors=True
            )
        except Exception as erro_abertura:
            print(f"\n[ERRO AO ABRIR O CHROME]: {erro_abertura}")
            print("Provavelmente existe alguma aba do Chrome aberta no seu Windows em segundo plano.")
            return
        
        # Recupera a página atual ou cria uma nova se necessário
        page = context.pages[0] if context.pages else context.new_page()

        print(f"\nIniciando monitoramento do produto: '{BARALHO_ALVO}'...")
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
        input("\nPressione ENTER aqui no terminal para fechar o navegador quando terminar...")
        context.close()

if __name__ == "__main__":
    monitorar_e_comprar_automatico()