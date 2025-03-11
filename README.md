# --Scraper-Name-Ecommerce

## Sistema Integrado de Extração de Contatos

Este projeto implementa um sistema integrado em Python para extração de informações de contato de lojas a partir de consultas ao Google e análise das páginas de resultados.

### Funcionalidades

- Extração de nomes de lojas do arquivo existente (main.py ou JSON)
- Consulta automática no Google usando a API Google Custom Search
- Extração avançada de contatos de páginas HTML:
  - Endereços de e-mail
  - Números de telefone (formatos brasileiros)
  - Links de WhatsApp
  - Perfis de redes sociais (Facebook, Instagram, LinkedIn, Twitter, YouTube)
- Sistema de delay adaptativo para evitar bloqueios
- Exportação de resultados em vários formatos (JSON, CSV, HTML)
- Tratamento de erros e logging abrangente

### Arquivos do Projeto

- `scraper_integrado.py`: Aplicação principal que integra todos os componentes
- `contact_extractor.py`: Módulo com funções convertidas de JavaScript para extração de contatos
- `api_google.py`: Interface para a API de pesquisa do Google
- `main.py`: Contém a função de extração de nomes de lojas do Mercado Livre
- `requirements.txt`: Dependências do projeto

### Requisitos

```
requests>=2.25.1
pandas>=1.2.4
beautifulsoup4>=4.9.3
google-api-python-client>=2.0.2
selenium>=4.0.0
webdriver-manager>=3.5.2
```

### Instalação

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

### Uso

Execute o script principal:

```
python scraper_integrado.py
```

O sistema irá:
1. Carregar os nomes das lojas do arquivo JSON ou extrair usando main.py
2. Pesquisar cada loja no Google com termos relacionados a contato
3. Extrair informações das páginas de resultados
4. Gerar arquivos de saída na pasta "resultados":
   - JSON com todos os dados extraídos
   - CSV para fácil importação em planilhas
   - HTML com tabela formatada para visualização

### Parando a Execução

- Pressione `Ctrl+C` para interromper a execução e salvar resultados parciais
- Os resultados serão salvos automaticamente a cada 10 lojas processadas

### Observações

- O sistema implementa técnicas avançadas para validação de e-mails e números de telefone
- Utiliza delays adaptativos para evitar bloqueios por parte do Google
- Implementa tratamento avançado de erros para garantir continuidade mesmo em caso de falhas
