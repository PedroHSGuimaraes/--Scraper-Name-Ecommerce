import os
import json
import logging

class Settings:
    """Configurações da aplicação."""
    
    def __init__(self, config_path=None):
        # Configurações padrão
        self.default_config = {
            # Configurações gerais
            "default_input_file": "lojas_oficiais_emergencia.json",
            "output_directory": "resultados",
            
            # Configurações de API
            "google_api": {
                "api_key": "AIzaSyDkwgWLJ_NISwA6Nk-4X0__e68jRK7eyLw",
                "engine_id": "47366a2537ee841e9"
            },
            
            # Configurações de scraping
            "scraping": {
                "max_retries": 3,
                "base_delay": 5,
                "timeout": 30
            }
        }
        
        # Carregar configurações do arquivo, se existir
        self.config = self.default_config.copy()
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
    
    def _load_from_file(self, config_path):
        """Carrega configurações de um arquivo JSON."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            
            # Mesclar com configurações padrão
            self._merge_configs(self.config, custom_config)
            logging.info(f"Configurações carregadas de {config_path}")
        except Exception as e:
            logging.error(f"Erro ao carregar configurações: {str(e)}")
    
    def _merge_configs(self, base, custom):
        """Mescla recursivamente duas estruturas de configuração."""
        for key, value in custom.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """
        Obtém um valor de configuração por chave.
        
        Args:
            key (str): Chave da configuração
            default: Valor padrão se a chave não existir
            
        Returns:
            O valor da configuração ou o valor padrão
        """
        # Suportar acesso por caminho (ex: "google_api.api_key")
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            for part in parts:
                if part not in current:
                    return default
                current = current[part]
            
            return current
        
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Define um valor de configuração.
        
        Args:
            key (str): Chave da configuração
            value: Novo valor
        """
        # Suportar acesso por caminho (ex: "google_api.api_key")
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        else:
            self.config[key] = value
