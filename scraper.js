<<<<<<< HEAD
/**
 * Scraper para E-commerce
 * Este arquivo contém as funções principais para extrair informações das lojas
 * usando o Puppeteer para automatizar a navegação web
 */

const puppeteer = require('puppeteer');

/**
 * Função para extrair números de telefone de uma página
 * Limita a extração a no máximo 5 números por loja
 * 
 * @param {Page} page - Objeto Page do Puppeteer representando a página web
 * @returns {string[]} - Lista com até 5 números de telefone encontrados
 * 
 * Como funciona:
 * 1. Busca no conteúdo da página usando expressão regular
 * 2. Captura números nos formatos:
 *    - (XX) XXXXX-XXXX (celular)
 *    - (XX) XXXX-XXXX (fixo)
 *    - +XX(XX)XXXXX-XXXX (internacional)
 * 3. Limita a 5 números para evitar falsos positivos
 */
async function extractPhoneNumbers(page) {
  try {
    // Executa o código dentro do contexto da página
    const phoneNumbers = await page.evaluate(() => {
      // Array para armazenar os números encontrados
      const phones = [];
      
      // Pega todo o texto visível da página
      const content = document.body.innerText;
      
      // Expressão regular para encontrar números de telefone
      // Aceita vários formatos como:
      // - +55 (11) 99999-9999
      // - (11) 99999-9999
      // - 11999999999
      const phoneRegex =
        /(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}/g;
      
      // Procura por todos os números que correspondem ao padrão
      let match;
=======
// ...existing code...

// Função para extrair números de telefone limitando a 5
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

>>>>>>> origin/main
      while ((match = phoneRegex.exec(content)) !== null && phones.length < 5) {
        phones.push(match[0]);
      }

      return phones;
    });

<<<<<<< HEAD
    // Garante que não ultrapassamos o limite de 5 números
    // mesmo que mais tenham sido encontrados
=======
    // Garantir que retornamos no máximo 5 números
>>>>>>> origin/main
    return phoneNumbers.slice(0, 5);
  } catch (error) {
    console.error("Erro ao extrair números de telefone:", error);
    return [];
  }
}

<<<<<<< HEAD
/**
 * Função principal que coordena a extração de dados das lojas
 * Processa cada URL fornecida e extrai as informações relevantes
 * 
 * @param {string[]} storeUrls - Lista de URLs das lojas para processar
 * @returns {Object[]} - Lista de objetos com os dados extraídos de cada loja
 * 
 * Cada objeto retornado tem o formato:
 * {
 *   name: "Nome da Loja",
 *   url: "https://loja.com",
 *   phones: ["(11) 99999-9999", ...],
 *   extractedAt: "2025-03-12T23:23:01.000Z"
 * }
 */
async function scrapeStores(storeUrls) {
  // Array para armazenar os resultados de todas as lojas
  const results = [];

  // Processa cada URL da lista
  for (const [index, url] of storeUrls.entries()) {
    try {
      // Mostra progresso do processamento
      console.log(`Processando loja ${index + 1}/${storeUrls.length}: ${url}`);
      
      // Inicia o navegador em modo headless (sem interface gráfica)
      const browser = await puppeteer.launch({ headless: true });
      
      // Cria uma nova página/aba no navegador
      const page = await browser.newPage();
      
      // Navega até a URL da loja
      // - waitUntil: espera a página carregar completamente
      // - timeout: cancela se demorar mais de 60 segundos
      await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });

      // Tenta extrair o nome da loja procurando por elementos HTML específicos
      // que geralmente contêm essa informação
      const storeName = await page.evaluate(() => {
        const nameElement =
          document.querySelector("h1.store-name") ||          // Tenta primeiro essa classe
          document.querySelector(".store-header h1") ||       // Depois essa
          document.querySelector(".seller-info h1");          // Por último essa
        return nameElement ? nameElement.innerText.trim() : "Loja Desconhecida";
      });

      // Extrai os números de telefone da página
      const phoneNumbers = await extractPhoneNumbers(page);

      // Adiciona as informações coletadas ao array de resultados
=======
// Função principal do scraper organizada por nome da loja
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
>>>>>>> origin/main
      results.push({
        name: storeName,
        url: url,
        phones: phoneNumbers,
<<<<<<< HEAD
        extractedAt: new Date().toISOString(),  // Marca data/hora da extração
      });

      // Fecha o navegador para liberar memória
      await browser.close();
    } catch (error) {
      // Se houver algum erro, registra no console e adiciona aos resultados
=======
        extractedAt: new Date().toISOString(),
      });

      await browser.close();
    } catch (error) {
>>>>>>> origin/main
      console.error(`Erro ao processar a URL ${url}:`, error);
      results.push({
        url: url,
        error: error.message,
        extractedAt: new Date().toISOString(),
      });
    }
  }

<<<<<<< HEAD
  // Ordena os resultados pelo nome da loja em ordem alfabética
  // Se alguma loja não tiver nome, mantém na mesma posição
=======
  // Ordenar resultados por nome da loja
>>>>>>> origin/main
  return results.sort((a, b) => {
    if (a.name && b.name) {
      return a.name.localeCompare(b.name);
    }
    return 0;
  });
}
<<<<<<< HEAD
=======

// ...existing code...
>>>>>>> origin/main
