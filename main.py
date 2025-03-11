import time
import json
import random
import sys
import signal
import traceback
import atexit  
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging

# Variável global para armazenar os resultados (para poder acessar no manipulador de sinal)
lojas_coletadas = []
driver = None

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_clean_arch.log"),
        logging.StreamHandler()
    ]
)

# Função para salvar os resultados atuais (chamada no manipulador de sinal)
def salvar_resultados(lojas_lista, sufixo="parcial"):
    try:
        if lojas_lista:
            print(f"\nInterrupção detectada. Salvando {len(lojas_lista)} lojas coletadas até agora...")
            
            # Limpar resultados para remover duplicados
            lojas_unicas = []
            nomes_vistos = set()
            
            for loja in lojas_lista:
                if loja['nome'] not in nomes_vistos:
                    lojas_unicas.append(loja)
                    nomes_vistos.add(loja['nome'])
            
            print(f"Total de lojas únicas após remoção de duplicados: {len(lojas_unicas)}")
            
            # Salva os resultados em um arquivo JSON
            nome_arquivo_json = f"lojas_oficiais_{sufixo}.json"
            with open(nome_arquivo_json, "w", encoding="utf-8") as f:
                json.dump(lojas_unicas, f, ensure_ascii=False, indent=4)
            
            print(f"Resultados {sufixo} salvos em '{nome_arquivo_json}'")
            
            # Salvar também como CSV para fácil importação em planilhas
            try:
                import csv
                nome_arquivo_csv = f"lojas_oficiais_{sufixo}.csv"
                with open(nome_arquivo_csv, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Nome", "Link"])
                    for loja in lojas_unicas:
                        writer.writerow([loja["nome"], loja["link"]])
                print(f"Resultados {sufixo} também salvos em '{nome_arquivo_csv}'")
                return True
            except Exception as e:
                print(f"Erro ao salvar CSV: {str(e)}")
                return False
        else:
            print("Nenhuma loja foi coletada antes da interrupção.")
            return False
    except Exception as e:
        print(f"Erro ao salvar dados: {str(e)}")
        return False

# Manipulador de sinal para quando o usuário pressionar Ctrl+C
def manipulador_interrupcao(sinal, frame):
    global lojas_coletadas, driver
    print("\n\nInterrupção detectada (Ctrl+C). Finalizando de forma limpa...")
    
    # Salvar os dados coletados até agora
    salvar_resultados(lojas_coletadas)
    
    # Fechar o navegador se estiver aberto
    if driver:
        try:
            print("Fechando o navegador...")
            driver.quit()
        except:
            pass
    
    print("Script finalizado pelo usuário.")
    sys.exit(0)

# Função para ser executada na saída do programa (independente da causa)
def finalizar_programa():
    global lojas_coletadas, driver
    print("\n\nFinalizando programa (função de saída de emergência)...")
    
    # Salvar dados coletados (usando sufixo diferente para não sobrescrever outros salvamentos)
    salvar_resultados(lojas_coletadas, "emergencia")
    
    # Fechar navegador se estiver aberto
    if driver:
        try:
            print("Fechando o navegador (limpeza de emergência)...")
            driver.quit()
        except:
            pass

def extrair_lojas_oficiais():
    global lojas_coletadas, driver
    url = "https://www.mercadolivre.com.br/lojas-oficiais/catalogo?"
    
    print(f"Configurando o navegador...")
    
    # Configurar as opções do Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Executar em modo headless (sem interface gráfica)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        # Inicializar o driver do Chrome
        print("Inicializando o navegador Chrome...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Adicionar um header personalizado para simular um navegador real
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })
        
        print(f"Acessando {url}")
        driver.get(url)
        
        # Esperar um pouco para a página carregar inicialmente
        time.sleep(5)
        
        # Verificar se há captcha ou outra proteção
        if "robot" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            print("Detectada possível proteção anti-bot (captcha).")
            print("Você precisa resolver o captcha manualmente...")
            
            # Salvar screenshot para debug
            driver.save_screenshot("captcha_screen.png")
            print("Screenshot salvo como 'captcha_screen.png'")
            
            # Esperar até que o usuário resolva o captcha
            print("*" * 70)
            print("IMPORTANTE: Vá até a janela do navegador Chrome que foi aberta e resolva o captcha.")
            print("Você tem 3 minutos para resolver o captcha.")
            print("Depois de resolver, o script continuará automaticamente.")
            print("*" * 70)
            
            # Dê ao usuário tempo para resolver o captcha, sem precisar pressionar Enter
            captcha_solved = False
            start_time = time.time()
            captcha_timeout = 180  # 3 minutos para resolver o captcha
            
            while not captcha_solved and (time.time() - start_time) < captcha_timeout:
                time.sleep(5)  # Verificar a cada 5 segundos
                
                # Verificar se o captcha foi resolvido
                if "robot" not in driver.page_source.lower() and "captcha" not in driver.page_source.lower():
                    captcha_solved = True
                    print("Captcha parece ter sido resolvido. Continuando...")
                else:
                    print("Aguardando resolução do captcha... Tempo restante: {:.0f} segundos".format(
                        captcha_timeout - (time.time() - start_time)))
            
            if not captcha_solved:
                print("Tempo esgotado para resolver o captcha. Tentando continuar mesmo assim...")
        
        # Permitir que a página termine de carregar após o captcha
        print("Aguardando carregamento completo da página...")
        time.sleep(10)
        
        # Resultado para armazenar os elementos encontrados
        lojas = []
        
        # Função para extrair elementos com classe "name"
        def extrair_elementos_name():
            print("Extraindo elementos com classe 'name'...")
            
            # Tentar diferentes estratégias para encontrar os elementos
            elementos = []
            
            # Estratégia 1: Classe name direta
            elements_by_class = driver.find_elements(By.CLASS_NAME, "name")
            if elements_by_class:
                print(f"Encontrados {len(elements_by_class)} elementos pela classe 'name'")
                elementos.extend(elements_by_class)
            
            # Estratégia 2: CSS Selector para elementos com classe name
            elements_by_css = driver.find_elements(By.CSS_SELECTOR, ".name")
            if elements_by_css:
                for elem in elements_by_css:
                    if elem not in elementos:
                        elementos.append(elem)
                print(f"Encontrados {len(elements_by_css)} elementos pelo CSS selector '.name'")
            
            # Estratégia 3: Atributos que contenham a classe name (para classes compostas)
            elements_by_contains = driver.find_elements(By.CSS_SELECTOR, "[class*='name']")
            if elements_by_contains:
                for elem in elements_by_contains:
                    if elem not in elementos:
                        elementos.append(elem)
                print(f"Encontrados {len(elements_by_contains)} elementos pela busca [class*='name']")
            
            if not elementos:
                print("Nenhum elemento com classe 'name' encontrado. Tentando analisar a estrutura da página...")
                # Salvar fonte da página para debug
                with open("page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("HTML atual salvo em 'page_source.html'")
                
                # Tentar encontrar por outros atributos comuns em listas de lojas
                alternative_elements = driver.find_elements(By.CSS_SELECTOR, 
                    "a[href*='loja'] span, a[href*='loja'] div, a[href*='tienda'] span, a[href*='tienda'] div, " +
                    "a[href*='brand'] span, a[href*='brand'] div, .brand, .store, .loja, .tienda")
                if alternative_elements:
                    elementos.extend(alternative_elements)
                    print(f"Encontrados {len(alternative_elements)} elementos alternativos")
            
            novos_elementos = []
            
            for elemento in elementos:
                try:
                    # Verificar se o elemento já foi processado
                    texto = elemento.text.strip()
                    
                    # Pular elementos vazios ou muito curtos
                    if not texto or len(texto) < 2:
                        continue
                    
                    # Tentar encontrar o link pai
                    link = ""
                    try:
                        # Tentar encontrar um link ancestral
                        link_element = elemento.find_element(By.XPATH, "./ancestor::a")
                        link = link_element.get_attribute("href")
                    except:
                        # Se não encontrar, tentar encontrar um link próximo
                        try:
                            link_element = driver.find_element(By.XPATH, f"//a[contains(., '{texto}')]")
                            link = link_element.get_attribute("href")
                        except:
                            pass
                    
                    # Verificar se já temos esse elemento (evitar duplicados)
                    if texto and not any(item["nome"] == texto for item in lojas):
                        info = {
                            "nome": texto,
                            "link": link
                        }
                        novos_elementos.append(info)
                except Exception as e:
                    print(f"Erro ao processar elemento: {str(e)}")
            
            return novos_elementos
        
        # Número máximo de rolagens para tentar
        max_rolagens = 2000  # Aumentado para 2000
        contador_rolagens = 0
        contador_sem_novos = 0  # Contador para tentativas sem novos elementos
        max_tentativas_sem_novos = 10  # Quantas tentativas sem novos elementos antes de desistir
        
        # Rolar a página várias vezes para carregar mais elementos
        print("Realizando scroll para carregar mais elementos...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Salvar a cada 50 scrolls como backup
        ultimo_salvamento = 0
        
        while contador_rolagens < max_rolagens:
            # Salvar estado atual dos elementos
            elementos_antes = len(lojas)
            
            # Técnica 1: Rolar até o final da página usando JavaScript (não precisa de mouse)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Técnica 2: Alternativa - rolagem suave em pequenos incrementos
            if contador_rolagens % 5 == 0:  # A cada 5 rolagens, usar método alternativo
                # Pegar altura visível da janela
                window_height = driver.execute_script("return window.innerHeight")
                # Rolar com incrementos de 1/3 da janela para simular rolagem mais natural
                for i in range(3):
                    driver.execute_script(f"window.scrollBy(0, {window_height/3});")
                    time.sleep(0.5)
            
            # Esperar um tempo aleatório para carregar novos elementos (simulando comportamento humano)
            time.sleep(random.uniform(3.0, 5.0))
            
            # Verificar se a página realmente rolou
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Tentar rolar de forma diferente se a altura não mudou
                scroll_amount = random.randint(500, 1000)
                # Técnica 3: Tentar scroll com diferentes métodos JavaScript
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(1)
                
                # Técnica 4: Tentar rolagem com elemento chave da página
                try:
                    # Identificar elementos na página
                    elementos_visiveis = driver.find_elements(By.CSS_SELECTOR, "div, section, article")
                    if elementos_visiveis:
                        # Escolher um elemento aleatório próximo do final da página visível
                        elemento_alvo = elementos_visiveis[min(len(elementos_visiveis)-1, int(len(elementos_visiveis)*0.8))]
                        # Rolar até o elemento usando JavaScript (sem precisar do mouse)
                        driver.execute_script("arguments[0].scrollIntoView();", elemento_alvo)
                        time.sleep(1)
                except Exception as e:
                    print(f"Erro ao tentar rolagem alternativa: {str(e)}")
                
                # Tentar clicar em botões "mostrar mais" se existirem
                try:
                    botoes_carregar_mais = driver.find_elements(By.CSS_SELECTOR, 
                                                          "button[class*='load'], a[class*='more'], button[class*='more'], .andes-pagination__button--next")
                    for botao in botoes_carregar_mais:
                        if botao.is_displayed() and botao.is_enabled():
                            try:
                                # Técnica 5: Clicar em botão usando JavaScript (não precisa de mouse)
                                driver.execute_script("arguments[0].click();", botao)
                                print("Clicou em botão 'carregar mais'")
                                time.sleep(3)
                                break
                            except:
                                pass
                except:
                    pass
            
            last_height = new_height
            
            # Atualizar contadores
            novos = extrair_elementos_name()
            elementos_novos_adicionados = 0
            
            for novo in novos:
                if not any(loja["nome"] == novo["nome"] for loja in lojas):
                    lojas.append(novo)
                    elementos_novos_adicionados += 1
                    print(f"Loja encontrada: {novo['nome']}")
            
            # Atualizar a variável global para o manipulador de sinal ter acesso aos dados atuais
            lojas_coletadas = lojas.copy()
            
            contador_rolagens += 1
            
            # Auto-salvamento a cada 50 scrolls como backup
            if contador_rolagens - ultimo_salvamento >= 1:
                print("\nRealizando auto-salvamento dos dados coletados até agora...")
                salvar_resultados(lojas)
                ultimo_salvamento = contador_rolagens
                print(f"Auto-salvamento concluído após {contador_rolagens} scrolls.")
            
            if elementos_novos_adicionados > 0:
                print(f"Scroll #{contador_rolagens} - Total: {len(lojas)} (+{elementos_novos_adicionados} novos)")
                contador_sem_novos = 0  # Resetar o contador se encontramos novos elementos
            else:
                contador_sem_novos += 1
                print(f"Scroll #{contador_rolagens} - Total: {len(lojas)} (Nenhum novo elemento - tentativa {contador_sem_novos}/{max_tentativas_sem_novos})")
                
                # Se várias tentativas sem encontrar novos elementos, podemos tentar mudar a estratégia
                if contador_sem_novos >= max_tentativas_sem_novos:
                    print("Muitas tentativas sem novos elementos. Tentando nova estratégia...")
                    # Tentar clicar em alguma paginação ou botão "carregar mais"
                    try:
                        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, ".andes-pagination__button")
                        load_more_buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='show-more'], a[class*='show-more']")
                        
                        if pagination_buttons:
                            for btn in pagination_buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    try:
                                        btn.click()
                                        print("Clicou em botão de paginação")
                                        time.sleep(5)
                                        contador_sem_novos = 0  # Resetar contador
                                        break
                                    except:
                                        pass
                        
                        elif load_more_buttons:
                            for btn in load_more_buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    try:
                                        btn.click()
                                        print("Clicou em botão 'mostrar mais'")
                                        time.sleep(5)
                                        contador_sem_novos = 0  # Resetar contador
                                        break
                                    except:
                                        pass
                        
                        # Se ainda não encontramos, podemos tentar rolar para outra posição
                        else:
                            random_scroll = random.randint(100, 500)
                            # Técnica 6: Rolagem para cima usando JavaScript
                            driver.execute_script(f"window.scrollBy(0, -{random_scroll});")
                            time.sleep(2)
                            contador_sem_novos = 5  # Reduzir contador, mas não zerar
                    except Exception as e:
                        print(f"Erro ao tentar nova estratégia: {str(e)}")
                        
                    # Se ainda não conseguimos novos elementos após várias tentativas, podemos considerar parar
                    if contador_sem_novos >= max_tentativas_sem_novos * 2:
                        print("Tentativas esgotadas. Parando o scraping.")
                        break
            
            # Pausa aleatória para evitar detecção
            if contador_rolagens % 10 == 0:
                pausa = random.uniform(2.0, 5.0)
                print(f"Pausa de {pausa:.1f} segundos para evitar detecção...")
                time.sleep(pausa)
        
        print(f"Processo de scraping concluído. Total de elementos encontrados: {len(lojas)}")
        
        return lojas
    
    except Exception as e:
        print(f"Erro durante o scraping: {str(e)}")
        traceback.print_exc()
        return lojas_coletadas  # Retorna o que foi coletado até o momento do erro
    
    finally:
        # Garantir que o driver seja fechado mesmo se ocorrer um erro
        if driver:
            print("Fechando o navegador...")
            driver.quit()

