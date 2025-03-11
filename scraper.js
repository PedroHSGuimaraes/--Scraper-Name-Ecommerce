/**
 * SCRAPER.JS - COLETADOR DE DADOS DE LOJAS
 * 
 * Propósito Geral:
 * Este arquivo funciona como um "robô navegador" especializado que:
 * 1. Visita páginas web de lojas automaticamente (como um cliente virtual)
 * 2. Extrai informações importantes como nome da loja e telefones de contato
 * 3. Processa os dados encontrados em um formato consistente
 * 4. Organiza os resultados em ordem alfabética por nome da loja
 * 
 * Fluxo de Trabalho:
 * [Lista de URLs] → [Navegação das Páginas] → [Extração de Dados] → [Resultados Organizados]
 * 
 * Bibliotecas Externas:
 * - puppeteer: Para navegação automatizada em páginas web (controla navegador headless)
 */

const puppeteer = require('puppeteer'); // Biblioteca para controlar navegador automatizado

/**
 * EXTRATOR DE TELEFONES
 * 
 * Propósito:
 * Encontra números de telefone na página web atual
 * 
 * Analogia: 
 * Como um detetive com lupa que procura apenas números de telefone em uma página
 * 
 * Parâmetros:
 * - page: Página web atual aberta pelo Puppeteer (como uma janela de navegador)
 * 
 * Processo:
 * 1. Execute código JavaScript dentro da própria página web
 * 2. Busque padrões de telefone no texto da página usando expressão regular
 * 3. Colete até 5 números de telefone para evitar falsos positivos
 * 4. Aplique limitação adicional no final (segurança dupla)
 * 
 * Tratamento de erros:
 * - Captura qualquer problema durante a extração
 * - Retorna lista vazia em caso de falha
 */
async function extractPhoneNumbers(page) {
  try {
    const phoneNumbers = await page.evaluate(() => {
      // Lógica para encontrar números de telefone na página
      const phones = [];
      // Busca por padrões de telefone na página
      const content = document.body.innerText;
      const phoneRegex =
        /(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}/g;
      let match;

      while ((match = phoneRegex.exec(content)) !== null && phones.length < 5) {
        phones.push(match[0]);
      }

      return phones;
    });

    // Garantir que retornamos no máximo 5 números
    return phoneNumbers.slice(0, 5);
  } catch (error) {
    console.error("Erro ao extrair números de telefone:", error);
    return [];
  }
}

/**
 * FUNÇÃO PRINCIPAL - NAVEGADOR E COLETOR
 * 
 * Propósito:
 * Processa uma lista de URLs para extrair dados das lojas
 * 
 * Analogia:
 * Como um pesquisador que visita várias lojas, coletando informações 
 * em uma prancheta e organizando tudo em ordem alfabética ao final
 * 
 * Parâmetros:
 * - storeUrls: Lista de endereços web para processar
 * 
 * Processo passo a passo:
 * 1. Para cada URL na lista:
 *    a. Inicia um navegador invisível (headless)
 *    b. Navega até a página da loja
 *    c. Espera o carregamento completo (60 segundos máximo)
 *    d. Busca o nome da loja usando diferentes seletores HTML
 *    e. Extrai números de telefone usando função especializada
 *    f. Registra os dados com data/hora da extração
 *    g. Fecha o navegador para liberar memória
 * 2. Ao final, organiza todos os resultados por nome da loja
 * 
 * Tratamento de erros:
 * - Captura falhas individuais em cada URL
 * - Registra o erro no console
 * - Continua processando as demais URLs da lista
 * - Inclui informação de erro nos resultados para rastreamento
 */
async function scrapeStores(storeUrls) {
  const results = [];

  for (const [index, url] of storeUrls.entries()) {
    try {
      console.log(`Processando loja ${index + 1}/${storeUrls.length}: ${url}`);
      const browser = await puppeteer.launch({ headless: true });
      const page = await browser.newPage();
      await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });

      // Extrair nome da loja
      const storeName = await page.evaluate(() => {
        const nameElement =
          document.querySelector("h1.store-name") ||
          document.querySelector(".store-header h1") ||
          document.querySelector(".seller-info h1");
        return nameElement ? nameElement.innerText.trim() : "Loja Desconhecida";
      });

      // Extrair até 5 números de telefone
      const phoneNumbers = await extractPhoneNumbers(page);

      // Adicionar dados da loja aos resultados
      results.push({
        name: storeName,
        url: url,
        phones: phoneNumbers,
        extractedAt: new Date().toISOString(),
      });

      await browser.close();
    } catch (error) {
      console.error(`Erro ao processar a URL ${url}:`, error);
      results.push({
        url: url,
        error: error.message,
        extractedAt: new Date().toISOString(),
      });
    }
  }

  // Ordenar resultados por nome da loja
  return results.sort((a, b) => {
    if (a.name && b.name) {
      return a.name.localeCompare(b.name);
    }
    return 0;
  });
}

/**
 * Exportação do módulo
 * Torna a função scrapeStores disponível para outros arquivos
 */
module.exports = {
  scrapeStores,
};
