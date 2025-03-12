/**
 * Utilitários para processamento dos dados do scraper
<<<<<<< HEAD
 * Este arquivo contém funções para manipular e organizar os dados coletados das lojas
 */

/**
 * Função para formatar e limpar números de telefone
 * Esta função recebe uma lista de telefones e retorna uma nova lista com os números formatados
 * 
 * @param {string[]} phones - Lista de números de telefone para formatar
 * @returns {string[]} - Lista de números de telefone formatados
 * 
 * Exemplos de formatação:
 * - "11999999999" vira "(11) 99999-9999"
 * - "1199999999" vira "(11) 9999-9999"
 */
function formatPhoneNumbers(phones) {
  return phones.map((phone) => {
    // Remove todos os caracteres que não são números ou o símbolo '+'
    // Por exemplo: "(11) 9999-9999" vira "11999999999"
    let cleanPhone = phone.replace(/[^\d+]/g, "");

    // Verifica se o número tem entre 10 e 13 dígitos (padrão brasileiro)
    // - 10 dígitos: telefone fixo (DDD + número)
    // - 11 dígitos: celular (DDD + 9 + número)
    // - 12/13 dígitos: formato internacional
    if (cleanPhone.length >= 10 && cleanPhone.length <= 13) {
      // Se tiver 11 dígitos, é um celular (formato: (XX) XXXXX-XXXX)
=======
 */

// Função para formatar e limpar números de telefone
function formatPhoneNumbers(phones) {
  return phones.map((phone) => {
    // Remover caracteres não numéricos
    let cleanPhone = phone.replace(/[^\d+]/g, "");

    // Verificar se tem formato brasileiro
    if (cleanPhone.length >= 10 && cleanPhone.length <= 13) {
      // Formatar como (XX) XXXXX-XXXX ou similar
>>>>>>> origin/main
      if (cleanPhone.length === 11) {
        return `(${cleanPhone.substring(0, 2)}) ${cleanPhone.substring(
          2,
          7
        )}-${cleanPhone.substring(7)}`;
<<<<<<< HEAD
      } 
      // Se tiver 10 dígitos, é um telefone fixo (formato: (XX) XXXX-XXXX)
      else if (cleanPhone.length === 10) {
=======
      } else if (cleanPhone.length === 10) {
>>>>>>> origin/main
        return `(${cleanPhone.substring(0, 2)}) ${cleanPhone.substring(
          2,
          6
        )}-${cleanPhone.substring(6)}`;
      }
    }
<<<<<<< HEAD
    // Se não se encaixar nos padrões acima, retorna o número apenas limpo
=======
>>>>>>> origin/main
    return cleanPhone;
  });
}

<<<<<<< HEAD
/**
 * Função para organizar lojas em ordem alfabética por nome
 * Usa a ordenação específica para o português brasileiro
 * 
 * @param {Object[]} stores - Lista de lojas para ordenar
 * @returns {Object[]} - Nova lista de lojas ordenada por nome
 * 
 * Cada loja deve ter um objeto com a propriedade 'name'
 * Exemplo de uso:
 * organizeStoresByName([
 *   { name: "Loja Z" },
 *   { name: "Loja A" }
 * ])
 * Retorna: [{ name: "Loja A" }, { name: "Loja Z" }]
 */
function organizeStoresByName(stores) {
  // Cria uma cópia do array original para não modificá-lo
  // Ordena as lojas usando localeCompare para considerar acentos do português
=======
// Organizar lojas por nome
function organizeStoresByName(stores) {
  // Ordenar lojas por nome
>>>>>>> origin/main
  const sortedStores = [...stores].sort((a, b) => {
    return a.name.localeCompare(b.name, "pt-BR");
  });

  return sortedStores;
}

<<<<<<< HEAD
/**
 * Função para remover lojas duplicadas baseado na URL
 * Uma loja é considerada duplicada se sua URL já existe na lista
 * 
 * @param {Object[]} stores - Lista de lojas para remover duplicatas
 * @returns {Object[]} - Nova lista de lojas sem duplicatas
 * 
 * Cada loja deve ter um objeto com a propriedade 'url'
 * Exemplo de uso:
 * removeDuplicateStores([
 *   { url: "loja1.com" },
 *   { url: "loja1.com" },
 *   { url: "loja2.com" }
 * ])
 * Retorna: [{ url: "loja1.com" }, { url: "loja2.com" }]
 */
function removeDuplicateStores(stores) {
  // Conjunto para armazenar URLs únicas já vistas
  const uniqueUrls = new Set();
  
  // Filtra as lojas, mantendo apenas aquelas com URLs únicas
  return stores.filter((store) => {
    // Se a URL já existe no conjunto, remove a loja (retorna false)
    if (uniqueUrls.has(store.url)) {
      return false;
    }
    // Se a URL é nova, adiciona ao conjunto e mantém a loja (retorna true)
=======
// Remover lojas duplicadas baseado na URL
function removeDuplicateStores(stores) {
  const uniqueUrls = new Set();
  return stores.filter((store) => {
    if (uniqueUrls.has(store.url)) {
      return false;
    }
>>>>>>> origin/main
    uniqueUrls.add(store.url);
    return true;
  });
}

<<<<<<< HEAD
// Exporta as funções para serem usadas em outros arquivos
=======
>>>>>>> origin/main
module.exports = {
  formatPhoneNumbers,
  organizeStoresByName,
  removeDuplicateStores,
};