if __name__ == "__main__":
    # Registrar o manipulador de sinal para Ctrl+C
    signal.signal(signal.SIGINT, manipulador_interrupcao)
    
    # Registrar manipulador para SIGTERM (usado pelo sistema operacional para encerrar processos)
    signal.signal(signal.SIGTERM, manipulador_interrupcao)
    
    # Registrar função para ser executada na saída do programa (independente da causa)
    atexit.register(finalizar_programa)
    
    try:
        print("Iniciando scraper do Mercado Livre com Selenium...")
        print("* NOTA: Web scraping pode violar os Termos de Serviço do Mercado Livre *")
        print("* Use este script apenas para fins educacionais e de acordo com as políticas do site *")
        print("* Este script abrirá uma janela do navegador Chrome para realizar a extração *")
        print("* Para interromper a execução pressione Ctrl+C, os dados coletados até então serão salvos *")
        print("-" * 70)
        
        # Executar o scraper
        lojas = extrair_lojas_oficiais()
        
        # Atualizar a variável global com os resultados finais
        lojas_coletadas = lojas
        
        if lojas:
            print(f"\nTotal de lojas encontradas: {len(lojas)}")
            
            # Limpar resultados para remover duplicados
            lojas_unicas = []
            nomes_vistos = set()
            
            for loja in lojas:
                if loja['nome'] not in nomes_vistos:
                    lojas_unicas.append(loja)
                    nomes_vistos.add(loja['nome'])
            
            print(f"Total de lojas únicas após remoção de duplicados: {len(lojas_unicas)}")
            
            # Salva os resultados em um arquivo JSON
            with open("lojas_oficiais.json", "w", encoding="utf-8") as f:
                json.dump(lojas_unicas, f, ensure_ascii=False, indent=4)
            
            print("Resultados salvos em 'lojas_oficiais.json'")
            
            # Salvar também como CSV para fácil importação em planilhas
            try:
                import csv
                with open("lojas_oficiais.csv", "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Nome", "Link"])
                    for loja in lojas_unicas:
                        writer.writerow([loja["nome"], loja["link"]])
                print("Resultados também salvos em 'lojas_oficiais.csv'")
            except Exception as e:
                print(f"Erro ao salvar CSV: {str(e)}")
        else:
            print("Nenhuma loja oficial foi encontrada ou o site pode estar protegido contra web scraping.")
    
    except Exception as e:
        print(f"Erro não tratado: {str(e)}")
        traceback.print_exc()
        # Não é necessário chamar o finalizar_programa() aqui, pois o atexit já vai fazer isso
    
    # Novamente, não é necessário chamada explícita ao finalizar_programa() aqui