/**
 * INDEX.JS - PONTO DE ENTRADA DO SCRAPER
 * 
 * Propósito Geral:
 * Este arquivo funciona como o "maestro" do sistema, coordenando:
 * 1. Leitura da lista de lojas a serem processadas (como uma agenda de tarefas)
 * 2. Execução do scraper para coletar dados de cada loja
 * 3. Limpeza e organização dos resultados (como filtrar e ordenar)
 * 4. Armazenamento dos dados finais em um arquivo JSON (como arquivar documentos)
 * 
 * Fluxo de Trabalho:
 * [Arquivo de URLs] → [Scraper] → [Processamento] → [Arquivo de Resultados]
 * 
 * Bibliotecas Externas:
 * - fs: Para leitura/escrita de arquivos (sistema de arquivos do Node.js)
 * - path: Para manipulação de caminhos de arquivos
 * - scraper: Módulo personalizado para extrair dados
 * - dataProcessor: Utilitário para formatar e organizar os dados coletados
 */

const fs = require("fs").promises;
const path = require("path");
const scraper = require("./scraper");
const {
  formatPhoneNumbers,
  organizeStoresByName,
  removeDuplicateStores,
} = require("./utils/dataProcessor");

/**
 * Função Principal - Coordenador do Processo
 * 
 * Analogia: Funciona como um gerente de projeto que:
 * - Define as tarefas a serem executadas
 * - Distribui o trabalho para equipes especializadas (módulos)
 * - Supervisiona a qualidade dos resultados
 * - Entrega o produto final no formato correto
 */
async function main() {
  try {
    // ETAPA 1: LEITURA DA LISTA DE LOJAS
    /**
     * Lê o arquivo com URLs de lojas e prepara a lista para processamento
     * - Abre o arquivo de texto usando o caminho completo (independente do SO)
     * - Divide o conteúdo em linhas separadas
     * - Remove espaços extras no início/fim de cada URL
     * - Filtra linhas vazias ou inválidas
     */
    const fileContent = await fs.readFile(
      path.join(__dirname, "store-urls.txt"),
      "utf8"
    );
    const storeUrls = fileContent
      .split("\n")
      .map((url) => url.trim())
      .filter((url) => url && url.length > 0);

    console.log(`Iniciando scraping de ${storeUrls.length} lojas...`);

    // ETAPA 2: COLETA DE DADOS
    /**
     * Executa o scraper para cada URL na lista
     * - Passa a lista completa para o módulo scraper
     * - O módulo retorna os dados brutos de todas as lojas
     */
    let scrapedStores = await scraper.scrapeStores(storeUrls);

    // ETAPA 3: PROCESSAMENTO E LIMPEZA DOS DADOS
    /**
     * Formata e limita os números de telefone para cada loja
     * - Para cada loja encontrada:
     *   - Verifica se existem telefones
     *   - Limita a quantidade para evitar dados incorretos (máximo 5)
     *   - Formata os números para um padrão consistente
     */
    scrapedStores = scrapedStores.map((store) => {
      if (store.phones) {
        // Limitar a 5 números de telefone
        store.phones = formatPhoneNumbers(store.phones.slice(0, 5));
      }
      return store;
    });

    // ETAPA 4: ORGANIZAÇÃO FINAL
    /**
     * Aplica filtros de qualidade e organização aos dados
     * - Remove lojas duplicadas (como tirar cópias repetidas)
     * - Organiza a lista por nome da loja (ordem alfabética)
     */
    const finalStores = organizeStoresByName(
      removeDuplicateStores(scrapedStores)
    );

    // ETAPA 5: SALVAMENTO DOS RESULTADOS
    /**
     * Salva os dados processados em um arquivo JSON
     * - Gera o caminho completo para o arquivo de saída
     * - Converte os dados para formato JSON com indentação
     * - Salva no disco com codificação UTF-8 (para acentos)
     */
    await fs.writeFile(
      path.join(__dirname, "resultados.json"),
      JSON.stringify(finalStores, null, 2),
      "utf8"
    );

    console.log(`Scraping concluído! ${finalStores.length} lojas processadas.`);
    console.log("Resultados salvos em resultados.json");
  } catch (error) {
    /**
     * Tratamento de erros
     * - Captura qualquer problema durante o processo
     * - Exibe mensagem detalhada no console
     * - Encerra o programa com código de erro (1)
     */
    console.error("Erro durante a execução do scraper:", error);
    process.exit(1);
  }
}

// Inicia a execução do programa chamando a função principal
main();
