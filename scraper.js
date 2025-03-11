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

// ...existing code...
