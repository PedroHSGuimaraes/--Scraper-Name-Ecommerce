/**
 * Utilitários para processamento dos dados do scraper
 */

// Função para formatar e limpar números de telefone
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

// Organizar lojas por nome
function organizeStoresByName(stores) {
  // Ordenar lojas por nome
  const sortedStores = [...stores].sort((a, b) => {
    return a.name.localeCompare(b.name, "pt-BR");
  });

  return sortedStores;
}

// Remover lojas duplicadas baseado na URL
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

module.exports = {
  formatPhoneNumbers,
  organizeStoresByName,
  removeDuplicateStores,
};
