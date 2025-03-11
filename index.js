const fs = require("fs").promises;
const path = require("path");
const scraper = require("./scraper");
const {
  formatPhoneNumbers,
  organizeStoresByName,
  removeDuplicateStores,
} = require("./utils/dataProcessor");

async function main() {
  try {
    // Ler URLs de lojas a partir do arquivo
    const fileContent = await fs.readFile(
      path.join(__dirname, "store-urls.txt"),
      "utf8"
    );
    const storeUrls = fileContent
      .split("\n")
      .map((url) => url.trim())
      .filter((url) => url && url.length > 0);

    console.log(`Iniciando scraping de ${storeUrls.length} lojas...`);

    // Executar o scraper
    let scrapedStores = await scraper.scrapeStores(storeUrls);

    // Processar os dados para garantir a qualidade
    scrapedStores = scrapedStores.map((store) => {
      if (store.phones) {
        // Limitar a 5 números de telefone
        store.phones = formatPhoneNumbers(store.phones.slice(0, 5));
      }
      return store;
    });

    // Remover duplicados e organizar por nome
    const finalStores = organizeStoresByName(
      removeDuplicateStores(scrapedStores)
    );

    // Salvar os resultados
    await fs.writeFile(
      path.join(__dirname, "resultados.json"),
      JSON.stringify(finalStores, null, 2),
      "utf8"
    );

    console.log(`Scraping concluído! ${finalStores.length} lojas processadas.`);
    console.log("Resultados salvos em resultados.json");
  } catch (error) {
    console.error("Erro durante a execução do scraper:", error);
    process.exit(1);
  }
}

main();
