import json
import os
import logging

class StoreRepository:
    """Repositório para gerenciar dados de lojas."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_stores(self, file_path):
        """
        Carrega lojas de um arquivo JSON.
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            list: Lista de dados de lojas ou lista vazia em caso de falha
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                self.logger.error(f"Arquivo não encontrado: {file_path}")
                return []
            
            # Ler arquivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                stores_data = json.load(f)
                
            self.logger.info(f"Carregadas {len(stores_data)} lojas de {file_path}")
            return stores_data
            
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar JSON de {file_path}")
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar lojas de {file_path}: {str(e)}")
            return []
    
    def save_stores(self, stores_data, file_path):
        """
        Salva dados de lojas em um arquivo JSON.
        
        Args:
            stores_data (list): Dados das lojas para salvar
            file_path (str): Caminho do arquivo de destino
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        try:
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salvar como JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stores_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Dados de {len(stores_data)} lojas salvos em {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados em {file_path}: {str(e)}")
            return False
