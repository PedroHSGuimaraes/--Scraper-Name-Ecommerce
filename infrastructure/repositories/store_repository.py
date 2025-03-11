# Importação das bibliotecas necessárias
# json: Para ler e escrever arquivos JSON
# os: Para operações com arquivos e diretórios
# logging: Para registrar informações e erros
import json
import os
import logging

class StoreRepository:
    """
    Classe responsável por gerenciar a persistência dos dados das lojas
    
    Esta classe implementa operações para:
    1. Carregar dados de lojas de arquivos JSON
    2. Salvar dados de lojas em arquivos JSON
    3. Gerenciar erros de leitura/escrita
    4. Registrar operações no log
    
    Utiliza codificação UTF-8 para suportar caracteres especiais
    e formatação JSON indentada para melhor legibilidade.
    """
    
    def __init__(self):
        """
        Inicializa o repositório de lojas
        
        Configura o logger específico para esta classe
        para registrar operações de leitura e escrita.
        """
        # Configuração do logger para esta classe
        self.logger = logging.getLogger(__name__)
    
    def load_stores(self, file_path):
        """
        Carrega dados de lojas de um arquivo JSON
        
        Este método:
        1. Verifica se o arquivo existe
        2. Lê e decodifica o conteúdo JSON
        3. Registra sucesso ou falha no log
        4. Trata diferentes tipos de erros
        
        Parâmetros:
            file_path (str): Caminho completo do arquivo JSON
            
        Retorna:
            list: Lista com os dados das lojas se sucesso
                 Lista vazia se houver qualquer erro
        """
        try:
            # Primeiro verifica se o arquivo existe
            # Evita tentar ler um arquivo inexistente
            if not os.path.exists(file_path):
                self.logger.error(f"Arquivo não encontrado: {file_path}")
                return []
            
            # Abre e lê o arquivo JSON com encoding UTF-8
            # para suportar caracteres especiais
            with open(file_path, 'r', encoding='utf-8') as f:
                stores_data = json.load(f)
                
            # Registra sucesso no log
            self.logger.info(f"Carregadas {len(stores_data)} lojas de {file_path}")
            return stores_data
            
        except json.JSONDecodeError:
            # Erro específico de formato JSON inválido
            self.logger.error(f"Erro ao decodificar JSON de {file_path}")
            return []
            
        except Exception as e:
            # Captura qualquer outro erro que possa ocorrer
            self.logger.error(f"Erro ao carregar lojas de {file_path}: {str(e)}")
            return []
    
    def save_stores(self, stores_data, file_path):
        """
        Salva dados de lojas em um arquivo JSON
        
        Este método:
        1. Cria o diretório de destino se necessário
        2. Salva os dados em formato JSON indentado
        3. Usa codificação UTF-8 para caracteres especiais
        4. Registra sucesso ou falha no log
        
        Parâmetros:
            stores_data (list): Lista com os dados das lojas
            file_path (str): Caminho onde salvar o arquivo
            
        Retorna:
            bool: True se os dados foram salvos com sucesso
                 False se ocorreu algum erro
        """
        try:
            # Cria toda a estrutura de diretórios necessária
            # exist_ok=True evita erro se o diretório já existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salva os dados em formato JSON
            # ensure_ascii=False: permite caracteres não-ASCII
            # indent=2: formata o JSON de forma legível
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stores_data, f, ensure_ascii=False, indent=2)
                
            # Registra sucesso no log
            self.logger.info(f"Dados de {len(stores_data)} lojas salvos em {file_path}")
            return True
            
        except Exception as e:
            # Registra qualquer erro que ocorra durante o salvamento
            self.logger.error(f"Erro ao salvar dados em {file_path}: {str(e)}")
            return False
