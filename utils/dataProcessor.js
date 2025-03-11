/**
 * DATAPROCESSOR.JS - PROCESSADOR DE DADOS DO SCRAPER
 * 
 * Propósito Geral:
 * Este arquivo funciona como um "filtro de qualidade" para os dados coletados pelo scraper:
 * 1. Formata números de telefone em padrões consistentes (como padronizar documentos)
 * 2. Organiza as lojas em ordem alfabética (como um índice de diretório)
 * 3. Remove lojas duplicadas (como eliminar cópias desnecessárias)
 * 
 * Fluxo de Trabalho:
 * [Dados Brutos do Scraper] → [Limpeza e Formatação] → [Organização] → [Dados Processados]
 * 
 * Importância:
 * Garante que os dados coletados estejam limpos, organizados e sem duplicações
 * antes de serem utilizados ou armazenados permanentemente.
 */

/**
 * FORMATADOR DE NÚMEROS DE TELEFONE
 * 
 * Propósito:
 * Padroniza os formatos de números de telefone para facilitar visualização e uso
 * 
 * Analogia:
 * Como um revisor que reescreve diferentes formatos de números para um padrão único
 * (ex: transformar "11 98765-4321", "11987654321" e "(11)98765.4321" todos em "(11) 98765-4321")
 * 
 * Parâmetros:
 * - phones: Lista de números de telefone em formatos variados
 * 
 * Processo:
 * 1. Para cada número na lista:
 *    a. Remove caracteres não numéricos (como parênteses, traços, pontos)
 *    b. Verifica se o formato é compatível com números brasileiros (10-13 dígitos)
 *    c. Aplica formatação específica para celulares (11 dígitos) ou fixos (10 dígitos)
 *    d. Mantém o formato original para números que não seguem padrão brasileiro
 * 
 * Retorno:
 * Lista de números formatados consistentemente
 */
function formatPhoneNumbers(phones) {
  return phones.map((phone) => {
    // Remover caracteres não numéricos
    let cleanPhone = phone.replace(/[^\d+]/g, "");

    // Verificar se tem formato brasileiro
    if (cleanPhone.length >= 10 && cleanPhone.length <= 13) {
      // Formatar como (XX) XXXXX-XXXX ou similar
      if (cleanPhone.length === 11) {
        return `(${cleanPhone.substring(0, 2)}) ${cleanPhone.substring(
          2,
          7
        )}-${cleanPhone.substring(7)}`;
      } else if (cleanPhone.length === 10) {
        return `(${cleanPhone.substring(0, 2)}) ${cleanPhone.substring(
          2,
          6
        )}-${cleanPhone.substring(6)}`;
      }
    }
    return cleanPhone;
  });
}

/**
 * ORGANIZADOR DE LOJAS POR NOME
 * 
 * Propósito:
 * Organiza a lista de lojas em ordem alfabética pelo nome
 * 
 * Analogia:
 * Como organizar um catálogo telefônico onde as empresas aparecem em ordem alfabética
 * 
 * Parâmetros:
 * - stores: Lista de objetos contendo informações das lojas
 * 
 * Processo:
 * 1. Cria uma cópia da lista original para não modificá-la diretamente
 * 2. Ordena a lista usando o método de comparação específico para português brasileiro
 *    (isso garante que acentos e caracteres especiais sejam tratados corretamente)
 * 
 * Retorno:
 * Nova lista ordenada alfabeticamente pelo nome das lojas
 */
function organizeStoresByName(stores) {
  // Ordenar lojas por nome
  const sortedStores = [...stores].sort((a, b) => {
    return a.name.localeCompare(b.name, "pt-BR");
  });

  return sortedStores;
}

/**
 * REMOVEDOR DE LOJAS DUPLICADAS
 * 
 * Propósito:
 * Elimina entradas repetidas da mesma loja baseado na URL
 * 
 * Analogia:
 * Como um fiscal que verifica um lote de produtos e remove itens duplicados
 * 
 * Parâmetros:
 * - stores: Lista de objetos contendo informações das lojas
 * 
 * Processo:
 * 1. Cria um conjunto (Set) para rastrear URLs já vistas
 * 2. Filtra a lista, mantendo apenas a primeira ocorrência de cada URL
 *    a. Se a URL já existe no conjunto, descarta o item (retorna false)
 *    b. Se a URL é nova, adiciona ao conjunto e mantém o item (retorna true)
 * 
 * Retorno:
 * Lista de lojas sem duplicações
 */
function removeDuplicateStores(stores) {
  const uniqueUrls = new Set();
  return stores.filter((store) => {
    if (uniqueUrls.has(store.url)) {
      return false;
    }
    uniqueUrls.add(store.url);
    return true;
  });
}

/**
 * Exportação do módulo
 * Disponibiliza as funções para uso em outros arquivos do projeto
 */
module.exports = {
  formatPhoneNumbers,
  organizeStoresByName,
  removeDuplicateStores,
};
