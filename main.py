import time
import json
import random
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extrair_lojas_oficiais():
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
        max_rolagens = 1000
        contador_rolagens = 0
        
        # Rolar a página várias vezes para carregar mais elementos
        print("Realizando scroll para carregar mais elementos...")
        while contador_rolagens < max_rolagens:
            # Salvar estado atual dos elementos
            elementos_antes = len(lojas)
            
            # Rolar até o final da página
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Esperar explicitamente por novos elementos
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: len(extrair_elementos_name()) > elementos_antes
                )
            except:
                print("Nenhum novo elemento carregado após scroll")
                break
            
            # Atualizar contadores
            novos = extrair_elementos_name()
            for novo in novos:
                if not any(loja["nome"] == novo["nome"] for loja in lojas):
                    lojas.append(novo)
                    print(f"Loja encontrada: {novo['nome']}")
            
            contador_rolagens += 1
            print(f"Scroll #{contador_rolagens} - Total: {len(lojas)}")
            time.sleep(2)
        
        print(f"Processo de scraping concluído. Total de elementos encontrados: {len(lojas)}")
        
        return lojas
    
    except Exception as e:
        print(f"Erro durante o scraping: {str(e)}")
        return []
    
    finally:
        # Garantir que o driver seja fechado mesmo se ocorrer um erro
        if 'driver' in locals():
            print("Fechando o navegador...")
            driver.quit()

if __name__ == "__main__":
    print("Iniciando scraper do Mercado Livre com Selenium...")
    print("* NOTA: Web scraping pode violar os Termos de Serviço do Mercado Livre *")
    print("* Use este script apenas para fins educacionais e de acordo com as políticas do site *")
    print("* Este script abrirá uma janela do navegador Chrome para realizar a extração *")
    print("-" * 70)
    
    lojas = extrair_lojas_oficiais()
    
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
    else:
        print("Nenhuma loja oficial foi encontrada ou o site pode estar protegido contra web scraping.")